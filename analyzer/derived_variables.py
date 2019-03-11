import numpy as np

DEFAULT_NA_VALUES = (98.0, 99.0)

def _combine_variables_row(row, varname1, varname2, on_conflict, na_values, ctx):
    v1 = row[varname1]
    v2 = row[varname2]
    is_nan_1 = (np.isnan(v1) or v1 in na_values)
    is_nan_2 = (np.isnan(v2) or v2 in na_values)
    if is_nan_1 and is_nan_2:
        return np.nan
    elif not is_nan_1 and is_nan_2:
        return v1
    elif is_nan_1 and not is_nan_2:
        return v2
    elif v1 == v2:
        return v1
    else: # Conflict
        res = on_conflict(v1, v2) if callable(on_conflict) else on_conflict
        if np.isnan(res):
            ctx.add_warning(row, 'Valores contradictorios: {}={} vs. {}={}'.format(varname1, v1, varname2, v2))
        return res
    
def _multibool_to_enum_row(row, variables, na_values, ctx):
    row_fragment = row[variables]
    num_vars = len(variables)
    if row_fragment.isna().sum() + row_fragment.isin(na_values).sum() == num_vars:
        return np.nan
    true_vars = row_fragment[row_fragment == 1.0]
    if len(true_vars) != 1:
        value_list = ', '.join('{}={}'.format(varname, row_fragment[varname]) for varname in row_fragment.index)
        ctx.add_warning(row, 'Multi-bool a enum - valores contradictorios: {}'.format(value_list))
        return np.nan
    return true_vars.index[0]

def combine_variables(varname1, varname2, on_conflict=np.nan, na_values=DEFAULT_NA_VALUES):
    def res(df, ctx):
        return df.apply(lambda row: _combine_variables_row(
            row, varname1, varname2, on_conflict, na_values, ctx), axis=1)
    return res

def logical_or(varname1, varname2, na_values=DEFAULT_NA_VALUES):
    return combine_variables(varname1, varname2, lambda v1, v2: v1 or v2, na_values)

def multibool_to_enum(variables, na_values=DEFAULT_NA_VALUES):
    def res(df, ctx):
        return df.apply(lambda row: _multibool_to_enum_row(
            row, variables, na_values, ctx), axis=1)
    return res
