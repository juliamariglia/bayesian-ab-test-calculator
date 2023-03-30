import re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go

from skeleton import input_skeleton
from ab_test.bayesian_engine import bayesian_test

percent_formatter = "{:.2%}".format

# ********* #
#  Layout   #
# ********* #
st.set_page_config(page_title='Bayesian Stats Calculator', page_icon=':sparkles:', layout='wide')
st.title("Bayesian Stats Calculator")
st.markdown("This calculator uses bayesian closed form analytics to evaluate whether any\
    of your variants are significantly different from one another. Refresh browser to clear entries.")

# ********* #
#  Sidebar  #
# ********* #
with st.sidebar:
    st.header("Configs")
    analytic_method = st.radio(label = "Select metric type",
                        options=['conversion', 'numeric, continuous', 'numeric, discrete'],
                        disabled=False)
    n_variants = st.number_input(label='Number of variants:', step=1, min_value=2, key="n_variants")
    significance_threshold = st.slider(label = 'Significance Threshold', min_value=75.0, max_value = 100.0, value=95.0, disabled=True)


# ********* #
#  Inputs   #
# ********* #
with st.expander('Input experiment data:'):
    var_labels_ls, sample_size_ls, conversions_ls, sum_numeric_ls = input_skeleton(analytic_method=analytic_method, n_variants=n_variants)

df_experiment_data = pd.DataFrame([var_labels_ls, sample_size_ls, conversions_ls, sum_numeric_ls]).T
df_experiment_data.columns = ['variant', 'sample_size', 'conversions', 'sum_numeric']
df_experiment_data['conversion rate'] = (df_experiment_data.conversions/df_experiment_data.sample_size)
df_experiment_data['avg numeric metric'] = (df_experiment_data.sum_numeric/df_experiment_data.conversions).apply(lambda x: round(x, 4))
df_experiment_data['conversion rate'] = df_experiment_data['conversion rate'].apply(lambda x: percent_formatter(x))

button_calculate = st.button('Calculate')

# ********* #
#  Results  #
# ********* #
st.header("Results")
if not button_calculate:
    st.markdown("_Click calculate to analyze_")
else:
    if (re.match('numeric', analytic_method) != None) and np.sum(sum_numeric_ls) == 0:
        st.error('_Error: please input non-zero numeric metrics._') # this won't occur for conversion metrics since min requirement is 1 on input
    else:
        bayesian = bayesian_test()
        prob_to_be_best, df_simulations = bayesian.evaluate(df_experiment_data, analytic_method=analytic_method)
        leader = prob_to_be_best[prob_to_be_best['probability to be best (%)'] > significance_threshold].variant
        if leader.any():
            st.success(":trophy: **_" + leader[0] + "_** _parameter is the leader!_")
        else:
            st.error(':red_circle: _No leader found._')

        df_experiment_data = pd.merge(df_experiment_data, prob_to_be_best, how='left', on='variant') # join input df with calculations
        df_experiment_data['probability to be best (%)'].fillna(0, inplace=True) # fill null prob to be best with 0; occurs where other variant(s) make up 100% probability
        df_experiment_data.dropna(axis=1, inplace=True)
        df_experiment_data.fillna(0, inplace=True)
        
        # FIGURE: tabular output of metrics
        fig_experiment_table = go.Figure(data=[go.Table(
            header=dict(values=list(df_experiment_data.columns),
                        align='left'),
            cells=dict(values=df_experiment_data.transpose().values.tolist(),
                    fill_color='lavender',
                    align='left'))
        ])
        fig_experiment_table.update_layout(width=1000, height=100, margin=dict(l=0, r=0, b=0, t=0))
        fig_experiment_table.update_traces(cells_font=dict(size = 12), cells_height = 25)
        st.write(fig_experiment_table)

        with st.container():
            st.markdown("**Probability to be best**")
            # FIGURE: probability to be best bar chart
            fig_prob_to_be_best = px.bar(data_frame = df_experiment_data[['variant', 'probability to be best (%)']], orientation='h', y = "variant", x = "probability to be best (%)")
            fig_prob_to_be_best.update_layout(width=1000, height=250, margin=dict(l=0, r=0, b=0, t=0))
            fig_prob_to_be_best.update_traces(marker_color='rgb(203,213,232)')
            st.write(fig_prob_to_be_best)

            st.markdown("**Simulation of parameter**")
            st.write(bayesian.describe())
            # FIGURE: posterior simulations distribution plot
            fig_posterior_simulations = ff.create_distplot([df_simulations['{}'.format(i)].values for i in df_simulations.columns], group_labels = df_simulations.columns, bin_size=.2, show_hist=False)
            fig_posterior_simulations.update_layout(width=1000, height=400, margin=dict(l=0, r=0, b=0, t=0), showlegend=False)
            st.write(fig_posterior_simulations)
