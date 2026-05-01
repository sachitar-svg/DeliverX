from flask import Blueprint, request, jsonify, current_app
from services.otp_service import verify_otp
from services.delivery_service import save_delivery_proof, get_delivery_proof

# Bug fix — blueprint name was "slot", conflicts with slot_routes.py
delivery_bp = Blueprint("delivery", __name__)


@delivery_bp.route("/confirm-delivery", methods=["POST"])
def confirm_delivery():
    """
    Agent confirms delivery. Requires OTP + optional photo + geo-tag.
    Body: {
        "order_id": "ORD001",
        "role": "agent",
        "otp": "4821",
        "lat": 28.6139,
        "lng": 77.2090,
        "photo": ""   (optional)
    }
    """
    data = request.json
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    order_id = data.get("order_id")
    role     = data.get("role")
    otp      = data.get("otp")
    lat      = data.get("lat")
    lng      = data.get("lng")
    photo    = data.get("photo", None)

    if not order_id or not role or otp is None:
        return jsonify({"error": "Missing order_id, role, or otp"}), 400

    if lat is None or lng is None:
        return jsonify({"error": "Missing lat or lng for geo-tag"}), 400

    success, message = verify_otp(
        str(order_id), role, str(otp).strip(),
        current_app.config["OTP_EXPIRY"]
    )

    if not success:
        return jsonify({"success": False, "message": message}), 400

    proof = save_delivery_proof(str(order_id), photo, float(lat), float(lng))

    return jsonify({
        "success": True,
        "message": "Delivery confirmed",
        "proof": {
            "order_id":   proof["order_id"],
            "lat":        proof["lat"],
            "lng":        proof["lng"],
            "timestamp":  proof["timestamp"],
            "photo_saved": proof["photo_path"] is not None
        }
    }), 200


# Bug fix — URL had no <order_id> parameter, function would crash
@delivery_bp.route("/delivery-proof/<order_id>", methods=["GET"])
def fetch_proof(order_id):
    """Returns the proof of delivery for an order."""
    proof = get_delivery_proof(order_id)
    if not proof:
        return jsonify({"error": "No proof found for this order"}), 404
    return jsonify(proof), 200