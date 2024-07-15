import numpy as np
import random
from External_Params import EternalConext
from Model1_Params import Model1


class Sim_12:


    
    def run_simulation(customers_count, partners):

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

            # Calculate the total number of customers for this month using the new growth function
            base_growth_rate = 0.03 + additional_growth_this_month
            customers_count_this_month = EternalConext.calculate_customer_growth(
                customers_count,
                month,
                base_growth_rate=base_growth_rate,
                diminishing_factor_min=0.90,
                diminishing_factor_max=0.99
            )

            # Add new customers if needed
            while len(initial_customers) < customers_count_this_month:
                new_customer = Model1()
                initial_customers.append(new_customer)
                # Initialize savings for new customer
                customer_savings_ST[new_customer.id] = [0] * 12

            # Record the total customer count for the month
            monthly_customer_counts.append(len(initial_customers))

            # Use 'initial_customers' as the customer list for this month's simulation
            customers = initial_customers

            for customer in customers:
                num_shops = random.randint(0, 5)
                for _ in range(num_shops):
                    # The spend function now uses Adjusted Sales Events
                    partner, spend_value = customer.spend(partners)
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