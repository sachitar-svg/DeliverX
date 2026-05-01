# app.py
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import os

from routes.order_routes    import order_bp
from routes.otp_routes      import otp_bp
from routes.delivery_routes import delivery_bp
from routes.notify_routes   import notify_bp
from routes.slot_routes     import slot_bp
from routes.hub_routes      import hub_bp
from routes.route_routes    import route_bp
from routes.bundle_routes   import bundle_bp

from models import create_tables
from utils.config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

with app.app_context():
    create_tables()

app.register_blueprint(order_bp)
app.register_blueprint(otp_bp)
app.register_blueprint(delivery_bp)
app.register_blueprint(notify_bp)
app.register_blueprint(slot_bp)
app.register_blueprint(hub_bp)
app.register_blueprint(route_bp)
app.register_blueprint(bundle_bp)

# ── Serve Frontend folder ────────────────────────────────────────
FRONTEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Frontend")

@app.route("/")
def home():
    return send_from_directory(FRONTEND, "home.html")

@app.route("/login")
def login():
    return send_from_directory(FRONTEND, "login.html")

@app.route("/agent")
def agent():
    return send_from_directory(FRONTEND, "agent.html")

@app.route("/hub")
def hub():
    return send_from_directory(FRONTEND, "hub.html")

@app.route("/customer")
def customer():
    return send_from_directory(FRONTEND, "customer.html")

@app.route("/admin")
def admin():
    return send_from_directory(FRONTEND, "admin.html")

# ── Serve JS, CSS, and other frontend assets ────────────────────
@app.route("/Frontend/<path:filename>")
def frontend_static(filename):
    return send_from_directory(FRONTEND, filename)

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}, 200
if __name__ == "__main__":
    app.run(debug=True)