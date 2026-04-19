import io
import os
import json
import requests
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

OWM_API_KEY = os.getenv("OWM_API_KEY", "")
LAT = 22.9968
LON = 72.5974
POLLUTANTS = ['PM25', 'PM10', 'NO', 'NO2', 'NOx', 'SO2', 'CO']

AQI_BREAKPOINTS = [
    (0,   30,   0,   50),
    (30,  60,  51,  100),
    (60,  90, 101,  200),
    (90, 120, 201,  300),
    (120, 250, 301, 400),
    (250, 500, 401, 500),
]

def calc_aqi(pm25):
    if pd.isna(pm25): return np.nan
    for c_lo, c_hi, a_lo, a_hi in AQI_BREAKPOINTS:
        if c_lo <= pm25 <= c_hi:
            return round(((a_hi - a_lo) / (c_hi - c_lo)) * (pm25 - c_lo) + a_lo, 1)
    return 500.0

def aqi_category(aqi):
    if pd.isna(aqi):  return 'Unknown'
    if aqi <= 50:     return 'Good'
    if aqi <= 100:    return 'Satisfactory'
    if aqi <= 200:    return 'Moderate'
    if aqi <= 300:    return 'Poor'
    if aqi <= 400:    return 'Very Poor'
    return 'Severe'

def get_season(month):
    if month in [12, 1, 2]:   return 'Winter'
    if month in [3, 4, 5]:    return 'Summer'
    if month in [6, 7, 8, 9]: return 'Monsoon'
    return 'Post-Monsoon'

def get_time_of_day(hour):
    if 5  <= hour < 10: return 'Morning_Rush'
    if 10 <= hour < 17: return 'Daytime'
    if 17 <= hour < 21: return 'Evening_Rush'
    return 'Night'

def process_stations_csv(content: bytes) -> list:
    df = pd.read_csv(io.StringIO(content.decode('utf-8')), skiprows=2, header=0)
    df.columns = ['SNo', 'State', 'City', 'Station_Name', 'Status']
    df = df[df['SNo'] != 'S.No.'].copy().reset_index(drop=True)
    df['State'] = df['State'].ffill()
    df['City']  = df['City'].ffill()
    df['Status'] = df['Status'].str.strip()
    gujarat = df[df['State'].str.contains('Gujarat', na=False, case=False)]
    return gujarat[['City', 'Station_Name', 'Status']].to_dict(orient='records')

def process_data(content: bytes) -> pd.DataFrame:
    df_raw = pd.read_csv(io.StringIO(content.decode('utf-8')), skiprows=16, header=0)
    df_raw.columns = ['From_Date', 'To_Date', 'PM25', 'PM10', 'NO', 'NO2', 'NOx', 'SO2', 'CO']
    df_raw['timestamp'] = pd.to_datetime(df_raw['From_Date'], format='%d-%m-%Y %H:%M', errors='coerce')
    df_raw = df_raw.dropna(subset=['timestamp'])
    for col in POLLUTANTS:
        df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce')
    df_raw = df_raw.set_index('timestamp').sort_index()
    df_clean = df_raw.copy()
    for col in POLLUTANTS:
        df_clean[col] = df_clean[col].where(df_clean[col] < 999, other=np.nan)
        df_clean[col] = df_clean[col].where(df_clean[col] >= 0,  other=np.nan)
    for col in POLLUTANTS:
        df_clean[col] = df_clean[col].interpolate(method='linear', limit=8, limit_direction='forward')
    df_clean['hour']        = df_clean.index.hour
    df_clean['day_of_week'] = df_clean.index.dayofweek
    df_clean['month']       = df_clean.index.month
    df_clean['year']        = df_clean.index.year
    df_clean['is_weekend']  = df_clean['day_of_week'].isin([5, 6]).astype(int)
    df_clean['season']      = df_clean['month'].apply(get_season)
    df_clean['time_of_day'] = df_clean['hour'].apply(get_time_of_day)
    df_clean['AQI']         = df_clean['PM25'].apply(calc_aqi)
    df_clean['AQI_cat']     = df_clean['AQI'].apply(aqi_category)
    return df_clean

def classify_source(row) -> str:
    so2  = row['mean_SO2']  if pd.notna(row.get('mean_SO2'))  else 0
    no2  = row['mean_NO2']  if pd.notna(row.get('mean_NO2'))  else 0
    co   = row['mean_CO']   if pd.notna(row.get('mean_CO'))   else 0
    pm25 = row['peak_PM25']
    if so2 > 40 and pm25 > 80:    return 'Industrial'
    if no2 > 55 and co > 1.0:     return 'Traffic'
    if pm25 > 100 and so2 < 20:   return 'Dust/Biomass'
    return 'Mixed'

def probable_source_location(source_type: str, time_of_day: str) -> str:
    if source_type == 'Industrial':   return 'Vatva GIDC (SE of Maninagar) or Naroda industrial area'
    if source_type == 'Traffic':      return 'Maninagar arterial roads (morning/evening rush)'
    if source_type == 'Dust/Biomass': return 'Outskirts or upstream agricultural burn (seasonal)'
    return 'Multiple sources — further monitoring needed'

def detect_events(df_clean: pd.DataFrame) -> pd.DataFrame:
    df = df_clean.copy()
    df['PM25_baseline'] = df['PM25'].rolling(window=8, min_periods=4).mean()
    df['is_surge'] = (df['PM25'] > df['PM25_baseline'] + 30) & df['PM25'].notna()
    df['surge_group'] = df['is_surge'].astype(int).diff().ne(0).cumsum()
    surge_events = (
        df[df['is_surge']]
        .groupby('surge_group')
        .agg(
            start       =('PM25', lambda x: x.index[0]),
            end         =('PM25', lambda x: x.index[-1]),
            peak_PM25   =('PM25', 'max'),
            mean_PM25   =('PM25', 'mean'),
            mean_SO2    =('SO2',  'mean'),
            mean_NO2    =('NO2',  'mean'),
            mean_CO     =('CO',   'mean'),
            mean_NOx    =('NOx',  'mean'),
            readings    =('PM25', 'count'),
            season      =('season', lambda x: x.mode()[0]),
            time_of_day =('time_of_day', lambda x: x.mode()[0]),
        )
        .reset_index(drop=True)
    )
    surge_events = surge_events[surge_events['readings'] >= 2].copy()
    surge_events['duration_min'] = (surge_events['end'] - surge_events['start']).dt.total_seconds() / 60 + 15
    surge_events['source_type']     = surge_events.apply(classify_source, axis=1)
    surge_events['probable_source'] = surge_events.apply(
        lambda r: probable_source_location(r['source_type'], r['time_of_day']), axis=1
    )
    return surge_events

def build_daily_summary(df_clean: pd.DataFrame) -> list:
    daily = (
        df_clean[POLLUTANTS + ['AQI', 'AQI_cat', 'season']]
        .resample('1D')
        .agg({
            'PM25':    ['mean', 'max', 'min'],
            'PM10':    'mean', 'SO2': 'mean', 'NO2': 'mean', 'CO': 'mean',
            'AQI':     'mean',
            'AQI_cat': lambda x: x.mode()[0] if len(x) > 0 else 'Unknown',
            'season':  lambda x: x.mode()[0] if len(x) > 0 else 'Unknown',
        })
    )
    daily.columns = ['_'.join(c).strip('_') for c in daily.columns]
    daily = daily.reset_index()
    daily['date'] = daily['timestamp'].dt.strftime('%Y-%m-%d')
    return daily.drop(columns=['timestamp']).round(2).to_dict(orient='records')

def build_monthly_summary(df_clean: pd.DataFrame) -> list:
    monthly = df_clean.groupby(['year', 'month'])['PM25'].mean().round(2).reset_index()
    monthly['date_label'] = monthly.apply(lambda r: f"{int(r['year'])}-{int(r['month']):02d}", axis=1)
    return monthly.round(2).to_dict(orient='records')

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

def fetch_weather() -> dict | None:
    if not OWM_API_KEY or OWM_API_KEY == "PASTE_YOUR_KEY_HERE":
        return None
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={OWM_API_KEY}&units=metric"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get('cod') != 200:
            return None
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
        return weather
    except Exception:
        return None

def generate_form_a_pdf(surge_row: dict, complainant_name="[To be filled]",
                         village="Maninagar, Ahmedabad", contact="[To be filled]",
                         output_path="GSPCB_FormA_Complaint.pdf") -> str:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER

    doc    = SimpleDocTemplate(output_path, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm, leftMargin=2*cm, rightMargin=2*cm)
    styles = getSampleStyleSheet()
    story  = []

    h  = ParagraphStyle('h',  parent=styles['Title'],  fontSize=13, spaceAfter=4,  alignment=TA_CENTER)
    sh = ParagraphStyle('sh', parent=styles['Normal'], fontSize=10, spaceAfter=2,  alignment=TA_CENTER)
    sc = ParagraphStyle('sc', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold',
                        textColor=colors.white, backColor=colors.HexColor('#1a1a2e'),
                        spaceAfter=4, spaceBefore=8, leftIndent=6)

    story += [
        Paragraph("GUJARAT POLLUTION CONTROL BOARD", h),
        Paragraph("FORM-A — COMPLAINT REGARDING AIR POLLUTION", h),
        Paragraph("Under Environment (Protection) Act, 1986 | Rule 14", sh),
        Spacer(1, 0.4*cm),
    ]

    src = surge_row.get('source_type', 'Mixed')
    source_locations = {
        'Industrial':   'Vatva GIDC Phase-4 / Naroda industrial zone (SE of Maninagar)',
        'Traffic':      'Maninagar arterial roads — peak traffic corridor',
        'Dust/Biomass': 'Peri-urban / agricultural zone — outskirts of Ahmedabad',
        'Mixed':        'Multiple sources — further field investigation required',
    }
    ts = TableStyle([
        ('BACKGROUND',   (0,0),(-1,0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR',    (0,0),(-1,0), colors.white),
        ('FONTNAME',     (0,0),(-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0,0),(-1,-1), 9),
        ('GRID',         (0,0),(-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, colors.HexColor('#f0f4f8')]),
        ('VALIGN',       (0,0),(-1,-1), 'MIDDLE'),
        ('LEFTPADDING',  (0,0),(-1,-1), 6),
        ('TOPPADDING',   (0,0),(-1,-1), 5),
        ('BOTTOMPADDING',(0,0),(-1,-1), 5),
    ])

    story.append(Paragraph("  SECTION A — INCIDENT DETAILS", sc))
    t1 = Table([
        ['Field','Value','Remarks'],
        ['Date',     str(surge_row.get('start',''))[:10],  'Auto-detected from CAAQMS'],
        ['Time',     str(surge_row.get('start',''))[11:16],'15-min sensor interval'],
        ['Duration', f"{surge_row.get('duration_min',0):.0f} min",''],
        ['Season',   surge_row.get('season','N/A'),''],
    ], colWidths=[5*cm,5*cm,7*cm])
    t1.setStyle(ts); story.append(t1)

    story.append(Paragraph("  SECTION B — POLLUTION DATA", sc))
    so2_v = f"{surge_row['mean_SO2']:.2f} µg/m³" if surge_row.get('mean_SO2') and not pd.isna(surge_row['mean_SO2']) else "N/A"
    no2_v = f"{surge_row['mean_NO2']:.2f} µg/m³" if surge_row.get('mean_NO2') and not pd.isna(surge_row['mean_NO2']) else "N/A"
    co_v  = f"{surge_row['mean_CO']:.3f} mg/m³"  if surge_row.get('mean_CO')  and not pd.isna(surge_row['mean_CO'])  else "N/A"
    t2 = Table([
        ['Pollutant','Value','CPCB Limit','Status'],
        ['PM2.5 (Peak)', f"{surge_row.get('peak_PM25',0):.2f} µg/m³", '60 µg/m³', f"{surge_row.get('peak_PM25',0)/60*100:.0f}% of limit"],
        ['SO2 (Mean)', so2_v, '80 µg/m³',''],
        ['NO2 (Mean)', no2_v, '80 µg/m³',''],
        ['CO (Mean)',  co_v,  '4.0 mg/m³',''],
    ], colWidths=[4.5*cm,4.5*cm,4*cm,4*cm])
    t2.setStyle(ts); story.append(t2)

    story.append(Paragraph("  SECTION C — SOURCE ANALYSIS", sc))
    t3 = Table([
        ['Field','Value'],
        ['Source Type', src],
        ['Location', source_locations.get(src,'Unknown')],
        ['Method', 'SO2/NO2/CO ratio fingerprinting'],
    ], colWidths=[6*cm,11*cm])
    t3.setStyle(ts); story.append(t3)

    story.append(Paragraph("  SECTION D — COMPLAINANT", sc))
    t4 = Table([
        ['Field','Details'],
        ['Name', complainant_name],
        ['Village', village],
        ['Contact', contact],
        ['Filed', datetime.now().strftime('%d-%m-%Y')],
    ], colWidths=[6*cm,11*cm])
    t4.setStyle(ts); story.append(t4)

    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        f"Generated by CAAQMS Pollution Evidence Engine · Station: Maninagar, Ahmedabad - GPCB · {datetime.now().strftime('%d-%m-%Y %H:%M')}",
        ParagraphStyle('f', parent=styles['Normal'], fontSize=7, textColor=colors.grey, alignment=TA_CENTER)
    ))
    doc.build(story)
    return output_path