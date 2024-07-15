# Import packages
import random
import numpy as np

class EternalConext:
    
    # Incentive Curves

    # Define function for s-shaped incentive curve
    def incentive_curve_sigmoid(x, max_value, midpoint):
        # Curve starts at 1 when x is 0
        base_adjustment = 1 - (max_value / (1 + np.exp(0.1 * midpoint)))
        return max_value / (1 + np.exp(-0.1 * (x - midpoint))) + base_adjustment

    def incentive_curve_linear(x, max_value, slope):
        # Linear function starting at 1 when x is 0
        return max(min(slope * x + 1, max_value), 1)

    def incentive_curve_root(x, max_value, midpoint):
        # Adjust the curve to start at 1
        base_adjustment = 1 - (max_value * np.sqrt(1 - midpoint) / np.sqrt(max_value + 1))
        return max(max_value * np.sqrt((x - midpoint) + 1) / np.sqrt(max_value + 1) + base_adjustment, 1)
    
    # Account for competition effects

    def calculate_competition_effect(partners, industry_competition_factor, randomness_scale=0.05):
        industry_counts = {}
        competition_effects = {}

        # Count the number of partners in each industry
        for partner, data in partners.items():
            industry = data["Industry"]
            industry_counts[industry] = industry_counts.get(industry, 0) + 1

        # Calculate competition effect for each partner
        for partner, data in partners.items():
            industry = data["Industry"]
            # The more competitors, the stronger the negative effect
            base_competition_effect = 1 - (industry_counts[industry] - 1) * industry_competition_factor
            
            # Add randomness to the competition effect
            random_adjustment = np.random.uniform(-randomness_scale, randomness_scale)
            competition_effect_with_randomness = base_competition_effect + random_adjustment

            # Ensure it doesn't go negative or exceed 1
            competition_effect_with_randomness = max(0, min(competition_effect_with_randomness, 1))

            competition_effects[partner] = competition_effect_with_randomness

        return competition_effects
    
    industry_competition_factor = 0.05  # Example value
    
    # Random New Partner Entries

    @staticmethod
    def generate_new_partner_data():
        # Simulate the generation of new partner data
        simulated_sales = random.randint(1000, 30000)  # Random sales between 1,000 and 100,000
        average_basket_value = random.randint(5, 500)   # Random average basket value between 5 and 500

        # Example: Using a power function to reduce the frequency of hitting the ceiling
        # Calculate the size factor based on sales and average basket value with more variability
        # Introduce a power function and a randomness factor
        randomness_factor = random.uniform(0.01, 0.1)  # Random factor 
        size_factor = (((simulated_sales / 100000) ** 0.5 + (average_basket_value / 500) ** 0.5) / 2) * randomness_factor


        # Ensuring the size factor doesn't exceed the maximum limit of 20%
        max_size_factor = 0.2
        size_factor = min(size_factor, max_size_factor)

        # Generate "AVGSales/Month" inversely related to "Average Basket Value"
        inverse_relation_factor = 40 / average_basket_value  # Inversely relate to Average Basket Value
        avg_sales_per_month = random.uniform(1, 8) * inverse_relation_factor
        avg_sales_per_month = min(avg_sales_per_month, 8)  # Ensure it doesn't exceed the upper limit

        return {
                "Sales Events": simulated_sales,
                "Average Basket Value": average_basket_value,
                "Industry": random.randint(1, 5),
                "AVGSales/Month": avg_sales_per_month,
                "Conversion Rate to Central": random.uniform(0.4, 1),
                "size_factor": size_factor  
            }
    
    # Monthly Network Growth Rate

    def calculate_customer_growth(initial_customer_count, month, base_growth_rate=0.03, diminishing_factor_min=0.90, diminishing_factor_max=0.99, additional_factor = 0.0):
        """
        Calculate the number of customers for the current month with diminishing and random growth.

        :param initial_customer_count: The initial number of customers.
        :param month: The current month in the simulation.
        :param base_growth_rate: The base monthly growth rate.
        :param diminishing_factor_min: The minimum value for the random diminishing factor.
        :param diminishing_factor_max: The maximum value for the random diminishing factor.
        :return: The calculated number of customers for the current month.
        """
        current_growth_rate = base_growth_rate + additional_factor
        total_growth = 0

        # Apply diminishing and random growth rate for each month
        for m in range(1, month + 1):
            total_growth += current_growth_rate
            random_diminishing_factor = random.uniform(diminishing_factor_min, diminishing_factor_max)
            current_growth_rate *= random_diminishing_factor

        additional_customers = initial_customer_count * total_growth
        return initial_customer_count + int(additional_customers)
    

    def add_new_customers_based_on_partner_size(Model, customers, partners, new_partner_data):
        # Calculate total sales value of existing partners
        total_sales_value = sum(data["Sales Events"] * data["Average Basket Value"] for data in partners.values())

        # Calculate sales value of new partner
        new_partner_sales_value = new_partner_data["Sales Events"] * new_partner_data["Average Basket Value"]

        # Calculate relative size of new partner
        if total_sales_value > 0:  # Avoid division by zero
            relative_size = new_partner_sales_value / total_sales_value
        else:
            relative_size = 1  # If there are no existing partners, treat the new partner as having full relative size

        # Determine the number of new customers to add
        current_total_customer_count = len(customers)
        new_customers_to_add = int(current_total_customer_count * relative_size)

        # Add new customers
        for _ in range(new_customers_to_add):
            customers.append(Model())

        # Return both the updated customers list and the number of new customers added
        return customers, new_customers_to_add


