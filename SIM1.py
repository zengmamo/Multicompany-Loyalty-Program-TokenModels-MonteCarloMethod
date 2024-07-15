import numpy as np
import random
import importlib
import External_Params
import Model1_Params
import Partners

importlib.reload(External_Params)
importlib.reload(Model1_Params)
importlib.reload(Partners)

import numpy as np
import random
from External_Params import EternalConext
from Model1_Params import Model1
from Partners import PartnerData


class Sim_1:


    
    def run_simulation(customers_count, partners):

        total_customers_count = customers_count  # Initialize total customers count

        # Initialization
        initial_customers = [Model1() for _ in range(customers_count)]  # Starting number of customers

        # Initialize customer_savings_ST using customer IDs
        customer_savings_ST = {customer.id: [0] * 12 for customer in initial_customers} 

        # Initialization of other variables
        total_tokens_redeemed = {partner: 0 for partner in partners}
        wallet_values = {}

        # New list to record monthly customer counts
        monthly_customer_counts = []

        # Initialize partner metrics
        partner_metrics = {
            partner: {
                "Purchases Per Month": [0] * 12,
                "Unique Customers Per Month": [set() for _ in range(12)],
                "Total Sales Per Month": [0] * 12,
                "Average Basket Value Per Month": [0] * 12,
                "Tokens Redeemed Per Month": [0] * 12
            }
            for partner in partners
        }

        tier_distribution = {"Tier 1": 0, "Tier 2": 0, "Tier 3": 0}

        leaderboard = {}  # Initialize an empty leaderboard

        # Monthly simulation
        # Monthly simulation with competition effects
        for month in range(12):
            additional_growth_this_month = 0
            initial_customers = Model1.adjust_customer_list(initial_customers, customers_count)
            customer_savings_ST = {customer.id: customer_savings_ST.get(customer.id, [0] * 12) for customer in initial_customers}
            # Quarterly Voting for New Partners
            if month % 3 == 2:  # Every third month
                num_applications = random.randint(0, 2)
                new_partner_applications = [EternalConext.generate_new_partner_data() for _ in range(num_applications)]
                accepted_partners = Model1.conduct_vote(partners, new_partner_applications)
                for accepted_partner_data in accepted_partners:

                    # Add accepted new partner and update additional growth
                    partner_name = f"New Partner {month}"
                    partners[partner_name] = accepted_partner_data
                    # add_new_customers_based_on_partner_size function
                    all_customers, additional_customers = EternalConext.add_new_customers_based_on_partner_size(
                        Model1, initial_customers, partners, accepted_partner_data
                    )
                    total_customers_count += additional_customers  # Update the total customers count
                    # Update customer_savings_ST for each newly added customer
                    for i in range(-additional_customers, 0):
                        new_customer_id = initial_customers[i].id
                        customer_savings_ST[new_customer_id] = [0] * 12

                    # Initialize metrics for the new partner
                    partner_metrics[partner_name] = {
                        "Purchases Per Month": [0] * 12,
                        "Unique Customers Per Month": [set() for _ in range(12)],
                        "Total Sales Per Month": [0] * 12,
                        "Average Basket Value Per Month": [0] * 12,
                        "Tokens Redeemed Per Month": [0] * 12
                    }

                    # Initialize total tokens redeemed for the new partner
                    total_tokens_redeemed[partner_name] = 0

                    # Update the additional growth for this month with the new partner's size factor
                    additional_growth_this_month += accepted_partner_data['size_factor']

            # Calculate the total number of customers for this month
            customers_count_this_month = EternalConext.calculate_customer_growth(
                total_customers_count,
                month,additional_factor=additional_growth_this_month
            )

            # Add new customers if needed
            while len(initial_customers) < customers_count_this_month:
                new_customer = Model1()
                initial_customers.append(new_customer)
                # Initialize savings for new customer and update customer_savings_ST
                customer_savings_ST[new_customer.id] = [0] * 12

                # Ensure that a record for the new customer is added to customer_savings_ST
                if new_customer.id not in customer_savings_ST:
                    customer_savings_ST[new_customer.id] = [0] * 12


            # Record the total customer count for the month
            monthly_customer_counts.append(len(initial_customers))

            # Use 'initial_customers' as the customer list for this month's simulation
            customers = initial_customers

            competition_effects = EternalConext.calculate_competition_effect(partners, EternalConext.industry_competition_factor)


            for customer in customers:
                num_shops = random.randint(0, 5)
                for _ in range(num_shops):
                    # The spend function now uses Adjusted Sales Events
                    partner, spend_value = customer.spend(partners,competition_effects)
                    if partner:  
                        partner_metrics[partner]["Purchases Per Month"][month] += 1
                        partner_metrics[partner]["Unique Customers Per Month"][month].add(customer)
                        partner_metrics[partner]["Total Sales Per Month"][month] += spend_value

                        customer.earn_tokens(spend_value)
                        
                        redeemed_tokens, savings = customer.redeem_tokens()
                        if partner in partner_metrics:  # Check if partner exists in partner_metrics
                            partner_metrics[partner]["Tokens Redeemed Per Month"][month] += redeemed_tokens
                            customer_savings_ST[customer.id][month] += savings
                        total_tokens_redeemed[partner] += redeemed_tokens
                        # Store the customer's savings after they redeem tokens

                    customer.current_month_spent += spend_value
                    
                customer.update_tier()

            # Update the leaderboard at the end of the month
            for customer in customers:
                customer.update_leaderboard(leaderboard)

            # Sort the leaderboard
            sorted_leaderboard = sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)

            # Reward top customers and update their leaderboard positions
            for rank, (customer_id, score) in enumerate(sorted_leaderboard):
                customer = next(c for c in customers if c.id == customer_id)
                customer.update_leaderboard_position(rank)

                # Top 1% customers
                if rank < len(customers) * 0.01:
                    customer.tokens += 20

                # Top 10% customers
                elif rank < len(customers) * 0.10:
                    customer.tokens += 10

            # Reset leaderboard and monthly earnings for the next month
            leaderboard.clear()
            for customer in customers:
                customer.reset_monthly_earned_tokens()    

        # Customer simulation loop
        for customer in customers:
            tier_distribution[customer.tier] += 1
            wallet_values[customer.id] = customer.tokens  # Use customer ID for wallet values

        # After the monthly simulation loop
        for partner in partners:
            for month in range(12):
                num_purchases = partner_metrics[partner]["Purchases Per Month"][month]
                total_sales = partner_metrics[partner]["Total Sales Per Month"][month]
                partner_metrics[partner]["Average Basket Value Per Month"][month] = total_sales / num_purchases if num_purchases else 0
                partner_metrics[partner]["Unique Customers Per Month"][month] = len(partner_metrics[partner]["Unique Customers Per Month"][month])

        wallet_values = {customer.id: customer.tokens for customer in initial_customers}
        average_wallet_value = np.mean(list(wallet_values.values()))  # Calculate the average wallet value

        return total_tokens_redeemed, tier_distribution, partner_metrics, wallet_values, average_wallet_value, customer_savings_ST, monthly_customer_counts



