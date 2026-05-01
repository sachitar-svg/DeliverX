import math

def calculate_distance(p1, p2):
    lat1, lon1 = p1
    lat2, lon2 = p2
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def bundle_orders(orders, max_distance=0.02, max_orders=3):
    bundles = []
    used = set()

    for i in range(len(orders)):
        if i in used:
            continue

        current_bundle = [orders[i]["id"]]
        used.add(i)

        for j in range(i + 1, len(orders)):
            if j in used:
                continue

            dist = calculate_distance(
                (orders[i]["lat"], orders[i]["lon"]),
                (orders[j]["lat"], orders[j]["lon"])
            )

            if dist <= max_distance and len(current_bundle) < max_orders:
                current_bundle.append(orders[j]["id"])
                used.add(j)

        bundles.append(current_bundle)

    return bundles