import os

class Config:
    DEBUG = True
    SECRET_KEY = "routemitra-secret-key"

    # Database
    DATABASE = os.path.join(os.getcwd(), "database.db")

    # File paths
    HUBS_FILE = os.path.join(os.getcwd(), "data/hubs.json")
    HELPERS_FILE = os.path.join(os.getcwd(), "data/helpers.json")

    # OTP settings (for next step)
    OTP_EXPIRY = 300  # seconds (5 mins)