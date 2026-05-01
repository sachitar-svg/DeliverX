import uuid
from flask import Blueprint, request, jsonify
from database.db import get_db
from services.revenue_service import calculate_delivery_fee
from services.mode_selector import select_mode
from services.failure_predictor import predict_failure
from services.hub_service import get_available_hub
from services.helper_service import get_available_helper
from utils.geocoding import get_coordinates
from routes.route_optimizer import get_route

order_bp = Blueprint('order_bp', __name__)


# =========================
# 📦 PLACE ORDER
# =========================
@order_bp.route("/place-order", methods=["POST"])
def place_order():
    data = request.json
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    required = [
        "area_type", "connectivity",
        "address_clear", "time",
        "start_address", "end_address",
        "customer_phone"
    ]

    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        hour = int(data["time"])
        if not (0 <= hour <= 23):
            raise ValueError
    except:
        return jsonify({"error": "'time' must be 0-23"}), 400

    order_id = str(uuid.uuid4())[:8].upper()

    area_type      = data.get("area_type", "").strip()
    connectivity   = data.get("connectivity", "").strip()
    address_clear  = data.get("address_clear", False)
    start_address  = data.get("start_address", "").strip()
    end_address    = data.get("end_address", "").strip()
    customer_phone = data.get("customer_phone", "").strip()

    mode = select_mode(area_type, connectivity, address_clear)

    risk = predict_failure({
        "time":             hour,
        "day_of_week":      data.get("day_of_week", "weekday"),
        "location_type":    data.get("location_type", "home"),
        "past_failures":    int(data.get("past_failures", 0)),
        "reschedule_count": int(data.get("reschedule_count", 0)),
    })

    hub    = None
    helper = None

    if mode == "micro-hub":
        hub = get_available_hub()
        if hub:
            helper = get_available_helper(hub["location"])

    # =========================
    # 📍 ROUTE & COORDINATES
    # =========================
    # ✅ Initialize all to None BEFORE the if block
    # so Pylance always sees them as defined
    distance_km = time_min = carbon_kg = traffic = weather = None
    start_lat = start_lon = None
    end_lat   = end_lon   = None

    if start_address and end_address:
        start_coords = get_coordinates(start_address)
        end_coords   = get_coordinates(end_address)

        if start_coords and end_coords:
            # ✅ Save coordinates from geocoding
            start_lat, start_lon = start_coords
            end_lat,   end_lon   = end_coords

            route = get_route(start_coords, end_coords)
            distance_km = route["distance"]
            time_min    = route["time"]
            carbon_kg   = route["carbon_kg"]
            traffic     = route["traffic"]
            weather     = route["weather"]

    # =========================
    # 💰 REVENUE CALCULATION
    # =========================
    price_data = calculate_delivery_fee(
        distance_km=distance_km if distance_km else 0,
        mode=mode,
        risk_level=risk["level"],
        weather=weather if weather else "clear"
    )
    total_cost = price_data["total_cost"]

    # =========================
    # 💾 SAVE TO DB
    # =========================
    try:
        db = get_db()
        db.execute("""
    INSERT INTO orders (
        order_id, status, mode, area_type, connectivity,
        start_address, end_address,
        lat, lon,
        hub_id, helper_id,
        failure_score, failure_level,
        distance_km, time_min, carbon_kg,
        traffic, weather,
        total_cost
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
""", (
    order_id,
    "placed",
    mode,
    area_type,
    connectivity,
    start_address,
    end_address,
    end_lat,
    end_lon,
    hub["id"] if hub else None,
    helper["id"] if helper else None,
    risk["score"],
    risk["level"],
    distance_km,
    time_min,
    carbon_kg,
    traffic,
    weather,
    total_cost,
))
        db.commit()
        db.close()

    except Exception as e:
        print(f"[DB ERROR] {str(e)}")
        return jsonify({"error": f"DB error: {str(e)}"}), 500

    return jsonify({
        "order_id":   order_id,
        "mode":       mode,
        "risk":       risk,
        "hub":        hub,
        "helper":     helper,
        "total_cost": total_cost
    }), 200


# =========================
# 🔍 ORDER STATUS
# =========================
@order_bp.route("/order-status/<order_id>", methods=["GET"])
def order_status(order_id):
    try:
        db = get_db()
        row = db.execute(
            "SELECT * FROM orders WHERE order_id = ?",
            (order_id.upper(),)
        ).fetchone()
        db.close()

        if not row:
            return jsonify({"error": "Order not found"}), 404

        return jsonify(dict(row)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# 🔄 UPDATE STATUS
# =========================
@order_bp.route("/order-status/<order_id>", methods=["PATCH"])
def update_order_status(order_id):
    data = request.json
    if not data:
        return jsonify({"error": "Body required"}), 400

    new_status = data.get("status")

    try:
        db = get_db()
        result = db.execute(
            "UPDATE orders SET status = ? WHERE order_id = ?",
            (new_status, order_id.upper())
        )
        db.commit()
        db.close()

        if result.rowcount == 0:
            return jsonify({"error": "Order not found"}), 404

        return jsonify({"status": new_status}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# 📋 ALL ORDERS
# =========================
@order_bp.route("/all-orders", methods=["GET"])
def all_orders():
    try:
        status_filter = request.args.get("status")
        db = get_db()

        if status_filter:
            rows = db.execute(
                "SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC",
                (status_filter,)
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM orders ORDER BY created_at DESC"
            ).fetchall()

        db.close()
        return jsonify({"orders": [dict(r) for r in rows]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500