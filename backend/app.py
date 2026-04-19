from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import json
import os
import io
import requests
from datetime import datetime
from dotenv import load_dotenv

# Change to backend dir so imports work
os.chdir(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(os.path.dirname(__file__), '../vayusatya_api/.env.txt'))
OWM_API_KEY = os.getenv("OWM_API_KEY", "")
LAT = 22.9968
LON = 72.5974

from simulator import get_all_readings, VILLAGES, generate_reading
from fusion_engine import run_fusion, INDUSTRIES, is_industry_active
from form_generator import generate_form_a

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return """
    <html>
        <head><title>VayuSatya Backend Support</title></head>
        <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
            <h1 style="color: #10B981;">Backend is running successfully! ✅</h1>
            <p style="font-size: 18px; color: #555;">This is an API-only server without a user interface here.</p>
            <p style="font-size: 18px;">To view and interact with the application, please open the Frontend link:</p>
            <a href="http://localhost:8000" style="display: inline-block; background: #3B82F6; color: white; padding: 10px 20px; font-size: 18px; text-decoration: none; border-radius: 8px;">Go to Frontend Dashboard</a>
        </body>
    </html>
    """


# In-memory log (last 200 readings per village)
_reading_log = {v: [] for v in VILLAGES}
_alerts = []
_archives = [] # Store submitted GSPCB forms

def log_reading(reading):
    village = reading["village"]
    _reading_log[village].append(reading)
    if len(_reading_log[village]) > 200:
        _reading_log[village] = _reading_log[village][-200:]
    if reading.get("alert"):
        # Simulated SMS / WhatsApp Workflow for Sarpanch
        print(f"==================================================")
        print(f"MOCK SMS/WHATSAPP DISPATCH INITIATED")
        print(f"To: Sarpanch, {reading['village']}")
        print(f"Msg: ACTION REQUIRED. PM2.5 Alert ({reading['pm25']} µg/m³) detected at Node {reading['node_id']}.")
        print(f"==================================================", flush=True)
            
        _alerts.insert(0, {**reading, "acknowledged": False})
        if len(_alerts) > 50:
            _alerts.pop()

# ─── ENDPOINTS ───

@app.route("/api/readings", methods=["GET"])
def get_readings():
    """Get latest sensor readings for all villages"""
    force_surge = request.args.get("surge")
    readings = get_all_readings(force_surge_village=force_surge)
    for r in readings:
        log_reading(r)
    return jsonify({"readings": readings, "timestamp": datetime.now().isoformat()})

@app.route("/api/readings/<village>", methods=["GET"])
def get_village_readings(village):
    """Get latest reading + history for a specific village"""
    surge = request.args.get("surge") == "true"
    node_ids = VILLAGES.get(village, {}).get("nodes", [])
    if not node_ids:
        return jsonify({"error": "Village not found"}), 404
    readings = [generate_reading(nid, village, force_surge=surge) for nid in node_ids]
    for r in readings:
        log_reading(r)
    return jsonify({
        "village": village,
        "readings": readings,
        "history": _reading_log[village][-50:]
    })

@app.route("/api/fusion/<village>", methods=["GET"])
def get_fusion(village):
    """Run fusion engine on current reading for a village"""
    surge = request.args.get("surge") == "true"
    node_ids = VILLAGES.get(village, {}).get("nodes", [])
    if not node_ids:
        return jsonify({"error": "Village not found"}), 404

    # Get the most polluted node reading
    readings = [generate_reading(nid, village, force_surge=surge) for nid in node_ids]
    worst = max(readings, key=lambda r: r["pm25"])
    for r in readings:
        log_reading(r)

    result = run_fusion(worst)
    result["node_id"] = worst["node_id"]
    result["lat"] = worst["lat"]
    result["lng"] = worst["lng"]
    result["aqi"] = worst["aqi"]
    result["aqi_label"] = worst["aqi_label"]
    result["wind_speed"] = worst["wind_speed"]
    return jsonify(result)

@app.route("/api/generate-complaint", methods=["POST"])
def generate_complaint():
    """Generate GSPCB Form-A PDF"""
    data = request.json
    fusion_result = data.get("fusion_result", {})
    sarpanch_name = data.get("sarpanch_name", "")
    village_name = data.get("village_name", "")
    gram_panchayat = data.get("gram_panchayat", "")

    pdf_buffer = generate_form_a(fusion_result, sarpanch_name, village_name, gram_panchayat)

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"GSPCB_FormA_{village_name}_{ts}.pdf"
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )

@app.route("/api/industries", methods=["GET"])
def get_industries():
    village = request.args.get("village")
    now = datetime.now()
    result = []
    for ind in INDUSTRIES:
        if village and ind["village"] != village:
            continue
        result.append({**ind, "currently_active": is_industry_active(ind, now)})
    return jsonify({"industries": result})

import random

@app.route("/api/submit-complaint", methods=["POST"])
def submit_complaint():
    """Mock one-step direct API submission to GSPCB Headquarter Servers"""
    data = request.json
    ticket_id = f"GSPCB-2026-{random.randint(1000, 9999)}"
    
    archive_entry = {
        "ticket_id": ticket_id,
        "village": data.get("village", "Unknown"),
        "timestamp": datetime.now().isoformat(),
        "status": "Submitted & Awaiting Inspection",
        "data": data
    }
    _archives.insert(0, archive_entry)
    
    return jsonify({
        "status": "success",
        "ticket_id": ticket_id,
        "message": "Form-A successfully transmitted to GSPCB."
    })

@app.route("/api/archives", methods=["GET"])
def get_archives():
    """Fetch archived Form-A submissions for Admin UI"""
    return jsonify({"archives": _archives})

@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    return jsonify({"alerts": _alerts[:20]})

@app.route("/api/villages", methods=["GET"])
def get_villages():
    return jsonify({"villages": list(VILLAGES.keys()),
                    "details": VILLAGES})

def wind_direction_to_label(deg: float) -> str:
    dirs = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
    return dirs[round(deg / 22.5) % 16]

def check_industrial_risk(wind_deg: float, wind_speed: float) -> tuple:
    if wind_speed < 0.5:
        return "CALM", "Wind too calm for directional inference. Monitor all pollutants."
    source_dir = (wind_deg + 180) % 360
    if 110 <= source_dir <= 160:
        return "HIGH", f"Pollution likely from SE ({source_dir:.0f}°) — VATVA GIDC zone. Check SO2."
    elif 290 <= source_dir <= 340:
        return "MODERATE", f"Pollution from NW ({source_dir:.0f}°) — Naroda area. Monitor PM2.5."
    return "LOW", f"Wind source: {source_dir:.0f}° ({wind_direction_to_label(source_dir)}). No major industrial zone upwind."

@app.route("/api/nodes/<node_id>/maintenance", methods=["POST"])
def dispatch_maintenance(node_id):
    """Workflow-based fault resolution dispatch"""
    # Logic: Mark the node as 'dispatched' or 'repair in progress'
    # In a real system, this would trigger a technician notification
    return jsonify({
        "status": "success",
        "message": f"Maintenance dispatch ticket created for Node {node_id}.",
        "dispatched_at": datetime.now().isoformat(),
        "technician": "VayuSatya Rapid Response Team (Valsad/Bharuch)"
    })

@app.route("/api/bom", methods=["GET"])
def get_bom():
    """Bill of Materials justification for sensor nodes (< ₹2,500 target)"""
    return jsonify({
        "target_cost": 2500,
        "currency": "INR",
        "components": [
            {"part": "Plantower PMS5003 (PM2.5 Sensor)", "cost": 1400, "verified": True},
            {"part": "Winsen MQ136 (SO2 Electrochemical Sensor)", "cost": 420, "verified": True},
            {"part": "ESP32 WROOM (Wi-Fi/BT MCU)", "cost": 380, "verified": True},
            {"part": "Enclosure & Power Supply (5V/2A)", "cost": 150, "verified": True}
        ],
        "total": 2350,
        "justification": "Low-cost distributed architecture allows for hyperlocal sensing at 1/50th the cost of CAAQMS stations."
    })

@app.route("/api/weather", methods=["GET"])
def get_weather():
    if not OWM_API_KEY:
        return jsonify({"status": "unavailable", "message": "Set OWM_API_KEY"}), 500
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={OWM_API_KEY}&units=metric"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get('cod') != 200:
            return jsonify({"status": "error", "message": data.get('message')}), 500
        weather = {
            'temperature_c':      round(data['main']['temp'], 1),
            'humidity_pct':       data['main']['humidity'],
            'wind_speed_ms':      round(data['wind']['speed'], 2),
            'wind_direction_deg': data['wind'].get('deg', 0),
            'weather_desc':       data['weather'][0]['description'],
        }
        risk, message = check_industrial_risk(weather['wind_direction_deg'], weather['wind_speed_ms'])
        weather['risk_level']   = risk
        weather['risk_message'] = message
        return jsonify({"status": "success", **weather})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "time": datetime.now().isoformat()})

if __name__ == "__main__":
    print("TS-09 Backend running on http://localhost:5050")
    app.run(debug=False, port=5050, host="0.0.0.0")
