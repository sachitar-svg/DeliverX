
from flask import Blueprint, request, jsonify
from utils.geocoding import get_coordinates
from routes.route_optimizer import get_route

route_bp = Blueprint("route", __name__)


@route_bp.route("/geocode", methods=["POST"])
def geocode():
    """
    Converts a text address to GPS coordinates.
    Frontend uses this before showing a pin on the map.

    Body: { "address": "MG Road, Bangalore" }

    Returns: { "address": "...", "coordinates": [lat, lon] }
    """
    data = request.json
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    address = data.get("address", "").strip()
    if not address:
        return jsonify({"error": "Missing or empty address field"}), 400

    coords = get_coordinates(address)
    if coords is None:
        return jsonify({
            "error": "Address not found. Try a more specific address."
        }), 404

    return jsonify({
        "address":     address,
        "coordinates": coords
    }), 200


@route_bp.route("/route", methods=["POST"])
def get_delivery_route():
    """
    Calculates full route between two addresses.
    Frontend uses this to display route info and estimated delivery time.

    Body: { "start": "Whitefield, Bangalore", "end": "Koramangala, Bangalore" }

    Returns distance, time, traffic, weather, CO2, and routing method used.
    """
    data = request.json
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    start_address = data.get("start", "").strip()
    end_address   = data.get("end", "").strip()

    if not start_address or not end_address:
        return jsonify({"error": "Missing start or end address"}), 400

    # Convert addresses to coordinates
    start_coords = get_coordinates(start_address)
    end_coords   = get_coordinates(end_address)

    if not start_coords:
        return jsonify({
            "error": f"Could not find coordinates for start address: {start_address}"
        }), 404

    if not end_coords:
        return jsonify({
            "error": f"Could not find coordinates for end address: {end_address}"
        }), 404

    route_data = get_route(start_coords, end_coords)

    if route_data is None:
        return jsonify({"error": "Route calculation failed"}), 500

    return jsonify({
        "start":       start_address,
        "end":         end_address,
        "distance_km": route_data["distance"],
        "time_min":    route_data["time"],
        "method":      route_data["source"],
        "traffic":     route_data["traffic"],
        "weather":     route_data["weather"],
        "carbon_kg":   route_data["carbon_kg"]
    }), 200
