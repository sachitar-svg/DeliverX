from flask import Blueprint, request, jsonify
from services.bundling import bundle_orders

bundle_bp = Blueprint("bundle_bp", __name__)
# IMPORT AFTER blueprint (important for debugging)
try:
    from services.bundling import bundle_orders
    print("✅ bundling import success")
except Exception as e:
    print("❌ bundling import error:", e)

print("🔥 bundle_routes LOADED")
print("Routes inside bundle:", bundle_bp.deferred_functions)
@bundle_bp.route("/bundle-orders", methods=["POST"])
def bundle():
    """
    Groups nearby orders into delivery batches.
    Call this before dispatching agents — it tells you which orders
    to assign to the same agent in one trip.

    Body: {
        "orders": [
            {"id": "ORD001", "lat": 12.9716, "lon": 77.5946},
            {"id": "ORD002", "lat": 12.9720, "lon": 77.5950},
            {"id": "ORD003", "lat": 12.9900, "lon": 77.6100}
        ]
    }

    Returns: {
        "bundles": [
            ["ORD001", "ORD002"],
            ["ORD003"]
        ],
        "total_orders": 3,
        "total_bundles": 2
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    orders = data.get("orders", [])

    if not orders:
        return jsonify({"error": "orders list is required and cannot be empty"}), 400

    # Validate each order has required fields
    for i, order in enumerate(orders):
        if "id" not in order:
            return jsonify({"error": f"Order at index {i} is missing 'id'"}), 400
        if "lat" not in order or "lon" not in order:
            return jsonify({"error": f"Order {order.get('id', i)} is missing 'lat' or 'lon'"}), 400

    bundles = bundle_orders(orders)

    return jsonify({
        "bundles":       bundles,
        "total_orders":  len(orders),
        "total_bundles": len(bundles)
    }), 200



