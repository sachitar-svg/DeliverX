from flask import Blueprint, request, jsonify, current_app
from utils.eco import get_agent_eco_stats
from database.db import get_db
from services.otp_service import generate_otp, verify_otp
from services.hub_otp_service import (
    generate_agent_hub_otp,
    verify_agent_hub_otp,
    generate_customer_hub_otp,
    verify_customer_hub_otp,
    get_parcel_status,
)

otp_bp = Blueprint("otp", __name__)

# ✅ SET DEFAULT HUB ID
DEFAULT_HUB_ID = 1

# ═══════════════════════════════════════════════════════════════
# DIRECT DELIVERY (Agent <-> Customer)
# ═══════════════════════════════════════════════════════════════

@otp_bp.route("/generate-otp", methods=["POST"])
def create_otp():
    data = request.json or {}
    order_id = data.get("order_id")
    role = data.get("role")
    if not order_id or not role:
        return jsonify({"error": "Missing order_id or role"}), 400
    # Cast to str() to prevent Pylance "None" errors
    otp = generate_otp(str(order_id), role)
    return jsonify({"success": True, "otp": otp, "message": "OTP generated"})

@otp_bp.route("/verify-otp", methods=["POST"])
def check_otp():
    data = request.json or {}
    order_id = data.get("order_id")
    role = data.get("role")
    entered_otp = data.get("otp")
    if not order_id or not role or entered_otp is None:
        return jsonify({"error": "Missing order_id, role, or otp"}), 400
    
    success, message = verify_otp(
        str(order_id), 
        role, 
        str(entered_otp), 
        current_app.config["OTP_EXPIRY"]
    )
    return jsonify({"success": success, "message": message})

# ═══════════════════════════════════════════════════════════════
# HUB DELIVERY (Agent -> Hub -> Customer)
# ═══════════════════════════════════════════════════════════════

@otp_bp.route("/hub/generate-agent-otp", methods=["POST"])
def agent_hub_generate():
    data = request.json or {}
    order_id = data.get("order_id")
    if not order_id: return jsonify({"error": "Missing order_id"}), 400
    otp = generate_agent_hub_otp(str(order_id))
    return jsonify({"success": True, "otp": otp})

@otp_bp.route("/hub/verify-bundle-otp", methods=["POST"])
def verify_bundle_otp():
    data = request.json or {}
    order_id = data.get("order_id")
    entered_otp = data.get("otp")
    
    if not order_id or not entered_otp:
        return jsonify({"error": "Missing order_id or otp"}), 400

    # Fixed: str(order_id) ensures we don't call .upper() on None
    success, message = verify_agent_hub_otp(str(order_id), str(entered_otp), current_app.config["OTP_EXPIRY"])
    
    if not success:
        return jsonify({"success": False, "message": message}), 400

    try:
        db = get_db()
        db.execute("UPDATE orders SET status = 'at_hub' WHERE status = 'dispatched' AND mode = 'micro-hub'")
        db.commit()
        db.close()
    except Exception as e:
        return jsonify({"error": f"DB Error: {str(e)}"}), 500

    return jsonify({"success": True, "message": "Bulk handoff successful! All parcels accepted."})

@otp_bp.route("/hub/verify-agent-otp", methods=["POST"])
def agent_hub_verify():
    data = request.json or {}
    order_id = data.get("order_id")
    entered_otp = data.get("otp")
    if not order_id or not entered_otp: return jsonify({"error": "Missing fields"}), 400

    success, message = verify_agent_hub_otp(str(order_id), str(entered_otp), current_app.config["OTP_EXPIRY"])
    if success:
        db = get_db()
        # ✅ FIXED: str(order_id).upper() prevents the Pylance error
        db.execute("UPDATE orders SET status = ? WHERE order_id = ?", ("at_hub", str(order_id).upper()))
        db.commit()
        db.close()
    return jsonify({"success": success, "message": message})

@otp_bp.route("/hub/generate-customer-otp", methods=["POST"])
def customer_hub_generate():
    data = request.json or {}
    order_id = data.get("order_id")
    if not order_id: return jsonify({"error": "Missing order_id"}), 400
    otp = generate_customer_hub_otp(str(order_id))
    return jsonify({"success": True, "otp": otp})

@otp_bp.route("/hub/verify-customer-otp", methods=["POST"])
def customer_hub_verify():
    data = request.json or {}
    order_id = data.get("order_id")
    entered_otp = data.get("otp")
    
    hub_id = data.get("hub_id") or DEFAULT_HUB_ID

    if not order_id or entered_otp is None:
        return jsonify({"error": "Missing order_id or otp"}), 400

    success, message = verify_customer_hub_otp(
        str(order_id), 
        str(entered_otp), 
        current_app.config["OTP_EXPIRY"], 
        int(hub_id)
    )

    if success:
        db = get_db()
        # ✅ FIXED: str(order_id).upper() prevents the Pylance error
        db.execute("UPDATE orders SET status = ? WHERE order_id = ?", ("delivered", str(order_id).upper()))
        db.commit()
        db.close()
        return jsonify({"success": True, "message": message, "parcel_status": "collected"})
    
    return jsonify({"success": False, "message": message}), 400

@otp_bp.route("/agent-stats", methods=["GET"])
def agent_stats():
    try:
        db = get_db()
        rows = db.execute("SELECT * FROM orders WHERE status = 'delivered'").fetchall()
        db.close()
        orders = [dict(r) for r in rows]
        stats = get_agent_eco_stats(orders)
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
