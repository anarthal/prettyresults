import pandas as pd
import numpy as np
import webbrowser
from pandas.api.types import CategoricalDtype
from os import path
import os
import shutil

from .results import ResultManager
from .utils import VarType
from .word import WordGenerator

class AnalysisContext(object):
    '''
    Class representing an analysis.
    An analysis has associated the following data:

    - Variable metadata: information about the involved variables. Used in load_data.
    - Results: accumulates any result produced in the analysis.
    - Result directory: the AnalysisContext remembers where to
      write directories to and where to read them from.
    '''
    def __init__(self, variables, container_results, results_directory, case_id_fun):
        '''
        Initializes the analysis context with the variable metadata given in
        variables. result_directory should be a path where the results will get written.
        If result_directory does not already exist, it will be created. If it already
        exists, any existing result will be loaded.
        container_results specifies a list of container results to be created. This is
        a shortcut to create container results beforehand. container_result must be a list
        of 3 element tuples. Element 0 is the container ID, element 1 is the container
        display name, and element 2 is a list of child containers to be created, with the
        same described format (so the structure can be arbitrarily nested).
        case_id_fun must be a callable taking a single Pandas dataframe row argument
        and returning a string. It should return a human-readable identifier for the given row.
        '''
        self._results_directory = results_directory
        os.makedirs(results_directory, exist_ok=True)
        self.case_id_fun = case_id_fun
        self._variables = variables
        self._result_manager = ResultManager(results_directory, container_results)
        self._warnings_result = self._result_manager['root'].add_table(
            'warnings', 'Warnings', headings=['Caso', ''], rows=[])
        
    def load_data(self, fname, na_values=[' ']):
        '''Loads data from the CSV file identified by fname and pre-processes it.

        The variable names to load are taken from the variable metadata passed to the constructor.
        Only variables without a 'computation' key in their dict will be loaded.
        na_values will be forwarded to pandas.read_csv.
        After loading, data will be pre-processed:
        
            - Derived variables (those defining a 'computation' key in their dict) will be computed.
            - A copy of the original values will be stored in the dataframe, under the name
              $NAME_ORIGINAL, being $NAME the original variable name.
            - Type transformations will be applied.
            - Mandatory checks will be performed. Any row with a NaN value in any mandatory
              variable will be dropped.
        
        Loading data may add warnings to the context.

        Args:
            fname (str): path to the CSV file to load.
            na_values (list of str): values to be considered as NaN
        Returns:
            Dataframe with the loaded data.
        '''
        csv_varnames = [varname for varname, var in self._variables.items() if 'computation' not in var]
        df = pd.read_csv(fname, usecols=csv_varnames, na_values=na_values)
        self._preprocess(df)
        return df
    
    def get_result(self, result_id):
        '''Returns a result object identified by result_id. Raises KeyError if not found.
        
        Args:
            result_id (str): fully-qualified ID of the result to be retrieved.
        Returns:
            Result object.
        '''
        return self._result_manager[result_id]
    
    def dump_results(self):
        '''Writes results to the result directory.'''
        self._result_manager.dump()
            
    def generate_web(self, open_browser=True):
        '''Generates the web page.
        
        Creates a subdirectory named "web" under the results directory, and copies
        all relevant files to this directory. Open web/index.html to access the web.
        
        The will contain every result known to the analysis context, including
        any from previous runs.
        
        Args:
            open_browser (bool): if True, the resulting page will be open in a new web browser tab. 
        '''
        # Create the directory
        project_dir = path.dirname(path.realpath(__file__))
        web_directory = path.join(self._results_directory, 'web')
        shutil.rmtree(web_directory, ignore_errors=True)
        shutil.copytree(path.join(project_dir, 'web'), web_directory)
        os.makedirs(web_directory, exist_ok=True)
        
        # Generate data.js
        results_data = b'var ANALYSIS_RESULTS = '
        with open(self._result_manager.json_path, 'rb') as f:
            results_data += f.read()
        with open(path.join(web_directory, 'data.js'), 'wb') as f:
            f.write(results_data)
        
        # Open the browser
        if open_browser:
            webbrowser.open('file:///{}/index.html'.format(web_directory), new=2)
            
    def generate_word(self, output_file, result_ids=None):
        '''Generates a Microsoft Word (.docx) file with the results known to the analysis context.

        Args:
            output_file (str): path to the Word file to be generated, normally with a .docx extension.
                The directory part of the path should already exist.
            result_ids (list of str): a list of fully qualified result IDs to be included in the output document.
                If the specified results have children, these will be recursively be included, too.
                If set to None, all results will be included.
        '''
        
        WordGenerator(self._result_manager.results,
                      self._results_directory).generate(output_file, result_ids)
            
    def add_warning(self, case_id, text):
        '''Logs a warning.
        
        In this context, a warning has an identifier and a text. The identifier should help
        locate which data triggered the warning.
        Warnings will be included as a TableResult with ID root.warnings.
        
        Args:
            case_id (str or pandas.Series): if str, should identify the data that triggered the warning.
                If pd.Series, an string identifier will be generated by
                invoking the case_id_fun provided to the constructor.

            text (str): Warning text.
        '''
        if isinstance(case_id, pd.Series):
            case_id = self.case_id_fun(case_id)
        self._warnings_result.add_row((case_id, text))
        
    # Helpers for load_data
    def _drop_na(self, df, varname):
        lost_cases = df[df[varname].isna()]
        if len(lost_cases) != 0:
            for _, row in lost_cases.iterrows():
                self.add_warning(row, '{} perdida'.format(varname))
            df.dropna(subset=[varname], inplace=True)
            
    def _compute_derived(self, df):
        for varname, var in self._variables.items():
            fun = var.get('computation')
            if fun is not None:
                df[varname] = fun(df, self)
                
    def _preprocess(self, df):
        self._compute_derived(df)
        for varname in df:
            vardata = self._variables[varname]
            vartype = vardata['type']
            
            # Store the original value
            df[varname + '_ORIGINAL'] = df[varname]
    
            # Convert to adequate type
            if vartype == VarType.Category:
                cat_type = CategoricalDtype(categories=vardata['labels'].keys())
                cat_map = { key: value[0] for key, value in vardata['labels'].items() }
                df.loc[:, varname] = df[varname].astype(cat_type)
                df[varname].cat.rename_categories(cat_map, inplace=True)
            elif vartype == VarType.Bool:
                df.loc[~df[varname].isin((0, 1)), [varname]] = np.nan
                
            # Mandatory checking
            if vardata.get('mandatory', False):
                self._drop_na(df, varname)
                # Further conversion can be done if no NaN is present
                if vartype == VarType.Int:
                    df[varname] = df[varname].astype(np.int64)
