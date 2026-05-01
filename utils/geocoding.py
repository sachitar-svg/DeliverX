# utils/geocoding.py
import requests

# ✅ Known coordinates — skip geocoding for fixed warehouse address
KNOWN_LOCATIONS = {
    "deliverx central warehouse": (12.9698, 77.7500),  # Whitefield, Bangalore
}

def get_coordinates(address):
    # Check known locations first (fast, no network needed)
    key = address.lower().strip()
    for known, coords in KNOWN_LOCATIONS.items():
        if known in key:
            print(f"[Geocoding] Using cached coords for: {address}")
            return list(coords)

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json"}
    headers = {"User-Agent": "DeliverX-App"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"[Geocoding] Network error for '{address}': {e}")
        return None

    if not data:
        print(f"[Geocoding] No results for: {address}")
        return None

    try:
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        print(f"[Geocoding] Found: {address} → {lat}, {lon}")
        return [lat, lon]
    except (KeyError, ValueError) as e:
        print(f"[Geocoding] Parse error: {e}")
        return None