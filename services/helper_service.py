import json
from flask import current_app


def get_available_helper(area):
    """
    Returns the highest-rated available helper in the given area.
    Returns None if no helper is available in that area.
    """
    file_path = current_app.config["HELPERS_FILE"]

    with open(file_path) as f:
        helpers = json.load(f)

    matches = [
        h for h in helpers
        if h.get("area") == area and h.get("available", False)
    ]

    if not matches:
        return None

    # Pick the highest-rated helper
    return max(matches, key=lambda h: h.get("rating", 0))