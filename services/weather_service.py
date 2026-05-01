import requests

def get_weather(lat, lon):
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": "YOUR_API_KEY",
            "units": "metric"
        }

        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        return data.get("weather", [{}])[0].get("main", "Unknown")

    except Exception as e:
        print("[Weather] API error:", e)

        # ✅ IMPORTANT: return fallback instead of crashing
        return "Unknown"