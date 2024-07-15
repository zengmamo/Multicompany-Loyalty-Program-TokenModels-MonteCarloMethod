import numpy as np
import random
import importlib
import External_Params

importlib.reload(External_Params)

import numpy as np
import random
from External_Params import EternalConext

class Model3:


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

    def __init__(self):
        self.id = Model3.id_counter
        Model3.id_counter += 1
        self.tier = "Tier 1"   # Initialize each customer as Tier 1
        self.total_spent = 0   # Total spent = 0
        self.tokens = {}       # Initialize tokens as an empty dictionary
        self.current_month_spent = 0      # Token spent current month = 0
        self.savings = 0   # cumulative savings

        self.leaderboard_position = None
        self.monthly_earned_tokens = 0


    TOKEN_VALUE = 0.5  # e.g., each token is worth 0.5€

    previous_central_token_value = TOKEN_VALUE

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

    
    def calculate_token_value_change_percentage(current_value, previous_value):
        if previous_value == 0:
            return 0
        return (current_value - previous_value) / previous_value



    def incentive_to_spend(self,current_central_token_value):
        # Base x-value from tier
        base_x_value = self.TIER_SPEND_VALUES[self.tier]

        # Calculate the trend component based on the percentage change
        token_value_change_percentage = Model3.calculate_token_value_change_percentage(
            current_central_token_value, 
            Model3.previous_central_token_value
        )
        
        # Trend component is proportional to the percentage change in token value
        trend_component = token_value_change_percentage * 0.1  # Define this factor according to desired sensitivity


        total_tokens = sum(self.tokens.values())
        # Adding token-based component to x-value
        token_component = 1 * total_tokens

        # Introducing randomness using normal distribution
        random_component = np.random.normal(0, 0.2)

        # Total x-value for incentive curve with randomness
        x_value = base_x_value + token_component + random_component + trend_component

        # Using your chosen incentive curve function with the calculated x-value
        # Replace with prefered incentive curve function and parameters
        multiplier = EternalConext.incentive_curve_linear(x_value, slope=0.5, max_value=2.0)

        # Calculating incentive probability
        incentive_prob = self.BASE_SPEND_PROBABILITY * multiplier

        # Ensure the probability does not exceed 1
        return min(incentive_prob, 1)

    def spend(self, partners, current_central_token_value, competition_effects):
       # Adjust the Sales Events for each partner based on competition
        for partner, data in partners.items():
            competition_factor = competition_effects.get(partner, 1)  # Default to 1 if not specified
            # Use Adjusted Sales Events for partner probabilities
            partner_probabilities = [((data["Sales Events"] * data["AVGSales/Month"] * data["Average Basket Value"]) * competition_factor) / 12 for _, data in partners.items()]
            total_events = sum(partner_probabilities)
            partner_probabilities = [p / total_events for p in partner_probabilities]
        
        should_spend = random.random() < self.incentive_to_spend(current_central_token_value)
        if should_spend:
            partner = random.choices(list(partners.keys()), weights=partner_probabilities, k=1)[0]
            spend_value = random.uniform(0, partners[partner]["Average Basket Value"] * 2)
            self.total_spent += spend_value
            return partner, spend_value
        return None, 0
    
    def earn_partner_tokens(self, spend_value, partner):
        earn_rate = Model3.tier_rates[self.tier]
        earned_tokens = spend_value * earn_rate
        self.tokens[partner] = self.tokens.get(partner, 0) + earned_tokens
        self.monthly_earned_tokens += earned_tokens  # Update total earned tokens from all partners


    # Function to handle conversions from partner coins to central coin -- uses pre-agreed conversion rates
    def convert_coins(amount, from_partner, to_partner, partners):
        if to_partner == 'Central':
            rate = partners[from_partner]['Conversion Rate to Central']
            return amount * rate
        elif from_partner == 'Central':
            rate = partners[to_partner]['Conversion Rate to Central']
            return amount / rate
        else:
            # Conversion through central coin as intermediary
            to_central = amount * partners[from_partner]['Conversion Rate to Central']
            return to_central / partners[to_partner]['Conversion Rate to Central']

    # New method to convert tokens between partners or to/from central coin
    def convert_tokens(self, amount, from_partner, to_partner, partners):
        converted_amount = Model3.convert_coins(amount, from_partner, to_partner, partners)
        self.tokens[from_partner] -= amount
        self.tokens[to_partner] += converted_amount


    def update_tier(self):
        new_tier = self.tier  # Start by assuming current tier

        if self.total_spent >= Model3.tier_thresholds["Tier 3"]:
            new_tier = "Tier 3"
        elif self.total_spent >= Model3.tier_thresholds["Tier 2"]:
            new_tier = "Tier 2"
        else:
            new_tier = "Tier 1"

        # Maintenance
        if new_tier == "Tier 3" and self.current_month_spent < Model3.tier_maintenance["Tier 3"]:
            new_tier = "Tier 2"
        if new_tier == "Tier 2" and self.current_month_spent < Model3.tier_maintenance["Tier 2"]:
            new_tier = "Tier 1"

        self.tier = new_tier
        self.current_month_spent = 0

    def redeem_tokens(self, token_type, current_central_value):
        if token_type not in self.tokens:
            return 0, 0  # Token type does not exist

        # Sample rate for redemption
        sampled_rate = np.random.normal(0.20, 0.2)
        sampled_rate = max(0, min(1, sampled_rate))

        # Redeem tokens
        redeemed_tokens = self.tokens[token_type] * sampled_rate

        # Calculate redeemed value based on token type
        if token_type == 'Central':
            redeemed_value = redeemed_tokens * current_central_value
        else:
            redeemed_value = redeemed_tokens * self.TOKEN_VALUE

        # Subtract redeemed tokens
        self.tokens[token_type] -= redeemed_tokens

        return redeemed_tokens, redeemed_value



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


        # Constants for central token (Ethereum proxy)
    ANNUALIZED_VOL = 0.233
    ANNUALIZED_RET = 0.298

    # Function to simulate the monthly change in token value
    def simulate_token_value_change(current_value, annualized_vol, annualized_ret):
        monthly_ret = (1 + annualized_ret)**(1/12) - 1
        monthly_vol = annualized_vol / np.sqrt(12)
        return current_value * np.exp(np.random.normal(monthly_ret, monthly_vol))

    BASELINE_TOKEN_VALUE = 0.5  # Initial value of the central token

    # Function to adjust conversion rates
    def adjust_conversion_rate(partner_conversion_rate, central_token_value):
        adjusted_rate = partner_conversion_rate * (Model3.BASELINE_TOKEN_VALUE / central_token_value)
        return adjusted_rate
    
    
    def convert_to_central_tokens(partner_token_amount, partner_token_value, conversion_rate, central_token_value):
        """
        Convert Partner Tokens to Central Tokens based on their monetary value and conversion rate.

        :param partner_token_amount: Amount of Partner Tokens to convert.
        :param partner_token_value: Monetary value of one Partner Token.
        :param conversion_rate: Conversion rate from Partner Tokens to Central Tokens.
        :param central_token_value: Current value of one Central Token.
        :return: Amount of Central Tokens after conversion.
        """
        # Calculate the total monetary value of Partner Tokens
        total_monetary_value = partner_token_amount * partner_token_value

        # Apply conversion rate to get the eligible monetary value for Central Tokens
        eligible_monetary_value = total_monetary_value * conversion_rate

        # Convert the eligible monetary value to Central Tokens
        central_token_amount = eligible_monetary_value / central_token_value

        return central_token_amount
    
    @staticmethod
    def adjust_customer_list(customers, new_count):
        current_count = len(customers)
        if new_count > current_count:
            # Add new customers
            for _ in range(new_count - current_count):
                customers.append(Model3())
        elif new_count < current_count:
            # Remove extra customers
            customers = customers[:new_count]
        return customers

