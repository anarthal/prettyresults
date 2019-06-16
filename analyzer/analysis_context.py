import webbrowser
from os import path
import os
import shutil
import tempfile

from .results import ResultManager
from .word import WordGenerator

class AnalysisContext(object):
    '''
    Class that accumulates the results of an analysis.
    
    An analysis context has a result directory, a temporary directory where result files
    will be written to; and keeps track of the generated results. It provides methods to access
    and add results, and to write them in different formats.
    '''
    def __init__(self, results_directory=None, container_results=[]):
        '''
        Initializes the analysis context. The context will contain the root result
        (a container with ID 'root'), at least.
        
        Args:
            results_directory (str or None): Path to the directory where result files will be written to.
                Several files (result data, images...) will be written to the directory.
                If the directory does not already exist, it will be created. If the directory
                contains result files from previous runs, they will be loaded and added,
                as if they had been created in the current run.
                If it's None, a temporary directory will be created for result files, which will be removed
                when the AnalysisContext object is destroyed.
            container_results (list of tuples): Specifies a list of container results to be created. This is
                a shortcut to create container results beforehand. container_result must be a list
                of 3 element tuples. Element 0 is the container ID, element 1 is the container
                display name, and element 2 is a list of child containers to be created, with the
                same described format (so the structure can be arbitrarily nested).
        '''
        if results_directory is None:
            self._temp_dir = tempfile.TemporaryDirectory()
            results_directory = self._temp_dir.name
        else:
            os.makedirs(results_directory, exist_ok=True)
        self._results_directory = results_directory
        self._result_manager = ResultManager(results_directory, container_results)

    def get_result(self, result_id):
        '''Returns a result object identified by result_id. Raises KeyError if not found.
        
        Args:
            result_id (str): Fully-qualified ID of the result to be retrieved.
        Returns:
            Result object.
        '''
        return self._result_manager[result_id]
    
    def dump_results(self):
        '''Writes results to the result directory.'''
        self._result_manager.dump()
            
    def generate_web(self, web_directory, *, open_browser=False, overwrite=False):
        '''Generates the web page.
        
        The webpage will be created under web_directory and will contain every result
        known to the analysis context. Open index.html to view the web.
        The web is completely stand-alone: you can copy the web directory to another location
        or machine and will still display correctly.
        
        If web_directory already exists and overwrite is True,
        the directory will be RECURSIVELY REMOVED. If remove_if_exists is False and the
        directory exists, an exception of type FileExistsError will be raised.
        
        Args:
            web_directory (str): Path where the web page will be placed under.
            open_browser (bool): If True, the resulting page will be open in a new web browser tab.
            overwrite (bool): If True, the directory will be removed if already exists.
        '''
        # Create the directory
        if not overwrite and path.exists(web_directory):
            raise FileExistsError('Web directory {} already exists'.format(web_directory))
        project_dir = path.dirname(path.realpath(__file__))
        shutil.rmtree(web_directory, ignore_errors=True)
        shutil.copytree(path.join(project_dir, 'web'), web_directory)
        os.makedirs(web_directory, exist_ok=True)
        
        # Generate result_data.js
        with open(path.join(web_directory, 'result_data.js'), 'wt') as f:
            f.write('var ANALYSIS_RESULTS = ')
            self._result_manager.dump_result_data(f)
            
        # Copy additional files
        web_result_directory = path.join(web_directory, 'results')
        os.makedirs(web_result_directory, exist_ok=True)
        for fname in os.listdir(self._results_directory):
            full_path = path.join(self._results_directory, fname)
            if path.isfile(full_path):
                shutil.copy2(full_path, path.join(web_directory, 'results', fname))
            
        # Open the browser
        if open_browser:
            webbrowser.open('file:///{}/index.html'.format(web_directory), new=2)
            
    def generate_word(self, output_file, result_ids=None):
        '''Generates a Microsoft Word (.docx) file with the results known to the analysis context.

        Args:
            output_file (str): Path to the Word file to be generated, normally with a .docx extension.
                The directory part of the path should already exist.
            result_ids (list of str): A list of fully qualified result IDs to be included in the output document.
                If the specified results have children, these will be recursively be included, too.
                If set to None, all results will be included.
        '''
        
        WordGenerator(self._result_manager.results,
                      self._results_directory).generate(output_file, result_ids)
