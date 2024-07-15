import numpy as np
import matplotlib.pyplot as plt
import random
import Partners
import SIM0
import SIM1

from Partners import PartnerData
from SIM0 import Sim_0
from SIM1 import Sim_1




# Assuming Sim_0 and Sim_1 are defined as per your provided code
# and PartnerData.reset_partners_initial() initializes the partners


def get_average_metrics(sim_function, iterations, customer_count, partner_data):
    metrics = {'Partner 1': [], 'Partner 2': [], 'Partner 3': [], 'Partner 4': []}
    for _ in range(iterations):
        _, _, partner_metrics = sim_function(customer_count, partner_data)
        for partner in metrics.keys():
            metrics[partner].append(partner_metrics[partner])
    # Calculate average metrics over all iterations
    average_metrics = {partner: average_dicts(metrics[partner]) for partner in metrics}
    return average_metrics

def average_dicts(dicts):
    # Function to average a list of dictionaries with the same structure
    averaged = {}
    for key in dicts[0].keys():
        averaged[key] = np.mean([d[key] for d in dicts], axis=0)
    return averaged

def run_sim_0(customers_count, partner_data):
    # Create an instance of Sim_0
    simulation_0 = Sim_0()
    # Run the simulation with given customer count and partner data
    baseline_metrics, monthly_customer_counts = simulation_0.run_baseline(customers_count, partner_data)
    # Extract and return the relevant data
    return baseline_metrics, monthly_customer_counts

def run_sim_1(customers_count, partner_data):
    # Create an instance of Sim_1
    simulation_1 = Sim_1()
    # Run the simulation with given customer count and partner data
    total_tokens_redeemed, tier_distribution, partner_metrics, wallet_values, average_wallet_value, customer_savings_ST, monthly_customer_counts = simulation_1.run_simulation(customers_count, partner_data)
    # Extract and return the relevant data
    return total_tokens_redeemed, tier_distribution, partner_metrics, wallet_values, average_wallet_value, customer_savings_ST, monthly_customer_counts

def run_simulations(iterations, customers_count, seed=42):
    sim_0_results = []
    sim_1_results = []

    for _ in range(iterations):
        # Set the seed for each iteration
        np.random.seed(seed)
        random.seed(seed)

        # Reset partner data for each iteration
        partners_sim_0 = PartnerData.reset_partners_initial()
        partners_sim_1 = PartnerData.reset_partners_initial()

        # Run Sim_0 and Sim_1 simulations
        result_0 = run_sim_0(customers_count, partners_sim_0)
        sim_0_results.append(result_0)

        # Reset the seed again for Sim_1 to ensure identical random state
        np.random.seed(seed)
        random.seed(seed)

        result_1 = run_sim_1(customers_count, partners_sim_1)
        sim_1_results.append(result_1)

    return sim_0_results, sim_1_results


