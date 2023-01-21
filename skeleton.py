import streamlit as st

def input_skeleton(analytic_method, n_variants):
    """
    Parameters:
    This function creates the skeleton of the input data within st.expander in app.py.
    - analytic_method: str, 1 of ['conversion', 'numeric, discrete', 'numeric, continuous']
    - n_variants: int
    """
    var_labels_ls = []
    sample_size_ls = []
    conversions_ls = []
    sum_numeric_ls = []

    var_label, var_sample_size_input, var_conversions_input, var_numeric_input = st.columns([1,2,2,2])
    with var_label:
        for n in range(0, n_variants):
            var_labels_ls.append(st.text_input(label='', value='variant ' + str(n+1), key='var label ' + str(n)))

    with var_sample_size_input:
        for n in range(0, n_variants):
            sample_size_ls.append(st.number_input('sample size', step=1, min_value=1, key='sample size ' + str(n)))
    
    with var_conversions_input:
        for n in range(0, n_variants):
            conversions_ls.append(st.number_input('conversions', step=1, min_value=1, key='conversions '+ str(n)))

    if analytic_method == 'conversion':
        pass
    elif analytic_method in ['numeric, discrete', 'numeric, continuous']:
        with var_numeric_input:
            for n in range(0, n_variants):
                sum_numeric_ls.append(st.number_input('sum numeric metric', min_value=0.0, key='sum numeric metric '+ str(n)))

    return var_labels_ls, sample_size_ls, conversions_ls, sum_numeric_ls