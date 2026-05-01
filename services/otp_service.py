import random
import time

# In-memory store: { "ORDER123": { "agent": {"otp": "1234", "timestamp": 123456} } }
otp_store = {}

def generate_otp(order_id: str, role: str) -> str:
    """Generates a 4-digit OTP and stores it with normalized keys."""
    # Normalize: Order ID to Upper, Role to Lower
    oid = str(order_id).upper().strip()
    rl = str(role).lower().strip()
    
    otp = str(random.randint(1000, 9999))

    if oid not in otp_store:
        otp_store[oid] = {}

    otp_store[oid][rl] = {
        "otp": otp,
        "timestamp": time.time()
    }

    print(f"📦 [SERVICE] Generated OTP {otp} for Order {oid} | Role: {rl}")
    return otp

def verify_otp(order_id: str, role: str, entered_otp: str, expiry_time: int):
    """Verifies the OTP with strict normalization."""
    oid = str(order_id).upper().strip()
    rl = str(role).lower().strip()
    otp_val = str(entered_otp).strip()

    print(f"🔍 [SERVICE] Verifying Order {oid} | Role {rl} | Entered: {otp_val}")

    # 1. Check if Order exists
    if oid not in otp_store:
        print(f"❌ [SERVICE] Order {oid} not found in memory.")
        return False, "OTP not found"

    # 2. Check if Role exists for this order
    if rl not in otp_store[oid]:
        print(f"❌ [SERVICE] Role {rl} not found for Order {oid}. Available: {list(otp_store[oid].keys())}")
        return False, f"No OTP found for role {rl}"

    data = otp_store[oid][rl]

    # 3. Check Expiry
    if time.time() - data["timestamp"] > expiry_time:
        print(f"❌ [SERVICE] OTP for {oid} expired.")
        del otp_store[oid][rl]
        return False, "OTP expired"

    # 4. Check Value
    if data["otp"] == otp_val:
        print(f"✅ [SERVICE] OTP Match for {oid}!")
        # Optional: del otp_store[oid][rl] # Delete after use
        return True, "OTP verified"

    print(f"❌ [SERVICE] Value Mismatch. Expected {data['otp']}, got {otp_val}")
    return False, "Invalid OTP"
