import numpy as np
import random
import importlib
import External_Params

importlib.reload(External_Params)

import numpy as np
import random
from External_Params import EternalConext


class Model0:

    BASE_SPEND_PROBABILITY = 0.25  # 25% chance to spend without any incentives
    id_counter = 0  # Static counter for unique IDs

    def __init__(self):
        self.total_spent = 0
        self.current_month_spent = 0
        self.id = Model0.id_counter
        Model0.id_counter += 1

    def incentive_to_spend(self):

        # Introducing randomness using normal distribution
        random_component = np.random.normal(0, 0.2)

        # Total x-value for incentive curve with randomness
        x_value = 0 + random_component

        # Using your chosen incentive curve function with the calculated x-value
        # Replace with prefered incentive curve function and parameters
        multiplier = EternalConext.incentive_curve_linear(x_value, slope=0.5, max_value=2.0)

        # Calculating incentive probability
        incentive_prob = self.BASE_SPEND_PROBABILITY * multiplier

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
            # Choose a partner based on the adjusted probabilities
            partner = random.choices(list(partners.keys()), weights=partner_probabilities, k=1)[0]

            # The spend value logic remains the same
            spend_value = random.uniform(0, partners[partner]["Average Basket Value"] * 2)
            self.total_spent += spend_value
            return partner, spend_value
        return None, 0
        

    @staticmethod
    def adjust_customer_list(customers, new_count):
        current_count = len(customers)
        if new_count > current_count:
            # Add new customers
            for _ in range(new_count - current_count):
                customers.append(Model0())
        elif new_count < current_count:
            # Remove extra customers
            customers = customers[:new_count]
        return customers


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
