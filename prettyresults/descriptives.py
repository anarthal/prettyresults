from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats

from .utils import VarType, readable_index, freq_bar, freq_pie, format_float

# For simplicity, mean CI is included here too
def mean_confidence_interval(data, confidence=0.95):
    data = data[~np.isnan(data)]
    sample_mean = np.mean(data)
    sem = stats.sem(data, nan_policy='raise')
    n = len(data)
    t_value = stats.t.ppf((1.0+confidence)/2, n-1)
    interval_length = t_value * sem
    return (sample_mean, sample_mean-interval_length, sample_mean+interval_length, n)

def format_mean_ci_raw(lower, upper, decimals=2):
    return '{} ≤ μ ≤ {}'.format(format_float(lower, decimals), format_float(upper, decimals))

def format_mean_ci(result, decimals=2):
    return format_mean_ci_raw(result[1], result[2], decimals)

# Utilities to add results
def add_mean_ci_result(parent_result, series, confidence=0.95,
                       result_id='mean_ci', result_name='Intervalo de confianza para la media'):
    mean, lower, upper, n = mean_confidence_interval(series.values, confidence)
    total_cases = len(series)
    lost_cases = total_cases - n
    lost_cases_percent = lost_cases/total_cases*100.0
    parent_result.add_keyvalue_table(
        result_id,
        result_name,
        [
            ['Tamaño de muestra total', str(total_cases)],
            ['Casos perdidos', '{} ({:.2f}%)'.format(lost_cases, lost_cases_percent)],
            ['Tamaño de muestra efectivo', str(n)],
            ['Confianza', str(confidence)],
            ['Valor estimado para la media', '{:.2f}'.format(mean)],
            ['Intervalo de confianza', format_mean_ci_raw(lower, upper)]
        ]
    )

def add_histogram_result(parent_result, series, var_meta):
    series.hist(bins=var_meta.get('bins'))
    plt.xlabel(var_meta['desc'])
    plt.ylabel('Frecuencia')
    plt.title(var_meta['desc'])
    parent_result.add_figure('hist', 'Histograma')
    plt.close('all')

    
def add_frequency_results(parent_result, series, var_meta, *, calculate_value_counts=True, bar_plot=True, pie_plot=False):
    if calculate_value_counts:
        value_counts = series.value_counts()
    else:
        value_counts = series.copy()
        
    # Pretty value counts
    value_counts.index = readable_index(value_counts.index, var_meta)
    value_counts.index.name = var_meta['desc']
    
    # Bar plot
    if bar_plot:
        freq_bar(value_counts, title=var_meta['desc'])
        parent_result.add_figure('freq_bar', 'Gráfico de frecuencias')
        
    # Pie plot
    if pie_plot:
        freq_pie(value_counts, title=var_meta['desc'])
        parent_result.add_figure('freq_pie', 'Gráfico de frecuencias (diagrama de sectores)')
    
    # Table
    effective_sample_size = value_counts.sum()
    if calculate_value_counts:
        sample_size = len(series.index)
        num_nans = series.isna().sum()
        nans_percent = 100.0*num_nans/sample_size
        table_post = 'N = {}, perdidos = {} ({:.2f}%)'.format(sample_size, num_nans, nans_percent)
    else:
        sample_size = effective_sample_size
        table_post = 'N = {}'.format(sample_size)
        
    df_value_counts = pd.DataFrame(data={
        'Frecuencia': value_counts,
        'Porcentaje': value_counts.map(lambda v: '{:.2f}%'.format(100.0*v/effective_sample_size))
    })
    parent_result.add_dataframe_table(
        'freq_table',
        'Tabla de frecuencias',
        df_value_counts,
        post=table_post
    )
    
    plt.close('all')
    
def add_per_year_frequency_result(parent_result, series, per_year_series, var_meta):
    desc = var_meta['desc']
    cross_year = pd.crosstab(per_year_series, series)
    cross_year.columns = readable_index(cross_year.columns, var_meta)
    cross_year.columns.name = desc
    freq_bar(cross_year, '{} por año'.format(desc), ylabel='Frecuencia')
    parent_result.add_figure('freq_bar_by_year', 'Gráfico de frecuencias por año')
    plt.close('all')
    
# Apply a default set of single variable analysis to all variables
def _descriptive(parent_result, df, varname, var_meta, year_name='AÑO'):
    result = parent_result.add_container(varname, '{} ({})'.format(var_meta['desc'], varname))
    
    if var_meta['type'] == VarType.Int:
        add_histogram_result(result, df[varname], var_meta)
        add_mean_ci_result(result, df[varname])
    else:
        add_frequency_results(result, df[varname], var_meta) # table & bar plot
        add_per_year_frequency_result(result, df[varname], df[year_name], var_meta)
        
        # Original counts (if they exist)
        orig_varname = varname + '_ORIGINAL'
        if orig_varname in df:
            orig_result = result.add_container('orig', 'Datos originales')
            add_frequency_results(orig_result, df[orig_varname], var_meta)
            add_per_year_frequency_result(orig_result, df[orig_varname], df[year_name], var_meta)

    
def descriptives(parent_result, df, variable_meta, varnames=None, year_name='AÑO'):
    if varnames is None:
        varnames = variable_meta.keys()
    for varname in varnames:
        category = variable_meta[varname]['category']
        result = parent_result.get_child(category)
        if variable_meta[varname].get('descriptive', True):
            _descriptive(result, df, varname, variable_meta[varname], year_name)