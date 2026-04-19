import random
import math
import time
from datetime import datetime

VILLAGES = {
    "Vapi": {"lat": 20.3893, "lng": 72.9106, "nodes": ["VPI-N01", "VPI-N02", "VPI-N03"]},
    "Ankleshwar": {"lat": 21.6265, "lng": 72.9966, "nodes": ["ANK-N01", "ANK-N02"]},
    "Vatva": {"lat": 22.9712, "lng": 72.6389, "nodes": ["VAT-N01", "VAT-N02", "VAT-N03"]}
}

# Sensor state tracking for realistic drift
_sensor_state = {}

def _init_sensor(node_id):
    if node_id not in _sensor_state:
        _sensor_state[node_id] = {
            "pm25_base": random.uniform(35, 55),
            "so2_base": random.uniform(8, 18),
            "wind_dir": random.uniform(200, 340),
            "wind_speed": random.uniform(5, 15),
            "surge_active": False,
            "surge_countdown": 0
        }

def _maybe_trigger_surge(state, hour):
    # Industrial surges more likely during shift changes (6am, 2pm, 10pm)
    shift_change_hours = [6, 7, 14, 15, 22, 23]
    surge_prob = 0.08 if hour in shift_change_hours else 0.02
    if not state["surge_active"] and random.random() < surge_prob:
        state["surge_active"] = True
        state["surge_countdown"] = random.randint(4, 12)  # surge lasts 4-12 readings
    if state["surge_active"]:
        state["surge_countdown"] -= 1
        if state["surge_countdown"] <= 0:
            state["surge_active"] = False
    return state["surge_active"]

def generate_reading(node_id, village, force_surge=False):
    _init_sensor(node_id)
    state = _sensor_state[node_id]
    now = datetime.now()
    hour = now.hour

    # Drift the base values slowly
    state["pm25_base"] += random.uniform(-1.5, 1.5)
    state["pm25_base"] = max(20, min(80, state["pm25_base"]))
    state["so2_base"] += random.uniform(-0.5, 0.5)
    state["so2_base"] = max(5, min(25, state["so2_base"]))

    # Wind drift
    state["wind_dir"] += random.uniform(-8, 8)
    state["wind_dir"] = state["wind_dir"] % 360
    state["wind_speed"] += random.uniform(-1, 1)
    state["wind_speed"] = max(2, min(25, state["wind_speed"]))

    is_surge = force_surge or _maybe_trigger_surge(state, hour)

    if is_surge:
        pm25 = state["pm25_base"] + random.uniform(80, 220)
        so2 = state["so2_base"] + random.uniform(25, 90)
        surge_intensity = "HIGH" if pm25 > 200 else "MODERATE"
    else:
        pm25 = state["pm25_base"] + random.uniform(-5, 5)
        so2 = state["so2_base"] + random.uniform(-2, 2)
        surge_intensity = None

    pm25 = round(max(0, pm25), 1)
    so2 = round(max(0, so2), 1)

    # AQI calculation (simplified Indian AQI for PM2.5)
    if pm25 <= 30:
        aqi = round(pm25 * 50 / 30)
        aqi_label = "Good"
        aqi_color = "#22c55e"
    elif pm25 <= 60:
        aqi = round(50 + (pm25 - 30) * 50 / 30)
        aqi_label = "Satisfactory"
        aqi_color = "#84cc16"
    elif pm25 <= 90:
        aqi = round(100 + (pm25 - 60) * 100 / 30)
        aqi_label = "Moderate"
        aqi_color = "#eab308"
    elif pm25 <= 120:
        aqi = round(200 + (pm25 - 90) * 100 / 30)
        aqi_label = "Poor"
        aqi_color = "#f97316"
    elif pm25 <= 250:
        aqi = round(300 + (pm25 - 120) * 100 / 130)
        aqi_label = "Very Poor"
        aqi_color = "#ef4444"
    else:
        aqi = round(400 + (pm25 - 250) * 100 / 130)
        aqi_label = "Severe"
        aqi_color = "#7c2d12"

    # Classify source
    source_type = "Industrial" if (is_surge and so2 > 30) else \
                  "Agricultural/Seasonal" if (is_surge and so2 <= 15 and (4 <= hour <= 8 or 17 <= hour <= 20)) else \
                  "Industrial" if is_surge else "Background"

    # Simulated Hardware Fault Logic
    fault_detected = False
    if random.random() < 0.02:  # 2% chance of hardware failure
        fault_detected = True
        pm25 = -1
        so2 = -1
        aqi_label = "ERR"
        aqi_color = "#9CA3AF" # Grey for offline 

    return {
        "node_id": node_id,
        "village": village,
        "timestamp": now.isoformat(),
        "lat": VILLAGES[village]["lat"] + random.uniform(-0.002, 0.002),
        "lng": VILLAGES[village]["lng"] + random.uniform(-0.002, 0.002),
        "pm25": pm25,
        "so2": so2,
        "wind_direction": round(state["wind_dir"], 1),
        "wind_speed": round(state["wind_speed"], 1),
        "aqi": min(500, aqi),
        "aqi_label": aqi_label,
        "aqi_color": aqi_color,
        "surge_detected": is_surge,
        "surge_intensity": surge_intensity,
        "source_type": source_type,
        "alert": pm25 > 60 or so2 > 40,
        "fault_detected": fault_detected
    }

def get_all_readings(force_surge_village=None):
    readings = []
    for village, info in VILLAGES.items():
        for node_id in info["nodes"]:
            force = (village == force_surge_village)
            readings.append(generate_reading(node_id, village, force_surge=force))
    return readings

def get_wind_direction_label(degrees):
    dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
    idx = round(degrees / 22.5) % 16
    return dirs[idx]

def infer_source_direction(wind_dir_degrees):
    # Wind blows FROM source TO sensor, so source is UPWIND (opposite of wind direction)
    source_dir = (wind_dir_degrees + 180) % 360
    return {
        "source_bearing": round(source_dir, 1),
        "source_direction_label": get_wind_direction_label(source_dir),
        "wind_from_label": get_wind_direction_label(wind_dir_degrees)
    }
