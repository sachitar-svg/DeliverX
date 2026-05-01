import math

def haversine_distance(start, end):
    # Coordinates
    lat1, lon1 = start
    lat2, lon2 = end

    # Convert to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    radius = 6371  # Earth radius in km
    distance = radius * c

    return distance

def estimate_time(distance):
    # Assume average speed = 30 km/h (city delivery)
    speed = 30
    
    time_hours = distance / speed
    time_minutes = time_hours * 60

    return time_minutes

