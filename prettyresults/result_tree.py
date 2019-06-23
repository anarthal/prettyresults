import webbrowser
from os import path
import os
import shutil
import tempfile

from .results import ResultManager
from .word import WordGenerator

class ResultTree(object):
    '''
    Class that keeps track of all results. It is the entry point of a prettyresults application.
    It provides methods to access and add results, and to generate the web page and the Word
    document once all results have been added.
    
    A ResultTree is also associated to a results directory, where temporary files will
    be written to.
    '''
    def __init__(self, results_directory=None, container_results=[]):
        '''
        Initializes the result tree and creates the root result (a container
        result with ID 'root'.
        
        Args:
            results_directory (str or None): Path to the directory where temporary
                result files will be written to. If it's None, a temporary directory
                will be created for result files, which will be removed
                when the ResultTree object is destroyed.

            container_results (list of tuples): Specifies a list of container
                results to be created. This is a shortcut to create container results
                beforehand. container_result must be a list of 3 element tuples.
                Element 0 is the container unqualified ID, element 1 is the container
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
            result_id (str): Qualified ID of the result to be retrieved.
        Returns:
            Result object.
        '''
        return self._result_manager[result_id]
    
    def dump_results(self):
        self._result_manager.dump()
            
    def generate_web(self, web_directory, *, open_browser=False, overwrite=False):
        '''Generates the web page.
        
        The webpage will be created under web_directory and will contain every result
        known to the analysis context. Open index.html to view the web.
        
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
            output_file (str): Path to the Word file to be generated,
                normally with a .docx extension.
                The directory part of the path should already exist.
            result_ids (list of str): A list of fully qualified result IDs
                to be included in the output document. If the specified results have
                children, these will be recursively be included, too.
                If set to None, all results will be included.
        '''
        
        WordGenerator(self._result_manager.results,
                      self._results_directory).generate(output_file, result_ids)
