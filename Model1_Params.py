import numpy as np
import random
import importlib
import External_Params
import Partners

importlib.reload(External_Params)
importlib.reload(Partners)

import numpy as np
import random
from External_Params import EternalConext
from Partners import PartnerData



class Model1:


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
        self.tier = "Tier 1"   # Initialize each customer as Tier 1
        self.total_spent = 0   # Token spent = 0
        self.tokens = 0        # Token held = 0
        self.current_month_spent = 0      # Token spent current month = 0
        self.savings = 0   # cumulative savings
        self.id = Model1.id_counter
        Model1.id_counter += 1

        self.leaderboard_position = None
        self.monthly_earned_tokens = 0

    TOKEN_VALUE = 0.5  # e.g., each token is worth 0.5€

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

    def incentive_to_spend(self):
        # Base x-value from tier
        base_x_value = self.TIER_SPEND_VALUES[self.tier]

        # Adding token-based component to x-value
        token_component = 0.01 * self.tokens

        # Introducing randomness using normal distribution
        random_component = np.random.normal(0, 0.2)

        # Total x-value for incentive curve with randomness
        x_value = base_x_value + token_component + random_component

        # Using your chosen incentive curve function with the calculated x-value
        # Replace with prefered incentive curve function and parameters
        multiplier = EternalConext.incentive_curve_linear(x_value, slope=0.5, max_value=2.0)

        # Calculating base incentive probability
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


    def spend(self, partners, competition_effects):

        # Adjust the Sales Events for each partner based on competition
        for partner, data in partners.items():
            competition_factor = competition_effects.get(partner, 1)  # Default to 1 if not specified
            # Use Adjusted Sales Events for partner probabilities
            partner_probabilities = [((data["Sales Events"] * data["AVGSales/Month"] * data["Average Basket Value"]) * competition_factor) / 12 for _, data in partners.items()]
            total_events = sum(partner_probabilities)
            partner_probabilities = [p / total_events for p in partner_probabilities]
            
            should_spend = random.random() < self.incentive_to_spend()
            if should_spend:
                partner = random.choices(list(partners.keys()), weights=partner_probabilities, k=1)[0]
                spend_value = random.uniform(0, partners[partner]["Average Basket Value"] * 2)
                self.total_spent += spend_value
                return partner, spend_value
            return None, 0


    def earn_tokens(self, spend_value):
        earn_rate = Model1.tier_rates[self.tier]
        self.tokens += spend_value * earn_rate
        self.monthly_earned_tokens += spend_value * self.tier_rates[self.tier]

    def update_tier(self):
        new_tier = self.tier  # Start by assuming current tier

        if self.total_spent >= Model1.tier_thresholds["Tier 3"]:
            new_tier = "Tier 3"
        elif self.total_spent >= Model1.tier_thresholds["Tier 2"]:
            new_tier = "Tier 2"
        else:
            new_tier = "Tier 1"

        # Maintenance
        if new_tier == "Tier 3" and self.current_month_spent < Model1.tier_maintenance["Tier 3"]:
            new_tier = "Tier 2"
        if new_tier == "Tier 2" and self.current_month_spent < Model1.tier_maintenance["Tier 2"]:
            new_tier = "Tier 1"

        self.tier = new_tier
        self.current_month_spent = 0

    def redeem_tokens(self, mean_rate=0.20, std_dev=0.2):
        # Sample from a normal distribution with the given mean and standard deviation
        sampled_rate = np.random.normal(mean_rate, std_dev)
        
        # Ensure the rate is within the range [0, 1]
        sampled_rate = max(0, min(1, sampled_rate))
        
        redeemed_tokens = self.tokens * sampled_rate
        redeemed_value = redeemed_tokens * self.TOKEN_VALUE  # Calculate the monetary value of redeemed tokens

        self.tokens -= redeemed_tokens
        
        # Return both redeemed tokens and the monetary savings from redemption
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
    
    @staticmethod
    def adjust_customer_list(customers, new_count):
        current_count = len(customers)
        if new_count > current_count:
            # Add new customers
            for _ in range(new_count - current_count):
                customers.append(Model1())
        elif new_count < current_count:
            # Remove extra customers
            customers = customers[:new_count]
        return customers
    