# In-memory slot store — replace with DB later
slot_store = {}

AVAILABLE_WINDOWS = [
    "07:00-09:00",
    "09:00-12:00",
    "12:00-15:00",
    "15:00-18:00",
    "18:00-21:00",
]

def get_available_slots():
    """Returns all possible delivery windows."""
    return AVAILABLE_WINDOWS

def select_slot(order_id: str, slot: str) -> tuple:
    """
    Assigns a delivery slot to an order.
    Returns (True, slot) on success, (False, reason) on failure.
    """
    if slot not in AVAILABLE_WINDOWS:
        return False, f"Invalid slot. Choose from: {AVAILABLE_WINDOWS}"

    slot_store[str(order_id)] = slot
    return True, slot

def get_slot(order_id: str):
    """Returns the chosen slot for an order, or None."""
    return slot_store.get(str(order_id))