import webbrowser
from os import path
import os
import shutil

from .results import ResultManager
from .word import WordGenerator

class AnalysisContext(object):
    '''
    Class that accumulates the results of an analysis.
    
    An analysis context has a result directory, a temporary directory where result files
    will be written to; and keeps track of the generated results. It provides methods to access
    and add results, and to write them in different formats.
    '''
    def __init__(self, results_directory, container_results=[]):
        '''
        Initializes the analysis context. The context will contain the root result
        (a container with ID 'root'), at least.
        
        Args:
            results_directory (str): path to the directory where result files will be written to.
                Several files (result data, images...) will be written to the directory.
                If the directory does not already exist, it will be created. If the directory
                contains result files from previous runs, they will be loaded and added,
                as if they had been created in the current run.
            container_results (list of tuples): specifies a list of container results to be created. This is
                a shortcut to create container results beforehand. container_result must be a list
                of 3 element tuples. Element 0 is the container ID, element 1 is the container
                display name, and element 2 is a list of child containers to be created, with the
                same described format (so the structure can be arbitrarily nested).
        '''
        self._results_directory = results_directory
        os.makedirs(results_directory, exist_ok=True)
        self._result_manager = ResultManager(results_directory, container_results)

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
