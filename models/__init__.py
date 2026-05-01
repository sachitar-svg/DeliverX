# models/__init__.py
import sqlite3
from database.db import DB_PATH

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id            TEXT UNIQUE,
        status              TEXT DEFAULT 'CREATED',
        mode                TEXT,
        area_type           TEXT,
        connectivity        TEXT,
        address_clear       BOOLEAN,
        time                INTEGER,
        start_address       TEXT,
        end_address         TEXT,
        lat                 REAL,
        lon                 REAL,
        hub_id              INTEGER,
        helper_id           INTEGER,
        failure_score       REAL,
        failure_level       TEXT,
        distance_km         REAL,
        estimated_time_min  REAL,
        time_min            REAL,
        carbon_kg           REAL,
        traffic             TEXT,
        weather             TEXT,
        created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Tables created successfully")