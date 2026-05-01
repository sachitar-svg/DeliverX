import requests
from utils.distance import haversine_distance, estimate_time
from utils.weather import get_weather
from utils.traffic import get_traffic
from utils.eco import calculate_emission


def get_route(start, end):
    """
    Calculates best route between two [lat, lon] coordinate pairs.
    Tries OSRM (real road routing) first, falls back to haversine.
    Applies real-time traffic and weather multipliers to travel time.
    """
    # OSRM expects lon,lat order
    start_str = f"{start[1]},{start[0]}"
    end_str   = f"{end[1]},{end[0]}"
    url = (
        f"http://router.project-osrm.org/route/v1/driving/"
        f"{start_str};{end_str}?overview=false"
    )

    traffic_factor, traffic_level     = get_traffic()
    weather_factor, weather_condition = get_weather(start[0], start[1])

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("code") == "Ok":
            route       = data["routes"][0]
            distance_km = route["distance"] / 1000
            time_min    = route["duration"] / 60
            adjusted    = time_min * traffic_factor * weather_factor
            carbon      = calculate_emission(distance_km)

            return {
                "distance":  round(distance_km, 2),
                "time":      round(adjusted, 2),
                "source":    "OSRM",
                "traffic":   traffic_level,
                "weather":   weather_condition,
                "carbon_kg": carbon
            }

    except Exception as e:
        # Bug fix — bare except replaced so errors show in terminal
        print(f"[Route] OSRM failed: {e}. Using haversine fallback.")

    # Fallback — straight-line haversine distance
    distance = haversine_distance(start, end)
    time     = estimate_time(distance)
    adjusted = time * traffic_factor * weather_factor
    carbon   = calculate_emission(distance)

    return {
        "distance":  round(distance, 2),
        "time":      round(adjusted, 2),
        "source":    "fallback",
        "traffic":   traffic_level,
        "weather":   weather_condition,
        "carbon_kg": carbon
    }