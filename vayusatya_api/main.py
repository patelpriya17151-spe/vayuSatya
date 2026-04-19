import io
import os
import json
import sqlite3
import tempfile
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd

from vayusatya_logic import (
    process_data, process_stations_csv, detect_events,
    build_daily_summary, build_monthly_summary,
    generate_form_a_pdf, fetch_weather
)

app = FastAPI(title="Vayusatya Air Quality API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "vayusatya.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            filename    TEXT,
            total_rows  INTEGER,
            avg_aqi     REAL,
            max_pm25    REAL,
            surge_count INTEGER,
            date_range  TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()


@app.get("/")
def root():
    return {"status": "running", "docs": "/docs"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files accepted.")
    try:
        contents = await file.read()
        df_clean = process_data(contents)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"CSV parse error: {e}")

    surge_events    = detect_events(df_clean)
    daily_summary   = build_daily_summary(df_clean)
    monthly_summary = build_monthly_summary(df_clean)

    recent = df_clean.iloc[-672:].reset_index()
    recent['timestamp'] = recent['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    recent_json = recent[['timestamp','PM25','PM10','NO','NO2','NOx','SO2','CO',
                           'AQI','AQI_cat','season','time_of_day']].round(2).to_dict(orient='records')

    surge_export = surge_events.copy()
    surge_export['start'] = surge_export['start'].dt.strftime('%Y-%m-%d %H:%M')
    surge_export['end']   = surge_export['end'].dt.strftime('%Y-%m-%d %H:%M')
    surge_list = surge_export.round(2).to_dict(orient='records')

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO analyses (filename,total_rows,avg_aqi,max_pm25,surge_count,date_range) VALUES (?,?,?,?,?,?)",
            (
                file.filename, len(df_clean),
                round(float(df_clean['AQI'].mean()), 2) if df_clean['AQI'].notna().any() else None,
                round(float(df_clean['PM25'].max()), 2) if df_clean['PM25'].notna().any() else None,
                len(surge_events),
                f"{df_clean.index.min().date()} to {df_clean.index.max().date()}"
            )
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB write failed (non-fatal): {e}")

    return {
        "status":         "success",
        "filename":       file.filename,
        "total_readings": len(df_clean),
        "date_range":     {"start": str(df_clean.index.min().date()), "end": str(df_clean.index.max().date())},
        "aqi_summary": {
            "avg_aqi":  round(float(df_clean['AQI'].mean()), 2) if df_clean['AQI'].notna().any() else None,
            "avg_pm25": round(float(df_clean['PM25'].mean()), 2) if df_clean['PM25'].notna().any() else None,
            "max_pm25": round(float(df_clean['PM25'].max()), 2) if df_clean['PM25'].notna().any() else None,
            "category": df_clean['AQI_cat'].mode()[0] if len(df_clean) > 0 else "Unknown",
        },
        "surge_summary": {
            "total":     len(surge_events),
            "by_source": surge_events['source_type'].value_counts().to_dict() if len(surge_events) > 0 else {},
        },
        "surge_events":    surge_list,
        "daily_summary":   daily_summary,
        "monthly_summary": monthly_summary,
        "recent_7days":    recent_json,
    }


@app.post("/analyze/stations")
async def analyze_stations(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files accepted.")
    contents = await file.read()
    try:
        stations = process_stations_csv(contents)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Station CSV parse error: {e}")
    return {"status": "success", "gujarat_stations": stations, "count": len(stations)}


@app.get("/weather")
def get_weather():
    weather = fetch_weather()
    if weather is None:
        return {"status": "unavailable", "message": "Set OWM_API_KEY in .env file."}
    return {"status": "success", **weather}


@app.post("/generate-pdf")
async def generate_pdf(
    surge_data:       str = Form(...),
    complainant_name: str = Form(default="[To be filled]"),
    village:          str = Form(default="Maninagar, Ahmedabad"),
    contact:          str = Form(default="[To be filled]"),
):
    try:
        surge_row = json.loads(surge_data)
    except Exception:
        raise HTTPException(status_code=400, detail="surge_data must be valid JSON.")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_path = tmp.name

    try:
        generate_form_a_pdf(
            surge_row=surge_row,
            complainant_name=complainant_name,
            village=village,
            contact=contact,
            output_path=pdf_path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")

    return FileResponse(pdf_path, media_type="application/pdf",
                        filename=f"GSPCB_FormA_{str(surge_row.get('start',''))[:10]}.pdf")


@app.get("/history")
def get_history():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id,filename,total_rows,avg_aqi,max_pm25,surge_count,date_range,created_at "
        "FROM analyses ORDER BY created_at DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return [{"id":r[0],"filename":r[1],"total_rows":r[2],"avg_aqi":r[3],
             "max_pm25":r[4],"surge_count":r[5],"date_range":r[6],"created_at":r[7]} for r in rows]