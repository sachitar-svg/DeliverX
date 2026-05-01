# services/revenue_service.py

def calculate_delivery_fee(distance_km, mode, risk_level, weather="clear"):
    """
    Dynamic Pricing Model:
    - Base Fee: ₹50
    - Distance Fee: ₹15 per km
    - Mode Adjustment: Micro-hub is 20% cheaper than Direct
    - Risk Surcharge: High risk adds ₹30 to cover potential redelivery
    - Weather Surcharge: Bad weather adds ₹20
    """
    base_fee = 50.0
    per_km_rate = 15.0
    
    # 1. Distance Cost
    distance_cost = distance_km * per_km_rate
    
    # 2. Mode Adjustment
    mode_multiplier = 0.8 if mode == "micro-hub" else 1.0
    
    # 3. Risk Surcharge (Integration with Failure Predictor)
    risk_fee = 0
    if risk_level == "high":
        risk_fee = 30.0
    elif risk_level == "medium":
        risk_fee = 15.0
        
    # 4. Weather Surcharge (Integration with Weather Service)
    weather_fee = 0
    if weather.lower() in ["storm", "heavy rain", "snow"]:
        weather_fee = 20.0

    total = (base_fee + distance_cost) * mode_multiplier + risk_fee + weather_fee
    
    return {
        "total_cost": round(total, 2),
        "breakdown": {
            "base": base_fee,
            "distance": round(distance_cost, 2),
            "mode_discount": "20% (Hub)" if mode == "micro-hub" else "None",
            "risk_surcharge": risk_fee,
            "weather_surcharge": weather_fee
        }
    }
