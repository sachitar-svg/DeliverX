# models/order_model.py
from database.db import get_db

def get_order_by_id(order_id):
    db = get_db()
    order = db.execute(
        "SELECT * FROM orders WHERE order_id = ?", (order_id,)
    ).fetchone()
    db.close()
    return dict(order) if order else None

def get_all_orders():
    db = get_db()
    orders = db.execute("SELECT * FROM orders").fetchall()
    db.close()
    return [dict(o) for o in orders]

def update_order_status(order_id, status):
    db = get_db()
    db.execute(
        "UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE order_id = ?",
        (status, order_id)
    )
    db.commit()
    db.close()