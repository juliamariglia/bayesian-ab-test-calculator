import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from typing_extensions import final

class bayesian_test:
    """
    Parameters:
    simulation_size: int
    seed: int
    """
    def __init__(self, simulation_size=10000, set_seed=9):
        
        self.simulation_size = simulation_size
        self.set_seed=set_seed
        
    def evaluate(self, df, prior_alpha = None, prior_beta = None, prior_success=0, prior_failure=0, analytic_method=None):
        """
        Binomial likelihood with weak Beta priors.
        Parameters:
        df: dataframe of input conversion data with cols:
            - variant
            - sample_size
            - conversions
        """
        
        np.random.seed(self.set_seed)
        
        self.analytic_method = analytic_method
        self.df_simulations = pd.DataFrame()
        self.dict_posteriors = {}
        
        for var in list(df.variant):
            sample_size = int(df[df.variant == var].sample_size)
            successes = int(df[df.variant == var].conversions)
            failures = sample_size - successes
            if bool(df.sum_numeric.notna().sum()):
                sum_of_numeric = int(df[df.variant == var].sum_numeric)
            
            if analytic_method == 'conversion':
                # simulation of beta distribution for posterior
                # setting prior parameters
                self.prior_alpha = prior_success + 1
                self.prior_beta = prior_failure + 1
                self.df_simulations[f'{var}'] = np.random.beta(self.prior_alpha+successes, self.prior_beta+failures, size=self.simulation_size)
            elif analytic_method == 'numeric, continuous':
                self.prior_gamma_alpha = 0.1
                self.prior_gamma_scale = 0.1
                self.df_simulations[f'{var}'] = 1 / (np.random.gamma(
                    shape=(self.prior_gamma_alpha + successes),
                    scale=(self.prior_gamma_scale / (1 + (self.prior_gamma_scale) * sum_of_numeric)),
                    size=self.simulation_size)
                )
                
            elif analytic_method == 'numeric, discrete':
                self.prior_gamma_alpha = 0.1
                self.prior_gamma_scale = 0.1
                self.df_simulations[f'{var}'] = np.random.gamma(
                    shape=(self.prior_gamma_alpha + sum_of_numeric),
                    scale=(self.prior_gamma_scale / (1 + (self.prior_gamma_scale) * successes)),
                    size=self.simulation_size
                )

            
        # calculate probability to be best variant
        prob_to_be_best = pd.DataFrame(np.round(self.df_simulations.idxmax(axis=1).value_counts(normalize=True)*100, 2)).reset_index()
        prob_to_be_best.columns = ['variant', 'probability to be best (%)']
        
        return prob_to_be_best, self.df_simulations
    
    @final
    def show_posterior_distributions(self):
        x = np.linspace(0,1,1000)
        plt.title('Expected Values for Posteriors')
        for var in self.dict_posteriors:
            x_lim_min = min(self.df_simulations[f'{var}'])
            x_lim_max = max(self.df_simulations[f'{var}'])
            plt.plot(x, self.dict_posteriors.get(var).pdf(x), label=var)
            plt.legend()
        plt.xlim(x_lim_min - 0.05, x_lim_max + 0.05)
        plt.show()

    def describe(self):
        if self.analytic_method == 'conversion':
            msg = "Conversion data is modeled as a binomial distribution, with each variants' binomial parameter modeled with a weak beta conjugate prior (prior beta successes = {}, prior beta failures = {}).\
                The expected value of the binomial distribution describing the data is the posterior beta distribution describing the parameters themselves, plotted below.".format(self.prior_alpha, self.prior_beta)
        if self.analytic_method == 'numeric, continuous':
            msg = "Continuous numeric data is modeled as an exponential distribution, with each variants' parameter modeled with a weak gamma priors (prior gamma alpha = {}, prior gamma scale = {}).\
                The expected value of the exponential distribution describing the data is the inverse of the parameter, plotted below.".format(self.prior_gamma_alpha, self.prior_gamma_scale)
        if self.analytic_method == 'numeric, discrete':
            msg = "Continuous numeric data is modeled as a poisson distribution, with each variants' parameter modeled with a weak gamma priors (prior gamma alpha = {}, prior gamma scale = {}).\
                The expected value of the poisson distribution describing the data is the parameter, plotted below.".format(self.prior_gamma_alpha, self.prior_gamma_scale)
        return msg