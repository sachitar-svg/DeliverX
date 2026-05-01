from flask import Blueprint, request, jsonify
from services.slot_service import get_available_slots, select_slot, get_slot

slot_bp = Blueprint("slot", __name__)


@slot_bp.route("/available-slots", methods=["GET"])
def available_slots():
    """Returns all delivery windows a customer can choose from."""
    return jsonify({"slots": get_available_slots()}), 200


@slot_bp.route("/select-slot", methods=["POST"])
def choose_slot():
    """
    Customer selects a delivery window.
    Body: { "order_id": "ORD001", "slot": "18:00-21:00" }
    """
    data = request.json
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    order_id = data.get("order_id")
    slot = data.get("slot")

    if not order_id or not slot:
        return jsonify({"error": "Missing order_id or slot"}), 400

    success, result = select_slot(str(order_id), slot)
    if not success:
        return jsonify({"error": result}), 400

    return jsonify({
        "message": "Slot confirmed",
        "order_id": order_id,
        "slot": result
    }), 200


@slot_bp.route("/get-slot/<order_id>", methods=["GET"])
def fetch_slot(order_id):
    """Returns the selected slot for an order."""
    slot = get_slot(order_id)
    if not slot:
        return jsonify({"error": "No slot selected for this order"}), 404
    return jsonify({"order_id": order_id, "slot": slot}), 200