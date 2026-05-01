import requests
from flask import current_app


def get_weather(lat, lon):
    """
    Fetches current weather condition and returns a delay multiplier.
    Uses OpenWeatherMap API. Key is read from app config, not hardcoded.

    Returns: (multiplier float, condition string)
      clear   → 1.0
      rain    → 1.1  (10% slower)
      storm   → 1.3  (30% slower)
      unknown → 1.0  (safe default)
    """
    try:
        api_key = current_app.config.get("WEATHER_API_KEY", "")
        if not api_key:
            return 1.0, "unknown"

        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "metric"
        }

        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if "weather" not in data:
            return 1.0, "unknown"

        condition = data["weather"][0]["main"].lower()

        if "rain" in condition:
            return 1.1, "rain"
        elif "storm" in condition or "thunderstorm" in condition:
            return 1.3, "storm"
        else:
            return 1.0, "clear"

    except Exception as e:
        print(f"[Weather] API error: {e}")
        return 1.0, "unknown"