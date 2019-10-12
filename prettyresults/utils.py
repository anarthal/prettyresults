import enum
from matplotlib import pyplot as plt

class VarType(enum.Enum):
    Int = 1
    Bool = 2
    Category = 3

def _get_label_dict(variable):
    if variable['type'] == VarType.Category:
        res = { elm[0]: elm[1] for elm in variable['labels'].values() }
        res.update({ key: value[1] for key, value in variable['labels'].items() })
        return res
    elif variable['type'] == VarType.Bool:
        return { 0.0: 'No', 1.0: 'Sí' }
    else:
        return None
    
def format_float(value, decimals=2):
    return ('{:.' + str(decimals) + 'f}').format(value)

def format_percentage(value):
    return format_float(value) + '%'
    
def readable_index(index, variable):
    label_dict = _get_label_dict(variable)
    if label_dict is None:
        return index
    else:
        return index.map(lambda x: label_dict.get(x, x))
    
def make_index_readable(obj, variable):
    obj.index = readable_index(obj.index, variable)
    obj.index.name = variable['desc']
    
# Plots
def freq_bar(value_counts, title='', xlabel='', ylabel='Frecuencia', rot=0, x_value_labels_dict=None, **kwargs):
    plt.figure(figsize=(8,5))
    ax = value_counts.plot.bar(title=title, rot=rot, **kwargs)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.subplots_adjust(top = 0.95, bottom = 0.05)
    if x_value_labels_dict is not None:
        plt.gca().set_xticklabels([x_value_labels_dict[elm] for elm in value_counts.index])
    
    for container in ax.containers:
        for rect in container:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width()/2., height+0.1, str(int(height)),
                    fontsize=8, fontweight='bold', ha='center', va='bottom')

def freq_pie(value_counts, size=8.0, **kwargs):
    plt.figure(figsize=(size, size)) # Prevent distortion
    ax = value_counts.plot.pie(legend=True, use_index=False,
                               labels=None, autopct='%.2f%%',
                                **kwargs)
    ax.set_ylabel('') # by default, series name is included as ylabel - remove it
    
