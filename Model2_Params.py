import numpy as np
import random
import importlib
import External_Params

importlib.reload(External_Params)

import numpy as np
import random
from External_Params import EternalConext


class Model2:

    # Gamification

    # To incentivize customers to transition to higher tiers, higher tiers have higher earning rates
    # For example in Tier 3 0.15 Tokens are earned per dollar spent
    tier_rates = {
        "Tier 1": 0.05,
        "Tier 2": 0.1,
        "Tier 3": 0.15
    }

    # Customers can slide into a higher tier by surpassing the accumulated spending thresholds
    tier_thresholds = {
        "Tier 2": 150,
        "Tier 3": 300
    }

    # Tier Maintenance is a gamification-mechanism that incentivizes customers to increase spending, as they may risk sliding down after one month
    # The thresholds refer to monthly spending levels within the partner network that need to be exceeded in order to remain in the tier
    tier_maintenance = {
        "Tier 2": 100,
        "Tier 3": 250
    }

    id_counter = 0  # Static counter for unique IDs

    BASE_SPEND_PROBABILITY = 0.25  # 25% chance to spend without any incentives
    TOKEN_VALUE = 0.1  # Set a default value for TOKEN_VALUE
    ISSUE_RATE = 0.01 # This means customers earn 0.01 tokens for each unit of spend

    def __init__(self):
        self.id = Model2.id_counter
        Model2.id_counter += 1
        self.tier = "Tier 1"   # Initialize each customer as Tier 1
        self.total_spent = 0   # Token spent = 0
        self.tokens = 0        # Token held = 0
        self.current_month_spent = 0      # Token spent current month = 0
        self.savings = 0   # cumulative savings
        self.monthly_spending = [0] * 12  # Initialize with 0 spending for each of the 12 months

        self.leaderboard_position = None
        self.monthly_earned_tokens = 0

    TIER_SPEND_VALUES = {
        "Tier 1": 0,   # Base x-value for Tier 1
        "Tier 2": 1,   # Base x-value for Tier 2
        "Tier 3": 2    # Base x-value for Tier 3
    }

    def update_leaderboard(self, leaderboard):
        # Logic to update the leaderboard based on this customer's performance
        # For example, it could update the leaderboard dictionary with the customer's ID and their total earned tokens
        leaderboard[self.id] = self.monthly_earned_tokens
        
    def reset_monthly_earned_tokens(self):
        self.monthly_earned_tokens = 0

    def update_leaderboard_position(self, position):
        self.leaderboard_position = position

    def update_tier(self):
        new_tier = self.tier  # Start by assuming current tier

        if self.total_spent >= Model2.tier_thresholds["Tier 3"]:
            new_tier = "Tier 3"
        elif self.total_spent >= Model2.tier_thresholds["Tier 2"]:
            new_tier = "Tier 2"
        else:
            new_tier = "Tier 1"

        # Maintenance
        if new_tier == "Tier 3" and self.current_month_spent < Model2.tier_maintenance["Tier 3"]:
            new_tier = "Tier 2"
        if new_tier == "Tier 2" and self.current_month_spent < Model2.tier_maintenance["Tier 2"]:
            new_tier = "Tier 1"

        self.tier = new_tier
        self.current_month_spent = 0

        # root-shaped Bonding Curve (default)

    max_value=10
    midpoint=0
    asymptote_point=1000000000

    def bonding_c_R(current_supply, max_value=max_value, midpoint=midpoint, asymptote_point=asymptote_point):
        # Ensure the current_supply is always greater than or equal to 0
        adjusted_supply = max(0, current_supply - midpoint)

        # The value of the token increases with the square root of the adjusted supply
        token_value = max_value * np.sqrt(adjusted_supply + 1) / np.sqrt(asymptote_point + 1)

        # Ensure that the token value does not exceed the max_value
        return min(token_value, max_value)
    
    
        # s-shaped Bonding Curve

    def bonding_c_S(x, L, k, x0):
        L = 10  # Maximum value: 1 TKN = 10€
        k = 0.001 # Arbitrary steepness value
        x0 = 50000  # Assuming midpoint is at 500 tokens for demonstration purposes
        return L / (1 + np.exp(-k * (x - x0)))
    
        # Calculate the monthly shift on the curve

    def calculate_monthly_curve_shift(current_month, total_supply, max_value=10, midpoint=0, asymptote_point=1000000000):
        # Calculate the current token value based on the new bonding curve
        current_token_value = Model2.bonding_c_R(total_supply, max_value, midpoint, asymptote_point)

        # Determine the relative position on the curve
        # For simplicity, we use the current token value divided by the max_value
        relative_position = current_token_value / max_value

        # The potential for appreciation is higher when the relative position is low
        # Using a simple linear relationship for this example: 
        # (1 - relative_position) gives higher values for lower positions on the curve
        curve_shift = (1 - relative_position) * 0.1  # Adjust the multiplier as needed

        return curve_shift
    

    @classmethod
    def update_token_value(cls, total_supply, TOKEN_VALUE=0.1):
        max_value = 10  # Maximum value: 1 TKN = 10€
        midpoint = 0  # Set the midpoint for the bonding curve
        asymptote_point = 1000000000  # Asymptotic point for the curve

        # Calculate the current token value using the new bonding curve
        calculated_value = Model2.bonding_c_R(total_supply, max_value, midpoint, asymptote_point)

        # Ensure the token value does not fall below the floor value
        cls.TOKEN_VALUE = max(calculated_value, TOKEN_VALUE)



    def incentive_to_spend(self, curve_shift):
        # Base x-value from tier
        base_x_value = self.TIER_SPEND_VALUES[self.tier]

        # Adding token-based component to x-value
        token_component = 0.01 * self.tokens

        # Token appreciation component
        # Lower position on the curve indicates higher potential for appreciation
        token_appreciation_component = (1.0 - np.exp(-self.TOKEN_VALUE) / 10.0)*0.1 # Assuming maximum token value is 10

        # Trend component based on monthly bonding curve shifts
        # Positive shift increases incentive, negative shift decreases it
        trend_component = curve_shift * 0.5   # Use the passed curve_shift value

        # Introducing randomness using normal distribution
        random_component = np.random.normal(0, 0.2)

        # Total x-value for incentive curve with randomness
        x_value = base_x_value + token_component + token_appreciation_component + trend_component + random_component

        # Using your chosen incentive curve function with the calculated x-value
        # Replace with prefered incentive curve function and parameters
        multiplier = EternalConext.incentive_curve_linear(x_value, slope=0.5, max_value=2.0)

        # Calculating incentive probability
        incentive_prob = self.BASE_SPEND_PROBABILITY * multiplier

        # Adjust incentive probability based on leaderboard position
        if self.leaderboard_position is not None:
            # Calculate rank_multiplier
            base_multiplier = 1 + (1 / (self.leaderboard_position + 1))
            random_reduction = random.uniform(0, 0.5 / (self.leaderboard_position + 1))
            rank_multiplier = min(base_multiplier - random_reduction, 2)
            
            # Apply rank_multiplier to incentive probability
            incentive_prob *= rank_multiplier

        # Ensure the probability does not exceed 1
        return min(incentive_prob, 1)

    def spend(self, partners, curve_shift, competition_effects):
        # Adjust the Sales Events for each partner based on competition
        for partner, data in partners.items():
            competition_factor = competition_effects.get(partner, 1)  # Default to 1 if not specified
            # Use Adjusted Sales Events for partner probabilities
            partner_probabilities = [((data["Sales Events"] * data["AVGSales/Month"] * data["Average Basket Value"]) * competition_factor) / 12 for _, data in partners.items()]
            total_events = sum(partner_probabilities)
            partner_probabilities = [p / total_events for p in partner_probabilities]

        should_spend = random.random() < self.incentive_to_spend(curve_shift)
        if should_spend:
            partner = random.choices(list(partners.keys()), weights=partner_probabilities, k=1)[0]
            spend_value = random.uniform(0, partners[partner]["Average Basket Value"] * 2)
            self.total_spent += spend_value
            return partner, spend_value
        return None, 0

    def earn_tokens(self, spend_value, partner, partners):
        """
        Calculates tokens earned based on spend value and ISSUE_RATE.
        """

        # Ensure that TOKEN_VALUE is the current value from the bonding curve
        current_token_value = self.TOKEN_VALUE

        earn_rate = Model2.tier_rates[self.tier]

        # Calculate tokens earned
        tokens_earned = (spend_value * earn_rate) / current_token_value

        # Update the number of tokens
        self.tokens += tokens_earned
        self.monthly_earned_tokens += spend_value * self.tier_rates[self.tier]

        partners[partner]["Wallet"] -= tokens_earned  # Deduct tokens from partner's wallet

        # Return the number of tokens earned
        return tokens_earned

    def redeem_tokens(self, partner,partners, mean_rate=0.20, std_dev=0.2):
        
        # Existing logic to calculate redeemed tokens
        sampled_rate = np.random.normal(mean_rate, std_dev)
        sampled_rate = max(0, min(1, sampled_rate))
        redeemed_tokens = self.tokens * sampled_rate
        redeemed_value = redeemed_tokens * self.TOKEN_VALUE

        # Deduct redeemed tokens from customer
        self.tokens -= redeemed_tokens

        # Add redeemed tokens back to partner's wallet
        partners[partner]["Wallet"] += redeemed_tokens

        # Return both redeemed tokens and their value
        return redeemed_tokens, redeemed_value
    
    
    def purchase_additional_tokens(partners, total_supply, recent_spending_data, market_trends, current_month, customer_growth_rate=0.07):
        for partner, data in partners.items():
            if len(recent_spending_data[partner]) > 0:
                # Calculate the dynamic threshold based on recent spending
                average_recent_spending = sum(recent_spending_data[partner]) / len(recent_spending_data[partner])
                dynamic_threshold = average_recent_spending * (1.1 + customer_growth_rate * current_month)  # 10% above average recent spending + growth factor

                # Consider market trends and seasonality
                market_trend_factor = market_trends[partner] * (1 + customer_growth_rate * current_month)  # Adjusting for customer growth

                # Token price trend consideration
                current_token_price = Model2.bonding_c_R(total_supply, Model2.max_value, Model2.midpoint, Model2.asymptote_point)
                expected_future_price = Model2.bonding_c_R(total_supply + 10000, Model2.max_value, Model2.midpoint, Model2.asymptote_point)
                price_trend_factor = expected_future_price / current_token_price

                # Introduce some randomness to the decision-making process
                random_factor = np.random.uniform(0.95, 1.05)

                # Decide if buying tokens is beneficial
                if data["Wallet"] < dynamic_threshold and price_trend_factor * random_factor > 1.001:
                    tokens_to_buy = max(0, dynamic_threshold - data["Wallet"]) * market_trend_factor
                    token_price = Model2.bonding_c_R(total_supply + tokens_to_buy, Model2.max_value, Model2.midpoint, Model2.asymptote_point)

                    # Update partner's wallet and total supply
                    data["Wallet"] += tokens_to_buy
                    total_supply += tokens_to_buy

                    # Record transaction for analysis
                    data["Token Purchases"][current_month].append((tokens_to_buy, token_price))

        return total_supply



    REWARD_PER_BLOCK = 90

    # PoS Validation
    def pos_validation(partners, transactions, reward_per_block=REWARD_PER_BLOCK):
        for transaction in transactions:
            validating_partners = random.sample(list(partners.keys()), 3)  # Select 3 random partners for validation
            for partner in validating_partners:
                partners[partner]["Wallet"] += reward_per_block / 3  # Distribute rewards evenly
        return partners

    def stake_tokens(partner_name, amount, partners):
        if amount <= partners[partner_name]["Wallet"]:
            partners[partner_name]["Staked Tokens"] += amount
            partners[partner_name]["Wallet"] -= amount

    def calculate_reward_metric(partners):
        metrics = {}
        for partner, data in partners.items():
            if data["Total Sales Per Month"]:
                current_sales = data["Total Sales Per Month"][-1]  # The last element for the current month's sales
                # Placeholder calculation for sales increase. Replace this with your actual calculation.
                previous_sales = data.get("Previous Sales", 1)  # Use 1 to avoid division by zero if previous sales data is missing
                current_sales = data["Total Sales Per Month"][-1]  # Assuming this is the current month's sales
                sales_increase = ((current_sales - previous_sales) / previous_sales) * 100 if previous_sales > 0 else 0

                # Calculate total number of tokens held (circulation + locked)
                total_tokens_held = data["Wallet"] + data.get("Staked Tokens", 0)

                # Calculate proportion of staked tokens
                proportion_staked = data.get("Staked Tokens", 0) / total_tokens_held if total_tokens_held > 0 else 0

                # Calculate the weighted metric
                metric = 0.2 * sales_increase + 0.4 * total_tokens_held + 0.4 * proportion_staked
                metrics[partner] = metric
            
            else:
                current_sales = 0  # Default to 0 if no sales data is available

        return metrics


    def stake_tokens(partner_name, percentage, partners, month):
        if "Staked Tokens" not in partners[partner_name]:
            partners[partner_name]["Staked Tokens"] = 0  # Initialize if not present
        tokens_to_stake = partners[partner_name]["Wallet"] * percentage
        partners[partner_name]["Staked Tokens"] += tokens_to_stake
        partners[partner_name]["Wallet"] -= tokens_to_stake
        # Record the staked tokens for the current month
        partners[partner_name]["Monthly Staked Tokens"][month] = tokens_to_stake
        return tokens_to_stake  # Return the amount of tokens staked


    def random_staking_decision(partners, min_percentage, max_percentage, month):
        for partner in partners:
            stake_percentage = random.uniform(min_percentage, max_percentage)
            Model2.stake_tokens(partner, stake_percentage, partners, month)


    def conduct_vote(existing_partners, new_partner_applications):
        accepted_partners = []

        for new_partner_data in new_partner_applications:
            # Counting the number of yes votes
            yes_votes = 0
            total_votes = len(existing_partners) + 1  # Including the third party

            # Votes from existing partners
            for _ in existing_partners:
                vote = random.choice([True, False])  # Random vote for each partner
                if vote:
                    yes_votes += 1

            # Third-party vote
            third_party_vote = random.choice([True, False])
            if third_party_vote:
                yes_votes += 1

            # Determine if the new partner is accepted
            if yes_votes > total_votes / 2:
                accepted_partners.append(new_partner_data)

        return accepted_partners
    
    
    def calculate_initial_buy_in(sales_events, current_token_price=0.1, min_monetary_buy_in=1000):
        # Introduce additional randomness factor
        randomness_factor = np.random.uniform(0.8, 1.2)

        # Adjusted parameters to set a minimum monetary buy-in value
        m = 0.5 * randomness_factor  # Adjusted slope with randomness
        c = min_monetary_buy_in * randomness_factor  # Minimum monetary value with randomness

        # Calculate the monetary buy-in based on sales events
        monetary_buy_in = m * (sales_events/6) + c

        # Add more randomness using normal distribution
        mu = monetary_buy_in
        sigma = 2000  # Increased variability
        random_monetary_buy_in = np.random.normal(mu, sigma)

        # Ensure the final buy-in money value is at least the minimum
        final_monetary_buy_in = max(c, int(random_monetary_buy_in))

        # Convert monetary value to number of tokens based on current price
        tokens_to_buy = final_monetary_buy_in / current_token_price

        return max(int(tokens_to_buy), 5000)  # Ensure at least 5000 tokens as minimum


    @staticmethod
    def initialize_new_partner(partner_data):
       # Use the default current token price or specify if different
        initial_tokens = Model2.calculate_initial_buy_in(partner_data["Sales Events"], Model2.TOKEN_VALUE)

        return {
            "Initial Tokens": initial_tokens,
            "Wallet": initial_tokens,
            "Staked Tokens": 0,
            "Total Tokens Held": initial_tokens,
            "Total Sales Per Month": [0] * 12,
            "Token Purchases": [[] for _ in range(12)],
            "Monthly Staked Tokens": [0] * 12,
            "Sales Events": partner_data["Sales Events"],  # Add Sales Events
            "Average Basket Value": partner_data["Average Basket Value"],  # Add Average Basket Value
            "Industry": partner_data["Industry"],  # Add Industry
            # Add other necessary fields from partner_data if required
        }
  
    @staticmethod
    def adjust_customer_list(customers, new_count):
        current_count = len(customers)
        if new_count > current_count:
            # Add new customers
            for _ in range(new_count - current_count):
                customers.append(Model2())
        elif new_count < current_count:
            # Remove extra customers
            customers = customers[:new_count]
        return customers