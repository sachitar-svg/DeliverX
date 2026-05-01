def predict_failure(order_data: dict) -> dict:
    """
    Predicts delivery failure risk using 5 signals.
    Returns a risk score (0.0–1.0) and a human-readable level.

    Expected keys in order_data:
        time          (int)   hour 0-23
        day_of_week   (str)   "weekday" or "weekend"
        location_type (str)   "home", "office", "other"
        past_failures (int)   number of past failed deliveries for this customer
        reschedule_count (int) number of times customer has rescheduled
    """
    score = 0.0

    # Signal 1 — time of day (weight: 0.25)
    hour = int(order_data.get("time", 12))
    if 9 <= hour <= 18:
        score += 0.0    # business hours = low risk
    elif 7 <= hour < 9 or 18 < hour <= 21:
        score += 0.15   # early morning / evening = medium
    else:
        score += 0.25   # late night / very early = high risk

    # Signal 2 — weekday vs weekend (weight: 0.15)
    day = order_data.get("day_of_week", "weekday")
    if day == "weekend":
        score += 0.0    # people are usually home
    else:
        score += 0.15   # weekday = might be at work

    # Signal 3 — location type (weight: 0.20)
    location = order_data.get("location_type", "home")
    if location == "home":
        score += 0.0
    elif location == "office":
        score += 0.10   # office hours only — risky outside 9-6
    else:
        score += 0.20   # unknown/other — highest risk

    # Signal 4 — past delivery failures (weight: 0.25)
    past_failures = int(order_data.get("past_failures", 0))
    if past_failures == 0:
        score += 0.0
    elif past_failures == 1:
        score += 0.10
    elif past_failures == 2:
        score += 0.18
    else:
        score += 0.25   # 3+ failures — high risk customer

    # Signal 5 — reschedule behaviour (weight: 0.15)
    reschedules = int(order_data.get("reschedule_count", 0))
    if reschedules == 0:
        score += 0.0
    elif reschedules == 1:
        score += 0.07
    else:
        score += 0.15

    # Clamp to 1.0
    score = min(round(score, 2), 1.0)

    if score >= 0.6:
        level = "high"
    elif score >= 0.3:
        level = "medium"
    else:
        level = "low"

    return {"score": score, "level": level}