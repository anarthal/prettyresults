import json
from os import path
from matplotlib import pyplot as plt
from collections import namedtuple
import weakref

Label = namedtuple('Label', ('color', 'text'))
    
class BaseResult(object):
    '''
    The base class of all result objects.
    
    Attributes:
        id (str): The fully-qualified ID of the result object (e.g. root.container1.container2.result).
        name (str): Human-readable display name for the result.
        children (list of str): List of fully-qualified IDs of the children of this result.
                                Only relevant for containers.
    '''
    
    def __init__(self, manager, id_, name, labels=[], children=[]):
        self.manager = manager
        self._id = id_
        self.name = name
        self.labels = labels
        self.data = {}
        self.children = children.copy()
    
    @property
    def id(self):
        return self._id
    
    def __getattr__(self, name):
        return self.data[name]
    
    def merge(self, old_result):
        self.children = old_result.children
    
    def dump(self):
        pass
    
    @property
    def result_type(self):
        return self.__class__.__name__
    
    @classmethod
    def from_json(cls, manager, json_obj):
        return cls(
            manager=manager,
            id_=json_obj['id'],
            name=json_obj['name'],
            labels=json_obj['labels'],
            children=json_obj['children'],
            **json_obj['data']
        )


class ContainerResult(BaseResult):
    ''' A container result '''
    def add(self, result_factory, id_, name, *args, **kwargs):
        if '.' in id_:
            raise ValueError('Result ID cannot contain dots: {}'.format(name))
        child_id = self.id + '.' + id_
        result = result_factory(manager=self.manager, id_=child_id, name=name, *args, **kwargs)
        if child_id not in self.children:
            self.children.append(result.id)
        self.manager.add(result)
        return result
    
    def add_container(self, *args, **kwargs):
        ''' Placeholder'''
        return self.add(ContainerResult, *args, **kwargs)
    
    def add_figure(self, *args, **kwargs):
        ''' Placeholder'''
        return self.add(FigureResult.from_figure, *args, **kwargs)
    
    def add_table(self, *args, **kwargs):
        ''' Placeholder'''
        return self.add(TableResult, *args, **kwargs)
    
    def add_dataframe_table(self, *args, **kwargs):
        ''' Placeholder'''
        return self.add(TableResult.from_dataframe, *args, **kwargs)
    
    def add_series_table(self, *args, **kwargs):
        ''' Placeholder'''
        return self.add(TableResult.from_series, *args, **kwargs)
    
    def add_keyvalue_table(self, *args, **kwargs):
        ''' Placeholder'''
        return self.add(TableResult.from_key_value, *args, **kwargs)
    
    def get_child(self, id_):
        return self.manager[self.id + '.' + id_]

    
class FigureResult(BaseResult):
    def __init__(self, fig, **kwargs):
        super().__init__(**kwargs)
        self.unsaved_fig = fig
        self.data = {
            'filename': self.filename
        }
        
    @property
    def filename(self):
        return self.id + '.jpg'

    @property
    def full_path(self):
        return path.join(self.manager.result_directory_path, self.filename)

    def dump(self):
        if self.unsaved_fig is not None:
            self.unsaved_fig.savefig(self.full_path, bbox_inches='tight')
            self.unsaved_fig = None
            
    @classmethod
    def from_figure(cls, fig='current', **kwargs):
        if fig == 'current':
            fig = plt.gcf()
        return cls(fig=fig, **kwargs)
    
    @classmethod
    def from_json(cls, manager, json_obj):
        return cls(
            manager=manager,
            id_=json_obj['id'],
            name=json_obj['name'],
            labels=json_obj['labels'],
            children=json_obj['children'],
            fig=None
        )

        
class TableResult(BaseResult):
    def __init__(self, headings, rows, pre='', post='', **kwargs):
        super().__init__(**kwargs)
        self.data = {
            'headings': headings,
            'rows': rows,
            'pre': pre,
            'post': post
        }
        
    def add_row(self, item):
        self.data['rows'].append(item)
                
    @classmethod
    def from_dataframe(cls, df, **kwargs):
        rows_heading = df.index.name if df.index.name is not None else ''
        cols_heading = df.columns.name if df.columns.name is not None else ''
        heading_sep = '/' if rows_heading != '' and cols_heading != '' else ''
        headings = [rows_heading + heading_sep + cols_heading] + list(df.columns.values)
        rows = [[str(df.index[i])] + list(df.iloc[i].values.astype(str)) for i in range(len(df.index))]
        return cls(headings, rows, **kwargs)
    
    @classmethod
    def from_key_value(cls, values, **kwargs):
        return cls(headings=['Nombre', 'Valor'], rows=values, **kwargs)
    
    @classmethod
    def from_series(cls, series, **kwargs):
        left_heading = series.index.name if series.index.name is not None else ''
        right_heading = series.name if series.name is not None else ''
        return cls(headings=[left_heading, right_heading],
                   rows=list(zip(series.index.astype(str), series.values.astype(str))),
                   **kwargs)


class ResultManager(object):
    RESULT_TYPE_MAP = { result.__name__: result for result in
                        (ContainerResult, FigureResult, TableResult) }
    
    def __init__(self, result_directory, containers):
        self._result_directory = result_directory
        self._results = self._load_result_directory()
        self._root = ContainerResult(weakref.proxy(self), 'root', 'Root result')
        self.add(self._root)
        self._create_containers(self._root, containers)

    def _result_from_json(self, result_obj):
        result_class = self.RESULT_TYPE_MAP[result_obj['type']]
        return result_class.from_json(weakref.proxy(self), result_obj)
    
    def _load_result_directory(self):
        # Read the JSON
        try:
            with open(self.json_path, 'rt') as f:
                obj = json.load(f)
                results = { elm['id']: elm for elm in obj['results'] }
        except (FileNotFoundError, json.JSONDecodeError):
            results = {}
        
        # Create the actual objects
        res = { id_: self._result_from_json(result_obj)
                for id_, result_obj in results.items() }
        
        return res
    
    def dump_result_data(self, fobj):
        results_array = [{
            'id': result.id,
            'name': result.name,
            'type': result.result_type,
            'data': result.data,
            'labels': result.labels,
            'children': result.children
        } for result in self._results.values()]
        json.dump({
            'results': results_array,
            'root_result': 'root'
        }, fobj, indent=4)
        
    @property
    def results(self):
        return self._results
        
    @property
    def root(self):
        return self._root
    
    @property
    def result_directory_path(self):
        return self._result_directory
    
    @property
    def json_path(self):
        return path.join(self._result_directory, 'data.json')
    
    def add(self, result):
        old_result = self._results.get(result.id)
        if old_result is not None:
            result.merge(old_result)
        result.dump()
        self._results[result.id] = result
  
    def dump(self):
        with open(self.json_path, 'wt') as f:
            self.dump_result_data(f)
            
    def __getitem__(self, id_):
        return self._results[id_]
            
    def _create_containers(self, parent, container_specs):
        for spec in container_specs:
            cont = parent.add_container(spec[0], spec[1])
            self._create_containers(cont, spec[2])