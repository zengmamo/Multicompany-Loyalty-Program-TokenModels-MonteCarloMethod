import numpy as np
import random
import importlib
import External_Params
import Baseline_Params
import Partners

importlib.reload(External_Params)
importlib.reload(Baseline_Params)

from External_Params import EternalConext
from Baseline_Params import Model0


class Sim_0:


    def run_baseline(customers_count, partners):

        # Initialization
        initial_customers = [Model0() for _ in range(customers_count)]  # Starting number of customers

        # New list to record monthly customer counts
        monthly_customer_counts = []

        total_customers_count = customers_count  # Initialize total customers count
            
        partner_metrics_baseline = {
            partner: {
                "Purchases Per Month": [0] * 12,
                "Unique Customers Per Month": [set() for _ in range(12)],
                "Total Sales Per Month": [0] * 12,
                "Average Basket Value Per Month": [0] * 12  # Include this key
            }
            for partner in partners
        }

        
        # Reset or initialize your customers and other variables if necessary
        # customers_baseline = [Model0() for _ in range(customers_count)]
        # partner_metrics_baseline = {partner: {"Purchases Per Month": [0] * 12, "Unique Customers Per Month": [set() for _ in range(12)], "Total Sales Per Month": [0] * 12} for partner in partners}


        for month in range(12):
            additional_growth_this_month = 0
            initial_customers = Model0.adjust_customer_list(initial_customers, total_customers_count)
            # Quarterly Voting for New Partners
            if month % 3 == 2:
                num_applications = random.randint(0, 2)
                new_partner_applications = [EternalConext.generate_new_partner_data() for _ in range(num_applications)]
                accepted_partners = Model0.conduct_vote(partners, new_partner_applications)
                for accepted_partner_data in accepted_partners:
                    partner_name = f"New Partner {month}"
                    partners[partner_name] = accepted_partner_data

                    # Add new customers based on the relative size of the new partner
                    all_customers, additional_customers = EternalConext.add_new_customers_based_on_partner_size(
                        Model0, initial_customers, partners, accepted_partner_data
                    )
                    total_customers_count += additional_customers

                    for i in range(-additional_customers, 0):
                        initial_customers[i].id

                    # Initialize metrics for the new partner
                    partner_metrics_baseline[partner_name] = {
                        "Purchases Per Month": [0] * 12,
                        "Unique Customers Per Month": [set() for _ in range(12)],
                        "Total Sales Per Month": [0] * 12,
                        "Average Basket Value Per Month": [0] * 12,
                    }

                    # Update the additional growth for this month with the new partner's size factor
                    additional_growth_this_month += accepted_partner_data['size_factor']

            # Calculate the total number of customers for this month
            customers_count_this_month = EternalConext.calculate_customer_growth(
                total_customers_count,
                month,additional_factor=additional_growth_this_month
            )

            # Add new customers if needed
            while len(initial_customers) < customers_count_this_month:
                new_customer = Model0()
                initial_customers.append(new_customer)
                #total_customers_count += 1

            # Record the customer count for this month
            monthly_customer_counts.append(len(initial_customers))

            competition_effects = EternalConext.calculate_competition_effect(partners, EternalConext.industry_competition_factor)

            # Use 'initial_customers' as the customer list for this month's simulation
            customers = initial_customers
            for customer in customers:
                num_shops = random.randint(0, 5)
                for _ in range(num_shops):
                    partner, spend_value = customer.spend(partners,competition_effects)
                    if partner:
                        partner_metrics_baseline[partner]["Purchases Per Month"][month] += 1
                        partner_metrics_baseline[partner]["Unique Customers Per Month"][month].add(customer)
                        partner_metrics_baseline[partner]["Total Sales Per Month"][month] += spend_value


        # Calculate average basket value

        for partner in partners:
            for month in range(12):
                unique_customers_count = len(partner_metrics_baseline[partner]["Unique Customers Per Month"][month])
                partner_metrics_baseline[partner]["Unique Customers Per Month"][month] = unique_customers_count

                num_purchases = partner_metrics_baseline[partner]["Purchases Per Month"][month]
                total_sales = partner_metrics_baseline[partner]["Total Sales Per Month"][month]
                partner_metrics_baseline[partner]["Average Basket Value Per Month"][month] = total_sales / num_purchases if num_purchases else 0

        # return baseline_partner_metrics
        return partner_metrics_baseline, monthly_customer_counts


    
