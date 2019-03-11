import pandas as pd
from pandas.api.types import CategoricalDtype
import numpy as np

from .utils import VarType

class DataLoader(object):
    def __init__(self, variables, case_id_fun):
        self.variables = variables
        self.case_id_fun = case_id_fun
        self._warnings = []
        
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
        self._warnings.append((case_id, text))
        
    def load_data(self, fname, ctx, na_values=[' ']):
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
        csv_varnames = [varname for varname, var in self.variables.items() if 'computation' not in var]
        df = pd.read_csv(fname, usecols=csv_varnames, na_values=na_values)
        self._preprocess(df)
        ctx.get_result('root').add_table('warnings', 'Warnings',
                                         headings=['Caso', ''], rows=self._warnings)
            
        return df
        
    def _drop_na(self, df, varname):
        lost_cases = df[df[varname].isna()]
        if len(lost_cases) != 0:
            for _, row in lost_cases.iterrows():
                self.add_warning(row, '{} perdida'.format(varname))
            df.dropna(subset=[varname], inplace=True)
            
    def _compute_derived(self, df):
        for varname, var in self.variables.items():
            fun = var.get('computation')
            if fun is not None:
                df[varname] = fun(df, self)
                
    def _preprocess(self, df):
        self._compute_derived(df)
        for varname in df:
            vardata = self.variables[varname]
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
                    
