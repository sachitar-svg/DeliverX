def select_mode(area_type, connectivity, address_clear):
    if area_type == "rural" or connectivity == "low" or not address_clear:
        return "micro-hub"
    return "direct"