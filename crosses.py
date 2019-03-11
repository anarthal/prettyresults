from matplotlib import pyplot as plt
import pandas as pd
from collections import namedtuple
from scipy import stats

from .utils import readable_index, freq_bar
from .results import Label

ContingencyResult = namedtuple('ContingencyResult',['p', 'chi2', 'too_small_freqs', 'crosstab', 'contingency_table', 'n'])
KendallTauResult = namedtuple('KendallTauResult', ['p', 'tau', 'n'])

def chi2_contingency(df, variable_meta, name1, name2):
    # Variable metadata
    var1 = variable_meta[name1]
    var2 = variable_meta[name2]
    
    # Data
    series1 = df[name1]
    series2 = df[name2]

    # Cross table
    cross = pd.crosstab(series1, [series2])
    cross.index = readable_index(cross.index, var1)
    cross.columns = readable_index(cross.columns, var2)
    cross.index.name = var1['desc']
    cross.columns.name = var2['desc']
    
    # Statistical analysis
    chi2, p, _, expected = stats.chi2_contingency(cross.values)
    
    # Check for too-small-frequencies
    min_expected = expected.min()
    min_actual = cross.values.min()
    too_few = (min_expected < 5) or (min_actual < 5)
    
    # Expected/actual frequency table (contingency table)
    expected_df = pd.DataFrame(expected, index=cross.index, columns=cross.columns)
    totals = cross.sum(axis=1)
    expected_percent = (expected_df*100.0).div(totals, axis='index')
    actual_percent = (cross*100.0).div(totals, axis='index')
    contingency_table = expected_percent.copy()
    for column in cross:
        for row_label in cross.index:
            contingency_table.loc[row_label, column] = '{expf:.0f}->{actf}, {expp:.2f}%->{actp:.2f}%'.format(
                expf=expected_df.loc[row_label, column], expp=expected_percent.loc[row_label, column],
                actf=cross.loc[row_label, column], actp=actual_percent.loc[row_label, column])
            
    # Sample size
    n = cross.sum().sum()
            
    return ContingencyResult(p, chi2, too_few, cross, contingency_table, n)

def significative_label():
    return Label('green', 'Significativo')

def too_small_freqs_label():
    return Label('red', 'Frecuencias demasiado pequeñas')
    
def add_chi2_results(parent_result, chi_values, significance=0.05):
    # Cross graph
    freq_bar(chi_values.crosstab)
    parent_result.add_figure('freq_bar', 'Gráfico de frecuencias')
    plt.close('all')
    
    # Frequency table
    parent_result.add_dataframe_table('freq_table', 'Tabla de frecuencias', df=chi_values.crosstab)
    
    # Contingency table
    parent_result.add_dataframe_table(
        'contingency_table',
        'Tabla de contingencia',
        chi_values.contingency_table,
        pre='Esperado -> Obtenido'
    )
    
    # Chi square result
    significative = (chi_values.p < significance)
    labels = []
    if significative:
        labels.append(significative_label())
    if chi_values.too_small_freqs:
        labels.append(too_small_freqs_label())
    parent_result.add_keyvalue_table(
        'chi_square_independence',
        'Test chi cuadrado de independencia',
        [
            ('Chi cuadrado', '{:.4f}'.format(chi_values.chi2)),
            ('Significancia', str(significance)),
            ('p', '{:.4f}'.format(chi_values.p)),
            ('Tamaño de muestra', str(chi_values.n)),
            ('Comprobación: frecuencias esperadas/obtenidas por celda',
                'FALLADO: frecuencias demasiado pequeñas' if chi_values.too_small_freqs else 'OK'),
        ],
        labels=labels
    )
    
def add_kendall_tau_result(parent_result, tau_values, significance=0.05):
    parent_result.add_keyvalue_table(
        'kendall_tau',
        'Tau de Kendall',
        [
            ('Tau de Kendall', '{:.4f}'.format(tau_values.tau)),
            ('Significancia', str(significance)),
            ('p', '{:.5f}'.format(tau_values.p)),
            ('Tamaño de muestra', str(tau_values.n)),
        ],
        labels=[significative_label()] if tau_values.p < significance else []
    )