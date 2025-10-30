def predict_congestion(distance, duration):
    """
    Simple congestion prediction placeholder.
    Returns 'low', 'medium', 'high', or 'unknown'.
    """
    if distance is None or duration is None:
        return "unknown"
    # simple heuristic: duration per meter
    ratio = duration / max(distance, 1)
    if ratio > 0.05:
        return "high"
    if ratio > 0.02:
        return "medium"
    return "low"


def get_real_time_traffic_data(start_location, end_location):
    """
    Placeholder implementation — replace with an actual traffic API call.
    Should return a tuple: (distance_meters, duration_seconds, raw_data)
    """
    return None, None, None


# Example usage inside app.py (safe standalone example)
if __name__ == "__main__":
    start_location = "PLACE_A"
    end_location = "PLACE_B"
    distance, duration, _ = get_real_time_traffic_data(start_location, end_location)
    if distance and duration:
        predicted_level = predict_congestion(distance, duration)
        print(f"Predicted congestion (next 10 mins): {predicted_level}")
    else:
        print("No traffic data available; replace get_real_time_traffic_data with a real API call.")
