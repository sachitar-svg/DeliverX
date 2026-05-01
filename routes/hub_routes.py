
from flask import Blueprint, request, jsonify, current_app
from services.hub_otp_service import (
    generate_agent_hub_otp,
    verify_agent_hub_otp,
    generate_customer_hub_otp,
    verify_customer_hub_otp,
    get_parcel_status,
    get_hub_by_id,
    is_hub_open
)
from services.notify_service import notify_parcel_arrived

hub_bp = Blueprint("hub", __name__)


# ── 1. Generate OTP-1 (agent gets this before going to hub) ─────
@hub_bp.route("/hub/generate-agent-otp", methods=["POST"])
def gen_agent_otp():
    """
    Called when order is dispatched to micro-hub.
    Body: { "order_id": "ORD001" }
    """
    data = request.json
    if not data:
        return jsonify({"error": "Request body required"}), 400

    order_id = data.get("order_id")
    if not order_id:
        return jsonify({"error": "Missing order_id"}), 400

    otp = generate_agent_hub_otp(str(order_id))
    return jsonify({
        "message": "OTP-1 generated for agent handoff",
        "order_id": order_id,
        "otp": otp
    }), 200


# ── 2. Verify OTP-1 (agent verifies at hub, hub accepts parcel) ─
@hub_bp.route("/hub/verify-agent-otp", methods=["POST"])
def verify_agent_otp():
    """
    Agent shows OTP-1 to hub. Hub verifies.
    On success: parcel marked as 'at_hub', SMS sent to customer.
    Body: {
        "order_id": "ORD001",
        "otp": "4821",
        "hub_id": 1,
        "customer_phone": "9999999999"
    }
    """
    data = request.json
    if not data:
        return jsonify({"error": "Request body required"}), 400

    order_id       = data.get("order_id")
    entered_otp    = data.get("otp")
    hub_id         = data.get("hub_id")
    customer_phone = data.get("customer_phone")

    if not order_id or entered_otp is None or not hub_id or not customer_phone:
        return jsonify({
            "error": "Missing order_id, otp, hub_id, or customer_phone"
        }), 400

    success, message = verify_agent_hub_otp(
        str(order_id),
        str(entered_otp),
        current_app.config["OTP_EXPIRY"]
    )

    if not success:
        return jsonify({"success": False, "message": message}), 400

    # OTP-1 verified — now generate OTP-2 for customer
    customer_otp = generate_customer_hub_otp(str(order_id))

    # Load hub details to include in SMS
    hub = get_hub_by_id(int(hub_id))
    if not hub:
        return jsonify({"error": "Hub not found"}), 404

    # Send SMS to customer
    sms_result = notify_parcel_arrived(
        phone          = customer_phone,
        order_id       = str(order_id),
        hub_name       = hub["name"],
        hub_location   = hub["location"],
        open_time      = hub["open_time"],
        close_time     = hub["close_time"],
        customer_otp   = customer_otp
    )

    return jsonify({
        "success": True,
        "message": "Parcel accepted by hub. Customer notified via SMS.",
        "parcel_status": "at_hub",
        "sms": sms_result
    }), 200


# ── 3. Verify OTP-2 (customer arrives at hub to collect parcel) ─
@hub_bp.route("/hub/verify-customer-otp", methods=["POST"])
def verify_customer_otp():
    """
    Customer shows OTP-2 at hub counter.
    System checks: hub open? → OTP correct? → mark collected.
    Body: {
        "order_id": "ORD001",
        "otp": "7362",
        "hub_id": 1
    }
    """
    data = request.json
    if not data:
        return jsonify({"error": "Request body required"}), 400

    order_id    = data.get("order_id")
    entered_otp = data.get("otp")
    hub_id      = data.get("hub_id")

    if not order_id or entered_otp is None or not hub_id:
        return jsonify({"error": "Missing order_id, otp, or hub_id"}), 400

    success, message = verify_customer_hub_otp(
        str(order_id),
        str(entered_otp),
        current_app.config["OTP_EXPIRY"],
        int(hub_id)
    )

    status_code = 200 if success else 400
    return jsonify({
        "success": success,
        "message": message,
        "parcel_status": "collected" if success else "at_hub"
    }), status_code


# ── 4. Check parcel status ───────────────────────────────────────
@hub_bp.route("/hub/parcel-status/<order_id>", methods=["GET"])
def parcel_status(order_id):
    """
    Returns current status of parcel.
    Possible values: in_transit | at_hub | collected | unknown
    """
    status = get_parcel_status(order_id)
    return jsonify({
        "order_id": order_id,
        "status": status
    }), 200


# ── 5. Check if a specific hub is open right now ─────────────────
@hub_bp.route("/hub/hours/<hub_id>", methods=["GET"])
def hub_hours(hub_id):
    """
    Returns hub operating hours and whether it is open right now.
    """
    hub = get_hub_by_id(hub_id)
    if not hub:
        return jsonify({"error": "Hub not found"}), 404

    is_open, hours_message = is_hub_open(hub)
    return jsonify({
        "hub_id": hub_id,
        "name": hub["name"],
        "open_time": hub["open_time"],
        "close_time": hub["close_time"],
        "is_open_now": is_open,
        "message": hours_message
    }), 200
