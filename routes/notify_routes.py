from flask import Blueprint, request, jsonify
from services.notify_service import notify_customer_enroute
from services.slot_service import get_slot

notify_bp = Blueprint("notify", __name__)


@notify_bp.route("/notify-customer", methods=["POST"])
def notify_customer():
    """
    Agent triggers this when they are heading to the customer.
    Body: { "order_id": "ORD001", "phone": "9999999999", "agent_name": "Ramesh" }
    """
    data = request.json
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    order_id = data.get("order_id")
    phone    = data.get("phone")
    agent    = data.get("agent_name")

    if not order_id or not phone or not agent:
        return jsonify({"error": "Missing order_id, phone, or agent_name"}), 400

    # Auto-attach slot if one was chosen
    slot = get_slot(order_id)

    result = notify_customer_enroute(phone, order_id, agent)
    return jsonify(result), 200