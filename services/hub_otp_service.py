import random
import time
import json
import os
from datetime import datetime
from flask import current_app

# Separate OTP store for hub handoff and customer pickup
hub_otp_store = {}

# Bug fix — anchor path relative to this file so it always lands in project root
# regardless of which directory you run "python app.py" from
STATUS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "parcel_status_store.json"
)


# ─── PERSISTENCE HELPERS ───────────────────────────────────────

def _load_status() -> dict:
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE) as f:
            return json.load(f)
    return {}


def _save_status(data: dict):
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f)


# ─── HUB HOURS CHECK ───────────────────────────────────────────

def is_hub_open(hub: dict) -> tuple:
    """
    Returns (True, message) if hub is currently open.
    Returns (False, reason) if closed.
    """
    now = datetime.now()
    current_minutes = now.hour * 60 + now.minute

    open_h,  open_m  = map(int, hub["open_time"].split(":"))
    close_h, close_m = map(int, hub["close_time"].split(":"))

    open_minutes  = open_h  * 60 + open_m
    close_minutes = close_h * 60 + close_m

    if open_minutes <= current_minutes <= close_minutes:
        return True, f"Hub is open until {hub['close_time']}"

    return False, (
        f"Hub is closed. Opens at {hub['open_time']}, "
        f"closes at {hub['close_time']}. Please visit during these hours."
    )


def get_hub_by_id(hub_id: int) -> dict | None:
    """Loads a hub record by its numeric id from hubs.json."""
    file_path = current_app.config["HUBS_FILE"]
    with open(file_path) as f:
        hubs = json.load(f)
    for hub in hubs:
        if hub["id"] == int(hub_id):
            return hub
    return None


# ─── OTP-1  agent → hub handoff ────────────────────────────────

def generate_agent_hub_otp(order_id: str) -> str:
    """
    Generates OTP-1 for the delivery agent to hand parcel to the hub.
    Sets parcel status to 'in_transit'.
    """
    otp = str(random.randint(1000, 9999))
    hub_otp_store[f"{order_id}_agent_hub"] = {
        "otp": otp,
        "timestamp": time.time()
    }
    data = _load_status()
    data[str(order_id)] = "in_transit"
    _save_status(data)
    return otp


def verify_agent_hub_otp(order_id: str, entered_otp: str, expiry: int) -> tuple:
    """
    Verifies OTP-1 when agent arrives at hub.
    On success: marks parcel as 'at_hub'.
    """
    key = f"{order_id}_agent_hub"

    if key not in hub_otp_store:
        return False, "OTP not found. Generate a new one."

    stored = hub_otp_store[key]

    if time.time() - stored["timestamp"] > expiry:
        del hub_otp_store[key]
        return False, "OTP expired. Generate a new one."

    if stored["otp"] != str(entered_otp).strip():
        return False, "Invalid OTP. Check and try again."

    del hub_otp_store[key]
    data = _load_status()
    data[str(order_id)] = "at_hub"
    _save_status(data)
    return True, "Agent handoff verified. Parcel is now at hub."


# ─── OTP-2  customer → hub pickup ──────────────────────────────

def generate_customer_hub_otp(order_id: str) -> str:
    """
    Generates OTP-2 for the customer to collect parcel.
    Raises ValueError if OTP-1 has not been verified yet (parcel not at hub).
    """
    data = _load_status()
    if data.get(str(order_id)) != "at_hub":
        raise ValueError("Parcel has not been handed off to hub yet.")

    otp = str(random.randint(1000, 9999))
    hub_otp_store[f"{order_id}_customer_hub"] = {
        "otp": otp,
        "timestamp": time.time()
    }
    return otp


def verify_customer_hub_otp(order_id: str, entered_otp: str,
                             expiry: int, hub_id: int) -> tuple:
    """
    Verifies OTP-2 when customer arrives at hub to collect parcel.
    Checks: hub open? → parcel at hub? → OTP correct?
    On success: marks parcel as 'collected'.
    """
    # Step 1 — hub must be open right now
    hub = get_hub_by_id(hub_id)
    if not hub:
        return False, "Hub not found."

    is_open, hours_message = is_hub_open(hub)
    if not is_open:
        return False, hours_message

    # Step 2 — parcel must be registered at hub
    data = _load_status()
    if data.get(str(order_id)) != "at_hub":
        return False, "Parcel is not at this hub yet."

    # Step 3 — verify OTP
    key = f"{order_id}_customer_hub"

    if key not in hub_otp_store:
        return False, "OTP not found. Ask hub to regenerate."

    stored = hub_otp_store[key]

    if time.time() - stored["timestamp"] > expiry:
        del hub_otp_store[key]
        return False, "OTP expired. Ask hub to regenerate."

    if stored["otp"] != str(entered_otp).strip():
        return False, "Invalid OTP. Check and try again."

    del hub_otp_store[key]
    data[str(order_id)] = "collected"
    _save_status(data)
    return True, "Pickup verified. Delivery complete."


# ─── STATUS ────────────────────────────────────────────────────

def get_parcel_status(order_id: str) -> str:
    """Returns parcel status: in_transit | at_hub | collected | unknown"""
    data = _load_status()
    return data.get(str(order_id), "unknown")