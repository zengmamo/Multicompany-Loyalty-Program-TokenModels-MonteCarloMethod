import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import random
import Partners
import SIM0
import SIM1

from Partners import PartnerData
from SIM0 import Sim_0
from SIM1 import Sim_1

# KPI functions

class KPI_calcs:  

    def calculate_average_purchases_with_ci(data_structure, num_bootstraps=10000, confidence_level=0.9):
        # Step 1: Sum all purchases for each year and each iteration
        yearly_purchase_sums = []
        for iteration in range(len(next(iter(data_structure.values()))['Purchases Per Month'])):
            yearly_sum = 0
            for partner_data in data_structure.values():
                yearly_sum += sum(partner_data['Purchases Per Month'][iteration])
            yearly_purchase_sums.append(yearly_sum)

        # Step 2: Compute the overall average across all iterations
        overall_average = np.mean(yearly_purchase_sums)

        # Step 3: Bootstrap resampling to calculate confidence interval
        bootstrapped_averages = []
        for _ in range(num_bootstraps):
            bootstrap_sample = np.random.choice(yearly_purchase_sums, size=len(yearly_purchase_sums))
            bootstrapped_averages.append(np.mean(bootstrap_sample))

        # Step 4: Calculate the confidence interval
        lower_percentile = (1 - confidence_level) / 2 * 100
        upper_percentile = 100 - lower_percentile
        confidence_interval = np.percentile(bootstrapped_averages, [lower_percentile, upper_percentile])

        return overall_average, confidence_interval
    
    def calculate_average_sales_with_ci(data_structure, num_bootstraps=10000, confidence_level=0.9):
        # Step 1: Sum all purchases for each year and each iteration
        yearly_purchase_sums = []
        for iteration in range(len(next(iter(data_structure.values()))['Total Sales Per Month'])):
            yearly_sum = 0
            for partner_data in data_structure.values():
                yearly_sum += sum(partner_data['Total Sales Per Month'][iteration])
            yearly_purchase_sums.append(yearly_sum)

        # Step 2: Compute the overall average across all iterations
        overall_average = np.mean(yearly_purchase_sums)

        # Step 3: Bootstrap resampling to calculate confidence interval
        bootstrapped_averages = []
        for _ in range(num_bootstraps):
            bootstrap_sample = np.random.choice(yearly_purchase_sums, size=len(yearly_purchase_sums))
            bootstrapped_averages.append(np.mean(bootstrap_sample))

        # Step 4: Calculate the confidence interval
        lower_percentile = (1 - confidence_level) / 2 * 100
        upper_percentile = 100 - lower_percentile
        confidence_interval = np.percentile(bootstrapped_averages, [lower_percentile, upper_percentile])

        return overall_average, confidence_interval
    
    def calculate_average_customers_with_ci(data_structure, num_bootstraps=10000, confidence_level=0.9):
        # Step 1: Sum all purchases for each year and each iteration
        yearly_purchase_sums = []
        for iteration in range(len(next(iter(data_structure.values()))['Unique Customers Per Month'])):
            yearly_sum = 0
            for partner_data in data_structure.values():
                yearly_sum += sum(partner_data['Unique Customers Per Month'][iteration])
            yearly_purchase_sums.append(yearly_sum)

        # Step 2: Compute the overall average across all iterations
        overall_average = np.mean(yearly_purchase_sums)

        # Step 3: Bootstrap resampling to calculate confidence interval
        bootstrapped_averages = []
        for _ in range(num_bootstraps):
            bootstrap_sample = np.random.choice(yearly_purchase_sums, size=len(yearly_purchase_sums))
            bootstrapped_averages.append(np.mean(bootstrap_sample))

        # Step 4: Calculate the confidence interval
        lower_percentile = (1 - confidence_level) / 2 * 100
        upper_percentile = 100 - lower_percentile
        confidence_interval = np.percentile(bootstrapped_averages, [lower_percentile, upper_percentile])

        return overall_average, confidence_interval

    def calculate_frequency_change_with_ci(data_structure, num_bootstraps=10000, confidence_level=0.9):
        def calculate_average_frequency_change(data):
            total_purchases_per_month = [sum(iteration_data['Purchases Per Month'][0][month] for iteration_data in data.values()) for month in range(12)]
            total_unique_customers_per_month = [sum(iteration_data['Unique Customers Per Month'][0][month] for iteration_data in data.values()) for month in range(12)]
            average_purchasing_frequency_per_month = [total_purchases / total_unique_customers if total_unique_customers > 0 else 0 for total_purchases, total_unique_customers in zip(total_purchases_per_month, total_unique_customers_per_month)]
            frequency_changes = []
            for i in range(11):
                if average_purchasing_frequency_per_month[i] > 0:
                    frequency_change = ((average_purchasing_frequency_per_month[i + 1] - average_purchasing_frequency_per_month[i]) / average_purchasing_frequency_per_month[i]) * 100
                    frequency_changes.append(frequency_change)
                else:
                    frequency_changes.append(0)
            average_frequency_change = sum(frequency_changes) / len(frequency_changes) if frequency_changes else 0
            return average_frequency_change

        # Bootstrap resampling
        bootstrapped_frequency_changes = []
        for _ in range(num_bootstraps):
            bootstrap_sample = dict()
            for partner, data in data_structure.items():
                iteration_idx = np.random.randint(0, len(data['Purchases Per Month']))
                bootstrap_sample[partner] = {'Purchases Per Month': [data['Purchases Per Month'][iteration_idx]], 'Unique Customers Per Month': [data['Unique Customers Per Month'][iteration_idx]]}
            bootstrapped_frequency_changes.append(calculate_average_frequency_change(bootstrap_sample))

        # Calculate percentiles for confidence interval
        lower_percentile = (1 - confidence_level) / 2
        upper_percentile = 1 - lower_percentile
        lower_bound = np.percentile(bootstrapped_frequency_changes, lower_percentile * 100)
        upper_bound = np.percentile(bootstrapped_frequency_changes, upper_percentile * 100)

        # Calculate the mean
        mean_frequency_change = np.mean(bootstrapped_frequency_changes)

        return mean_frequency_change, lower_bound, upper_bound


    def calculate_spending_change_with_ci(data_structure, num_bootstraps=10000, confidence_level=0.9):
        def calculate_average_spending_change(data):
            total_sales_per_month = [sum(iteration_data['Total Sales Per Month'][0][month] for iteration_data in data.values()) for month in range(12)]
            total_unique_customers_per_month = [sum(iteration_data['Unique Customers Per Month'][0][month] for iteration_data in data.values()) for month in range(12)]
            average_spending_per_customer_per_month = [total_sales / total_unique_customers if total_unique_customers > 0 else 0 for total_sales, total_unique_customers in zip(total_sales_per_month, total_unique_customers_per_month)]
            spending_changes = []
            for i in range(11):
                if average_spending_per_customer_per_month[i] > 0:
                    spending_change = ((average_spending_per_customer_per_month[i + 1] - average_spending_per_customer_per_month[i]) / average_spending_per_customer_per_month[i]) * 100
                    spending_changes.append(spending_change)
                else:
                    spending_changes.append(0)
            average_spending_change = sum(spending_changes) / len(spending_changes) if spending_changes else 0
            return average_spending_change

        # Bootstrap resampling
        bootstrapped_spending_changes = []
        for _ in range(num_bootstraps):
            bootstrap_sample = dict()
            for partner, data in data_structure.items():
                iteration_idx = np.random.randint(0, len(data['Total Sales Per Month']))
                bootstrap_sample[partner] = {'Total Sales Per Month': [data['Total Sales Per Month'][iteration_idx]], 'Unique Customers Per Month': [data['Unique Customers Per Month'][iteration_idx]]}
            bootstrapped_spending_changes.append(calculate_average_spending_change(bootstrap_sample))

        # Calculate percentiles for confidence interval
        lower_percentile = (1 - confidence_level) / 2
        upper_percentile = 1 - lower_percentile
        lower_bound = np.percentile(bootstrapped_spending_changes, lower_percentile * 100)
        upper_bound = np.percentile(bootstrapped_spending_changes, upper_percentile * 100)
        
        # Calculate the mean of spending changes
        mean_spending_change = np.mean(bootstrapped_spending_changes)

        return mean_spending_change, lower_bound, upper_bound

    
    def calculate_npv_with_ci(partner_metrics, partner_metrics_baseline, monthly_tokens_redeemed, token_value=0.5, discount_rate=0.05, num_bootstraps=10000, confidence_level=0.90):
        partner_npv_values = {partner: [] for partner in partner_metrics.keys()}  # Initialize empty lists for each partner
        total_npv_values = []

        for _ in range(num_bootstraps):
            for partner, metrics_data in partner_metrics.items():
                npv_value_this_bootstrap = 0

                monthly_averages = metrics_data["Total Sales Per Month"]
                for month in range(12):
                    monthly_average = sum([values[month] for values in monthly_averages]) / len(monthly_averages)
                    bootstrap_monthly_average = np.random.choice(monthly_averages[month])

                    incremental_revenue = bootstrap_monthly_average
                    costs = monthly_tokens_redeemed[partner][month] * token_value
                    baseline_costs = partner_metrics_baseline[partner]["Total Sales Per Month"][month] * token_value

                    net_cash_flow = incremental_revenue - costs - baseline_costs
                    discounted_cash_flow = net_cash_flow / ((1 + discount_rate) ** (month / 12))
                    npv_value_this_bootstrap += discounted_cash_flow

                partner_npv_values[partner].append(npv_value_this_bootstrap)
                total_npv_values.append(npv_value_this_bootstrap)

        # Calculate NPV mean and CI for each partner
        partner_npv_results = {}
        for partner, npv_values in partner_npv_values.items():
            partner_npv_results[partner] = {
                "Value": sum(npv_values) / num_bootstraps,
                "Confidence Interval": np.percentile(npv_values, [5, 95])
            }

        # Calculate 90% CI for total NPV
        total_npv_ci = np.percentile(total_npv_values, [5, 95])

        # Calculate mean of total NPV
        mean_total_npv = np.mean(total_npv_values) 

        result = {
            "Total NPV": {
                "Value": mean_total_npv,
                "Confidence Interval": total_npv_ci
            },
            "Partner NPVs": partner_npv_results
        }

        return result


    def extract_monthly_tokens_redeemed(partner_metrics):
        monthly_tokens_redeemed = {}
        for partner, data in partner_metrics.items():
            monthly_tokens_redeemed[partner] = data["Tokens Redeemed Per Month"]
        return monthly_tokens_redeemed



    import numpy as np
    import matplotlib.pyplot as plt

    def bootstrap_confidence_interval(data, num_bootstraps=1000, confidence_level=0.95):
        """Calculates confidence interval for given data using bootstrapping."""
        bootstrap_samples = np.random.choice(data, size=(num_bootstraps, len(data)), replace=True)
        bootstrap_means = np.mean(bootstrap_samples, axis=1)
        lower_bound = np.percentile(bootstrap_means, (1 - confidence_level) / 2 * 100)
        upper_bound = np.percentile(bootstrap_means, (1 + confidence_level) / 2 * 100)
        return lower_bound, upper_bound

    def calculate_system_equity_new(partner_metrics,num_bootstraps=10000,confidence_level=0.9):
        partner_avg_growth = {}
        partner_avg_growth_confidence_intervals = {}
        all_bootstrapped_avg_growths = []

        # Iterate through partners
        for partner, data in partner_metrics.items():
            partner_growth_samples = []

            # Iterate through months
            for month in range(1, 12):
                monthly_growth_rates = []

                # Iterate through iterations for each partner
                for iteration_data in data['Purchases Per Month']:
                    last_month_sales = iteration_data[month - 1]
                    current_month_sales = iteration_data[month]

                    if last_month_sales > 0:
                        growth = ((current_month_sales - last_month_sales) / last_month_sales) * 100
                        monthly_growth_rates.append(growth)

                # Accumulate monthly growth rates for bootstrapping
                partner_growth_samples.extend(monthly_growth_rates)

            # Bootstrapping for partner average growth and its confidence interval
            if partner_growth_samples:
                partner_avg_growth[partner] = np.mean(partner_growth_samples)
                lower_bound, upper_bound = KPI_calcs.bootstrap_confidence_interval(partner_growth_samples,num_bootstraps=num_bootstraps,confidence_level=confidence_level)
                partner_avg_growth_confidence_intervals[partner] = (lower_bound, upper_bound)
                all_bootstrapped_avg_growths.append(partner_growth_samples)

        # Bootstrapping for overall system metrics
        overall_avg_growth_samples = np.concatenate(all_bootstrapped_avg_growths)
        overall_avg_growth = np.mean(overall_avg_growth_samples)
        overall_avg_growth_ci = KPI_calcs.bootstrap_confidence_interval(overall_avg_growth_samples,num_bootstraps=num_bootstraps,confidence_level=confidence_level)

        system_equity_samples = [sum(abs(overall_avg_growth - avg) for avg in sample) for sample in all_bootstrapped_avg_growths]
        system_equity = np.mean(system_equity_samples)/1000
        system_equity_ci = KPI_calcs.bootstrap_confidence_interval(system_equity_samples,num_bootstraps=num_bootstraps,confidence_level=confidence_level)
        system_equity_ci = tuple(bound / 1000 for bound in system_equity_ci)

        return (partner_avg_growth, partner_avg_growth_confidence_intervals), (overall_avg_growth, overall_avg_growth_ci), (system_equity, system_equity_ci)




    def calculate_total_cltv_annual(partner_metrics, discount_rate=0.05):
        total_cltv = 0
        total_customers = 0

        # Extract monthly spend values and unique customer counts for each partner and each iteration
        for partner, data in partner_metrics.items():
            for iteration in range(len(data['Total Sales Per Month'])):
                monthly_spend_values = data['Total Sales Per Month'][iteration]
                unique_customers = data['Unique Customers Per Month'][iteration]

                # Calculate total spend per customer for each month
                for month in range(len(monthly_spend_values)):
                    if unique_customers[month] > 0:
                        cltv_this_month = (monthly_spend_values[month] / unique_customers[month]) / discount_rate
                        total_cltv += cltv_this_month * unique_customers[month]
                        total_customers += unique_customers[month]

        # Calculate the average CLTV per customer
        average_cltv_per_customer = total_cltv / total_customers if total_customers > 0 else 0

        return average_cltv_per_customer




