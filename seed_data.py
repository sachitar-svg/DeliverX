import sqlite3
import uuid
import random

# Path to your database
DB_PATH = "database.db"

def seed_orders():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        print("Connecting to database...")

        # 1. CLEAR OLD DATA (Optional)
        # We delete 'placed' orders so you have a clean slate to test the AI Bundling
        cursor.execute("DELETE FROM orders WHERE status = 'dispatched' OR status = 'placed'")
        print("🧹 Cleared old pending orders for a fresh test.")

        test_orders = []

        # --- SCENARIO 1: Direct Cluster A (Urban center - Very Close) ---
        # These 3 orders should form ONE bundle
        lat_a, lon_a = 12.9716, 77.5946
        for i in range(3):
            oid = str(uuid.uuid4())[:8].upper()
            # Tiny random variation to simulate different houses on one street
            lat = lat_a + random.uniform(-0.001, 0.001)
            lon = lon_a + random.uniform(-0.001, 0.001)
            test_orders.append((oid, "placed", "direct", lat, lon, "9886000001", "Urban Center"))

        # --- SCENARIO 2: Direct Cluster B (Suburbs - Close to each other, but far from A) ---
        # These 2 orders should form a SECOND bundle
        lat_b, lon_b = 13.0100, 77.6200
        for i in range(2):
            oid = str(uuid.uuid4())[:8].upper()
            lat = lat_b + random.uniform(-0.001, 0.001)
            lon = lon_b + random.uniform(-0.001, 0.001)
            test_orders.append((oid, "placed", "direct", lat, lon, "9886000002", "Suburban Area"))

        # --- SCENARIO 3: Hub Orders (Same Hub) ---
        # These 4 orders should all be bundled into ONE "Hub Master Bundle"
        for i in range(4):
            oid = str(uuid.uuid4())[:8].upper()
            lat = 12.9500 + random.uniform(-0.01, 0.01)
            lon = 77.5500 + random.uniform(-0.01, 0.01)
            # All assigned to hub_id = 1
            test_orders.append((oid, "placed", "micro-hub", lat, lon, "9886000003", "Hub Zone"))

        # --- INSERT INTO DB ---
        for o in test_orders:
            cursor.execute("""
                INSERT INTO orders (
                    order_id, status, mode, lat, lon, 
                    customer_phone, area_type, connectivity, address_clear, time, 
                    start_address, end_address, hub_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                o[0], o[1], o[2], o[3], o[4], 
                o[5], "urban", "high", 1, 12, 
                "Pickup Point", o[6], (1 if o[2] == 'micro-hub' else None)
            ))

        conn.commit()
        conn.close()
        print(f"✅ Successfully added {len(test_orders)} test orders!")
        print("\n--- EXPECTED RESULTS IN ADMIN PANEL ---")
        print("1. Hub Bundle: 4 orders grouped together (Mode: micro-hub)")
        print("2. Direct Bundle 1: 3 orders grouped together (Cluster A)")
        print("3. Direct Bundle 2: 2 orders grouped together (Cluster B)")
        print("\n👉 Now open your Admin Dashboard -> AI Bundling Tab -> Run AI")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")

if __name__ == "__main__":
    seed_orders()
