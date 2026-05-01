import random

def calculate_emission(distance_km):
    # Average CO2 emission (kg per km for a car)
    emission_factor = 0.12  
    carbon = distance_km * emission_factor
    return round(carbon, 3)

def calculate_savings(actual_carbon, mode):
    """Calculates CO2 savings if the mode is micro-hub."""
    if mode == "micro-hub":
        # Simulation: Hub-optimized trips save roughly 60% emissions 
        # compared to a direct trip from a central warehouse.
        estimated_standard_carbon = actual_carbon / 0.4 
        savings = estimated_standard_carbon - actual_carbon
        return round(savings, 3)
    return 0.0

def get_agent_eco_stats(orders):
    """Processes all delivered orders to generate dashboard stats."""
    total_carbon = 0.0
    total_savings = 0.0
    
    for o in orders:
        carbon = float(o.get('carbon_kg', 0) or 0)
        mode = o.get('mode', 'direct')
        total_carbon += carbon
        total_savings += calculate_savings(carbon, mode)
        
    # 1 tree absorbs roughly 21kg of CO2 per year
    trees_planted = round(total_savings / 21, 2)
    
    return {
        "total_carbon": round(total_carbon, 3),
        "total_savings": round(total_savings, 3),
        "trees_planted": trees_planted
    }

