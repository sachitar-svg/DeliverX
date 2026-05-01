import base64, os, time

# In-memory proof store — swap with DB later
delivery_proofs = {}

def save_delivery_proof(order_id: str, photo_b64: str, lat: float, lng: float) -> dict:
    """
    Saves delivery proof: decoded photo + geo-tag + timestamp.
    Photo is stored as a file in /uploads/. Falls back gracefully if no photo.
    """
    proof = {
        "order_id": order_id,
        "lat": lat,
        "lng": lng,
        "timestamp": time.time(),
        "photo_path": None
    }

    if photo_b64:
        try:
            uploads_dir = os.path.join(os.getcwd(), "uploads")
            os.makedirs(uploads_dir, exist_ok=True)

            filename = f"proof_{order_id}_{int(time.time())}.jpg"
            filepath = os.path.join(uploads_dir, filename)

            with open(filepath, "wb") as f:
                f.write(base64.b64decode(photo_b64))

            proof["photo_path"] = filepath
        except Exception as e:
            proof["photo_error"] = str(e)

    delivery_proofs[str(order_id)] = proof
    return proof


def get_delivery_proof(order_id: str):
    """Returns the proof record for an order, or None."""
    return delivery_proofs.get(str(order_id))