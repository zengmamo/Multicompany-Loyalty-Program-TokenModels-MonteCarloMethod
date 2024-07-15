import numpy as np
import random
import importlib
import Model3_Params
import External_Params

importlib.reload(Model3_Params)
importlib.reload(External_Params)

from External_Params import EternalConext
from Model3_Params import Model3


class Sim_3:

    
    def run_simulation(customers_count, partners):

        # Initialization
        total_customers_count = customers_count  # Initialize total customers count
        initial_customers = [Model3() for _ in range(customers_count)]  # Starting number of customers
        # New list to record monthly customer counts
        monthly_customer_counts = []

        total_tokens_redeemed = {partner: 0 for partner in partners}
        wallet_values = {}
        customer_savings_ST = {customer.id: [0] * 12 for customer in initial_customers} # Initialize customer_savings here

        

        central_token_value = Model3.BASELINE_TOKEN_VALUE
        # New list to store the monthly value of the central token
        monthly_central_token_values = []
        
        # Add partner coins and conversion rates
        for partner in partners:
            partners[partner]['Coin'] = f"{partner} Coin"
            partners[partner]['Conversion Rate to Central'] = random.uniform(0.4, 1)  # Different conversion rates

        token_spending_metrics = {
            partner: {
                "Partner Tokens Spent Per Month": [0] * 12,
                "Central Tokens Spent Per Month": [0] * 12
            } for partner in partners
        }

        partner_metrics = {
            partner: {
                "Purchases Per Month": [0] * 12,
                "Unique Customers Per Month": [set() for _ in range(12)],
                "Total Sales Per Month": [0] * 12,
                "Average Basket Value Per Month": [0] * 12,
                "Tokens Redeemed Per Month": [0] * 12  # New key for monthly token redemptions
            }
            for partner in partners
        }

        tier_distribution = {"Tier 1": 0, "Tier 2": 0, "Tier 3": 0}

        leaderboard = {}  # Initialize an empty leaderboard   

            # Monthly simulation
        for month in range(12):
            additional_growth_this_month = 0  # Initialize outside the monthly loop
            initial_customers = Model3.adjust_customer_list(initial_customers, customers_count)
            customer_savings_ST = {customer.id: customer_savings_ST.get(customer.id, [0] * 12) for customer in initial_customers}
            # Update Central Token Value
            central_token_value = Model3.simulate_token_value_change(central_token_value, Model3.ANNUALIZED_VOL, Model3.ANNUALIZED_RET)
            # Store the updated value of the central token for this month
            monthly_central_token_values.append(central_token_value)

            # Quarterly voting with random new partner applications
            if month % 3 == 0:
                num_applications = random.randint(0, 2)
                new_partner_applications = [EternalConext.generate_new_partner_data() for _ in range(num_applications)]
                accepted_partners = Model3.conduct_vote(partners, new_partner_applications)

                for accepted_partner_data in accepted_partners:
                    # Add accepted new partner and update additional growth
                    partner_name = f"New Partner {month}"
                    partners[partner_name] = accepted_partner_data
                    # add_new_customers_based_on_partner_size function
                    all_customers, additional_customers = EternalConext.add_new_customers_based_on_partner_size(
                        Model3, initial_customers, partners, accepted_partner_data
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

                    # Initialize token spending metrics for the new partner
                    token_spending_metrics[partner_name] = {
                        "Partner Tokens Spent Per Month": [0] * 12,
                        "Central Tokens Spent Per Month": [0] * 12
                    }

                    # Initialize total tokens redeemed for the new partner
                    total_tokens_redeemed[partner_name] = 0

                    # Update the additional growth for this month with the new partner's size factor
                    additional_growth_this_month += accepted_partner_data['size_factor']

            # Calculate the total number of customers for this month
            customers_count_this_month = EternalConext.calculate_customer_growth(
                total_customers_count,
                month, additional_factor=additional_growth_this_month
            )

            # Add new customers if needed
            while len(initial_customers) < customers_count_this_month:
                new_customer = Model3()
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
                # Initialize variables for each customer
                monthly_spent = 0
                total_savings_this_month = 0
                customer.tokens = {partner: 0 for partner in partners}
                customer.tokens['Central'] = 0
                for _ in range(random.randint(0, 5)):
                    # The spend function now uses Adjusted Sales Events
                    partner, spend_value = customer.spend(partners, central_token_value,competition_effects)
                    if partner:  
                        partner_metrics[partner]["Purchases Per Month"][month] += 1
                        partner_metrics[partner]["Unique Customers Per Month"][month].add(customer)
                        partner_metrics[partner]["Total Sales Per Month"][month] += spend_value

                        customer.earn_partner_tokens(spend_value, partner)
                        
                        redeemed_tokens, savings = customer.redeem_tokens(partner,central_token_value)
                        if partner in partner_metrics:
                            partner_metrics[partner]["Tokens Redeemed Per Month"][month] += redeemed_tokens
                        customer_savings_ST[customer.id][month] += savings  # Use customer.id as the key
                        total_tokens_redeemed[partner] += redeemed_tokens
                        monthly_spent += spend_value
                        # Store the customer's savings after they redeem tokens

                # Update savings and spending for the customer
                if customer.id in customer_savings_ST:  # Ensure customer ID exists in dictionary
                    customer_savings_ST[customer.id][month] += total_savings_this_month
                else:
                    print(f"Error: Customer ID {customer.id} not found in savings tracker")

                for partner in partners:
                    # Initialize the conversion amount to zero for each partner
                    central_token_amount = 0
                    if customer.tokens[partner] > 0:
                        # Adjust conversion rate based on current token value
                        adjusted_conversion_rate = Model3.adjust_conversion_rate(partners[partner]["Conversion Rate to Central"], central_token_value)
                        
                        # Calculate the amount of Partner Tokens to convert to Central Tokens
                        partner_token_value = Model3.TOKEN_VALUE  # Assuming a predefined value per Partner Token
                        central_token_amount = Model3.convert_to_central_tokens(
                            customer.tokens[partner], 
                            partner_token_value, 
                            adjusted_conversion_rate, 
                            central_token_value
                        )

                # Perform the conversion
                customer.convert_tokens(central_token_amount, partner, 'Central', partners)

                total_savings_this_month = 0  # Track total savings for the month    
                # Loop through each token type for redemption
                for token_type in customer.tokens:
                    if customer.tokens[token_type] > 0:
                        # Redeem tokens and accumulate savings
                        redeemed_tokens, savings = customer.redeem_tokens(token_type, central_token_value)
                        # Update metrics for the spent tokens
                        if token_type == 'Central':
                            chosen_partner = random.choice(list(partners.keys()))
                            token_spending_metrics[chosen_partner]["Central Tokens Spent Per Month"][month] += redeemed_tokens
                        else:
                            token_spending_metrics[token_type]["Partner Tokens Spent Per Month"][month] += redeemed_tokens
                    else:
                        # Initialize savings to 0 if no tokens of this type
                        savings = 0

                    # Accumulate total savings for this customer this month
                    total_savings_this_month += savings

                # Update savings and spending for the customer
                customer_savings_ST[customer.id][month] += total_savings_this_month
                customer.current_month_spent += monthly_spent
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
                    customer.tokens['Central'] += 20

                # Top 10% customers
                elif rank < len(customers) * 0.10:
                    customer.tokens['Central'] += 10

            # Reset leaderboard and monthly earnings for the next month
            leaderboard.clear()
            for customer in customers:
                customer.reset_monthly_earned_tokens()    
                    
                
        # Customer simulation loop
        for customer in customers:
            tier_distribution[customer.tier] += 1

        # After the monthly simulation loop
        for partner in partners:
            for month in range(12):
                num_purchases = partner_metrics[partner]["Purchases Per Month"][month]
                total_sales = partner_metrics[partner]["Total Sales Per Month"][month]
                partner_metrics[partner]["Average Basket Value Per Month"][month] = total_sales / num_purchases if num_purchases else 0
                partner_metrics[partner]["Unique Customers Per Month"][month] = len(partner_metrics[partner]["Unique Customers Per Month"][month])
                

        wallet_values = {customer: sum(customer.tokens.values()) for customer in customers}
        average_wallet_value = np.mean(list(wallet_values.values()))  # Calculate the average wallet value

        return total_tokens_redeemed, tier_distribution, partner_metrics, wallet_values, average_wallet_value, customer_savings_ST, token_spending_metrics, monthly_customer_counts, monthly_central_token_values



