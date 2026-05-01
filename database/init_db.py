# database/init_db.py
from database.db import DB_PATH
from models import create_tables
import sqlite3

def init_db():
    create_tables()
    print(f"✅ Database initialized at: {DB_PATH}")

if __name__ == "__main__":
    init_db()