import numpy as np
import random
import importlib
import Model2_Params
import External_Params

importlib.reload(Model2_Params)
importlib.reload(External_Params)

from External_Params import EternalConext
from Model2_Params import Model2



class Sim_2:


    def run_simulation(customers_count, partners):
    # Initialization

        # Initialization
        total_customers_count = customers_count  # Initialize total customers count
        initial_customers = [Model2() for _ in range(customers_count)]  # Starting number of customers
        # New list to record monthly customer counts
        monthly_customer_counts = []

        monthly_token_circulation = []
        monthly_token_values = []  # List to store token values for each month
        monthly_token_supply = []  # List to store token supply for each month

        # Initialize a dictionary for PoS rewards
        pos_rewards = {partner: 0 for partner in partners.keys()}

       
        total_tokens_redeemed = {partner: 0 for partner in partners}
        wallet_values = {}
        customer_savings_ST = {customer.id: [0] * 12 for customer in initial_customers} # Initialize customer_savings here

        recent_spending_data = {partner: [] for partner in partners}  # Initialize recent spending data
        market_trends = {partner: 1.0 for partner in partners}  # Initialize market trends (1.0 represents no change)

        # Initialize Wallet for each partner based on their initial token buy-in
        for partner, data in partners.items():
            initial_tokens = Model2.calculate_initial_buy_in(data["Sales Events"])
            data.update({
                "Initial Tokens": initial_tokens,
                "Tokens in Circulation": True,
                "Total Sales Per Month": [0] * 12,
                "Wallet": initial_tokens,
                "Token Purchases": [[] for _ in range(12)],
                "Monthly Staked Tokens": [0] * 12,
                'Staked Tokens': 0
                })

        total_supply = sum(partner_data["Wallet"] for partner_data in partners.values())

        # Initialize partner_metrics
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

        # Monthly simulation loop
        for month in range(12):
            additional_growth_this_month = 0  # Initialize outside the monthly loop
            initial_customers = Model2.adjust_customer_list(initial_customers, customers_count)
            customer_savings_ST = {customer.id: customer_savings_ST.get(customer.id, [0] * 12) for customer in initial_customers}
            # Quarterly voting for new partners
            if month % 3 == 0:
                num_applications = random.randint(0, 2)
                new_partner_applications = [EternalConext.generate_new_partner_data() for _ in range(num_applications)]
                accepted_partners = Model2.conduct_vote(partners, new_partner_applications)

                for accepted_partner_data in accepted_partners:
                    # Add accepted new partner and update additional growth
                    partner_name = f"New Partner {month}"
                    partners[partner_name] = accepted_partner_data
                    # add_new_customers_based_on_partner_size function
                    all_customers, additional_customers = EternalConext.add_new_customers_based_on_partner_size(
                        Model2, initial_customers, partners, accepted_partner_data
                    )
                    total_customers_count += additional_customers  # Update the total customers count
                    # Update customer_savings_ST for each newly added customer
                    for i in range(-additional_customers, 0):
                        new_customer_id = initial_customers[i].id
                        customer_savings_ST[new_customer_id] = [0] * 12

                    current_token_price = Model2.TOKEN_VALUE

                    # Initialize necessary keys for the new partner
                    partners[partner_name]["Wallet"] = Model2.calculate_initial_buy_in(partners[partner_name]["Sales Events"], current_token_price)
                    partners[partner_name]["Staked Tokens"] = 0
                    partners[partner_name]["Token Purchases"] = [[] for _ in range(12)]
                    partners[partner_name]["Total Sales Per Month"] = [0] * 12
                    partners[partner_name]["Monthly Staked Tokens"] = [0] * 12
                    partners[partner_name]["Initial Tokens"] = partners[partner_name]["Wallet"]

                    # Initialize metrics for the new partner
                    partner_metrics[partner_name] = {
                        "Purchases Per Month": [0] * 12,
                        "Unique Customers Per Month": [set() for _ in range(12)],
                        "Total Sales Per Month": [0] * 12,
                        "Average Basket Value Per Month": [0] * 12,
                        "Tokens Redeemed Per Month": [0] * 12
                    }

                    # Initialize PoS rewards, recent spending data, and market trends for new partner
                    total_tokens_redeemed[partner_name] = 0
                    pos_rewards[partner_name] = 0
                    recent_spending_data[partner_name] = [] 
                    market_trends[partner_name] = 1.0  # Default value for new partner

                    # Update the additional growth for this month with the new partner's size factor
                    additional_growth_this_month += accepted_partner_data['size_factor']

            # Calculate the total number of customers for this month
            customers_count_this_month = EternalConext.calculate_customer_growth(
                total_customers_count,
                month,additional_factor=additional_growth_this_month
            )

            # Add new customers if needed
            while len(initial_customers) < customers_count_this_month:
                new_customer = Model2()
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



            # Calculate the curve shift for the current month
            curve_shift = Model2.calculate_monthly_curve_shift(month, total_supply, max_value=10, midpoint=0, asymptote_point=1000000000)
            monthly_total_spending = {partner: 0 for partner in partners}
            unique_customers_tracker = {partner: set() for partner in partners}

            transactions = []  # list of transactions that occurred in the month

            for customer in customers:
                monthly_spent = 0
                total_savings_this_month = 0
                num_shops = random.randint(0, 5)
                for _ in range(num_shops):
                    partner, spend_value = customer.spend(partners, curve_shift,competition_effects)
                    if partner:
                        # Record spending transaction
                        spending_transaction = {
                            'customer': customer,
                            'partner': partner,
                            'amount': spend_value,
                            'type': 'spend'
                        }
                        transactions.append(spending_transaction)

                        # Customer earns tokens
                        customer.earn_tokens(spend_value, partner, partners)

                        # Record partner metrics
                        partner_metrics[partner]["Purchases Per Month"][month] += 1
                        partner_metrics[partner]["Unique Customers Per Month"][month].add(customer)
                        unique_customers_tracker[partner].add(customer)
                        partner_metrics[partner]["Total Sales Per Month"][month] += spend_value

                        # Update 'Total Sales Per Month' for the partner
                        if len(partners[partner]["Total Sales Per Month"]) < month + 1:
                            partners[partner]["Total Sales Per Month"].extend([0] * (month + 1 - len(partners[partner]["Total Sales Per Month"])))
                        partners[partner]["Total Sales Per Month"][month] += spend_value

                        # Customer redeems tokens
                        # Redeeming tokens
                        redeemed_tokens, redeemed_value = customer.redeem_tokens(partner, partners)
                        if redeemed_tokens:
                            # Ensure the customer ID exists in the customer_savings_ST before updating it
                            if customer.id in customer_savings_ST:
                                customer_savings_ST[customer.id][month] += redeemed_value
                                total_tokens_redeemed[partner] += redeemed_tokens
                            else:
                                # Handle the case where the customer ID is not in the dictionary
                                customer_savings_ST[customer.id] = [0] * 12
                                customer_savings_ST[customer.id][month] = redeemed_value

                            # Update partner metrics for tokens redeemed
                            if month < len(partner_metrics[partner]["Tokens Redeemed Per Month"]):
                                partner_metrics[partner]["Tokens Redeemed Per Month"][month] += redeemed_tokens
                            else:
                                partner_metrics[partner]["Tokens Redeemed Per Month"].extend([0] * (month + 1 - len(partner_metrics[partner]["Tokens Redeemed Per Month"])))
                                partner_metrics[partner]["Tokens Redeemed Per Month"][month] += redeemed_tokens

                    customer.current_month_spent += spend_value

                customer.update_tier()
                #tier_distribution[customer.tier] += 1

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

        # After monthly simulation loop
        for partner in partners:
            for month in range(12):
                # Convert the set of unique customers to its length (count)
                total_sales = partner_metrics[partner]["Total Sales Per Month"][month]
                monthly_total_spending[partner] += partner_metrics[partner]["Total Sales Per Month"][month]
                recent_spending_data[partner].append(monthly_total_spending[partner])
                partner_metrics[partner]["Unique Customers Per Month"][month] = len(partner_metrics[partner]["Unique Customers Per Month"][month])   
                num_purchases = partner_metrics[partner]["Purchases Per Month"][month]     
                partner_metrics[partner]["Average Basket Value Per Month"][month] = total_sales / num_purchases if num_purchases else 0
                
            # Customer simulation loop
        for customer in customers:
            tier_distribution[customer.tier] += 1


            # Update token value based on the new total supply
            Model2.update_token_value(total_supply)



            # PoS validation after all transactions
            Model2.random_staking_decision(partners, 0.05, 0.2, month) 
            num_blocks = len(transactions) // 100
            for block in range(num_blocks):
                metrics = Model2.calculate_reward_metric(partners)
                total_metric = sum(metrics.values())

                # Distribute rewards
                for partner in partners.keys():
                    if total_metric > 0:
                        reward = (metrics[partner] / total_metric) * Model2.REWARD_PER_BLOCK
                        reward = max(reward, 0)  # Ensure reward is not negative
                    else:
                        reward = 0

                    partners[partner]["Wallet"] += reward
                    pos_rewards[partner] += reward  


            # Partners may buy additional tokens based on their projected demand
            total_supply = Model2.purchase_additional_tokens(partners, total_supply, recent_spending_data, market_trends, month)

            staked_tokens_this_month = sum(partner_data["Monthly Staked Tokens"][month] for partner_data in partners.values())
            total_supply -= staked_tokens_this_month
            
            # Calculate total tokens in customer and partner wallets
            total_customer_tokens = sum(customer.tokens for customer in customers)
            total_partner_tokens = sum(partner_data["Wallet"] for partner_data in partners.values())
            current_tokens_in_circulation = total_customer_tokens + total_partner_tokens
            monthly_token_circulation.append(current_tokens_in_circulation)

            monthly_token_supply.append(total_supply)

            monthly_token_values.append(Model2.TOKEN_VALUE)

            # Update token value
            Model2.update_token_value(total_supply)

            """
            # Update average basket value at the end of each month for each partner
            for partner in partners:
                total_sales = partner_metrics[partner]["Total Sales Per Month"][month]
                monthly_total_spending[partner] += partner_metrics[partner]["Total Sales Per Month"][month]
                recent_spending_data[partner].append(monthly_total_spending[partner])
                if num_purchases > 0:
                    partner_metrics[partner]["Average Basket Value Per Month"][month] = total_sales / num_purchases
            """""

            # Update unique customer counts after all transactions are done for the month
            #for partner in partners:
            #    partner_metrics[partner]["Unique Customers Per Month"][month] = partner_metrics[partner]["Unique Customers Per Month"][month]

            


        # Final aggregation of wallet values
        for customer in customers:
            wallet_values[customer] = customer.tokens  # Update wallet values for each customer

        # Final aggregation and calculation of metrics after the simulation loop
        total_wallet_value = sum(wallet_values.values())  # Calculate the total value of all wallets
        average_wallet_value = total_wallet_value / customers_count if customers_count > 0 else 0  # Calculate the average wallet value

        return total_tokens_redeemed, tier_distribution, partner_metrics, wallet_values, average_wallet_value, customer_savings_ST, pos_rewards, monthly_token_values, monthly_token_supply, monthly_token_circulation, monthly_customer_counts




