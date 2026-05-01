from datetime import datetime

def get_traffic():
    hour = datetime.now().hour

    # Peak hours
    if 8 <= hour <= 11 or 17 <= hour <= 20:
        return 1.5, "high"
    
    # Moderate traffic
    elif 12 <= hour <= 16:
        return 1.2, "medium"
    
    # Low traffic
    else:
        return 1.0, "low"
