# utils/config.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    DEBUG = True
    SECRET_KEY = "routemitra-secret-key"

    # ✅ Single DB path — matches database/db.py
    DATABASE = os.path.join(BASE_DIR, "database.db")

    # File paths
    HUBS_FILE    = os.path.join(BASE_DIR, "data", "hubs.json")
    HELPERS_FILE = os.path.join(BASE_DIR, "data", "helpers.json")

    # OTP
    OTP_EXPIRY = 300  # seconds