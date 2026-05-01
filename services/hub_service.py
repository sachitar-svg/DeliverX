import json
from flask import current_app


def get_available_hub():
    """
    Returns the hub with the highest available_slots (best capacity),
    not just the first one found in the file.
    Returns None if no hubs have capacity.
    """
    file_path = current_app.config["HUBS_FILE"]

    with open(file_path) as f:
        hubs = json.load(f)

    available = [h for h in hubs if h.get("available_slots", 0) > 0]

    if not available:
        return None

    # Pick hub with most free slots (best capacity)
    return max(available, key=lambda h: h["available_slots"])