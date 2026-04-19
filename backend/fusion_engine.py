import json
import math
from datetime import datetime
from simulator import infer_source_direction, get_wind_direction_label

# Load industries
with open("data/industries.json") as f:
    INDUSTRIES = json.load(f)

def is_industry_active(industry, dt=None):
    if dt is None:
        dt = datetime.now()
    current_time = dt.strftime("%H:%M")
    for shift in industry["shifts"]:
        start = shift["start"]
        end = shift["end"]
        if start <= end:
            if start <= current_time <= end:
                return True
        else:  # overnight shift
            if current_time >= start or current_time <= end:
                return True
    return False

def bearing_difference(b1, b2):
    """Smallest angle between two bearings (0-180)"""
    diff = abs(b1 - b2) % 360
    return min(diff, 360 - diff)

def find_probable_sources(village, wind_direction_deg, surge_reading):
    source_info = infer_source_direction(wind_direction_deg)
    source_bearing = source_info["source_bearing"]

    village_industries = [i for i in INDUSTRIES if i["village"] == village]
    candidates = []

    for ind in village_industries:
        angle_diff = bearing_difference(ind["direction_from_village_deg"], source_bearing)
        active = is_industry_active(ind)
        has_so2 = "SO2" in ind["pollutants"]
        surge_so2 = surge_reading.get("so2", 0) > 30

        # Score: lower angle diff = more likely match
        if angle_diff <= 45:  # within 45 degrees of upwind direction
            match_score = 100 - angle_diff
            if active:
                match_score += 30
            if has_so2 and surge_so2:
                match_score += 25
            candidates.append({
                **ind,
                "angle_from_upwind": round(angle_diff, 1),
                "is_active": active,
                "match_score": round(match_score, 1)
            })

    candidates.sort(key=lambda x: x["match_score"], reverse=True)
    return candidates, source_info

def classify_source_type(reading, hour=None):
    if hour is None:
        hour = datetime.now().hour
    pm25 = reading.get("pm25", 0)
    so2 = reading.get("so2", 0)

    # Industrial: SO2 spike + PM2.5 spike during working hours
    if so2 > 30 and pm25 > 80:
        return {
            "type": "Industrial",
            "confidence": "HIGH",
            "reason": f"SO2 ({so2} µg/m³) and PM2.5 ({pm25} µg/m³) both elevated — typical of chemical/factory emissions"
        }
    # Agricultural: PM2.5 spike at dawn/dusk without SO2, seasonal
    elif pm25 > 80 and so2 < 15 and (4 <= hour <= 9 or 17 <= hour <= 21):
        return {
            "type": "Agricultural / Crop Burning",
            "confidence": "MODERATE",
            "reason": f"PM2.5 elevated ({pm25} µg/m³) with low SO2 at typical burning hours — likely agricultural burning"
        }
    elif pm25 > 60:
        return {
            "type": "Mixed / Unconfirmed",
            "confidence": "LOW",
            "reason": f"PM2.5 elevated ({pm25} µg/m³) but insufficient SO2 data to confirm industrial source"
        }
    else:
        return {
            "type": "Background",
            "confidence": "HIGH",
            "reason": "Readings within normal range — no significant pollution event detected"
        }

def run_fusion(reading):
    """Main fusion engine — takes a sensor reading and returns full analysis"""
    village = reading["village"]
    wind_dir = reading["wind_direction"]
    pm25 = reading["pm25"]
    so2 = reading["so2"]

    source_type_info = classify_source_type(reading)
    candidates, source_info = find_probable_sources(village, wind_dir, reading)

    top_source = candidates[0] if candidates else None

    return {
        "village": village,
        "timestamp": reading["timestamp"],
        "pm25": pm25,
        "so2": so2,
        "wind_direction_deg": wind_dir,
        "wind_from": source_info["wind_from_label"],
        "source_bearing": source_info["source_bearing"],
        "source_direction": source_info["source_direction_label"],
        "source_type": source_type_info,
        "probable_industries": candidates[:3],  # top 3 candidates
        "top_probable_source": top_source,
        "alert_level": "SEVERE" if pm25 > 200 else "HIGH" if pm25 > 120 else "MODERATE" if pm25 > 60 else "NORMAL"
    }
