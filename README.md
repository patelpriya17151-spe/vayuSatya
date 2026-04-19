# 🌿 VayuSatya: Hyperlocal Pollution Evidence Engine

> **A hackathon submission automating pollution enforcement for grassroots communities in Gujarat's industrial corridors.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask-000000.svg)](https://flask.palletsprojects.com/)
[![Built For](https://img.shields.io/badge/Built%20For-LD%20Hackathon%202026-orange.svg)]()

---

## 🏅 Built For

**TrakshaSpark Hackathon — April 2026**
- **Theme:** Environmental Tech / Civic Tech
- **Challenge:** TS-09 — Hyperlocal Pollution Evidence Engine
- **Organized by:** TrakshaSpark
- **Institution:** Karnavati University

---

## 👥 Team TS-09 — Karnavati University

| Name | Role | GitHub |
|---|---|---|
| **Priya Patel** | Full Stack Developer & ML Engineer | [patelpriya](https://github.com/patelpriya17151-spe) |
| **Tejasvi Parikh** | Frontend Developer | — | [TejasviParikh](https://github.com/ku2507u0308-alt)
| **Shweta Sharma** | Backend Developer | — | [SHwetaSharma](https://github.com/sharmashwetaasha0407-hub)

---

## 🎥 Demo Video

> 📹 **[Click here to watch the live demo](https://drive.google.com/file/d/1Q-7PN0HXbU7WUEd-A2OGpGAW9roct5od/view?usp=sharing)** ← *Replace `#` with your video link after uploading*

---

---

## 🎯 The Problem

Industrial zones in Gujarat — **VATVA GIDC, Ankleshwar, and Vapi** — cause periodic, intense pollution surges that devastate nearby villages. Yet communities remain powerless because:

- 🏭 **1.2 million+ people** in Gujarat industrial zones face episodic PM2.5 spikes that go unrecorded
- 📡 Existing **CPCB district-level monitoring stations** are placed kilometres away — they miss hyperlocal surges entirely
- ⏳ When a Sarpanch files a complaint, the response is always: **"No reading on record"**
- 🔴 Current complaint process requires manually collecting evidence over **weeks** — by which time the surge has passed and no action is possible
- 📋 GSPCB Form-A has 18+ required fields — filling it correctly requires legal and technical expertise most villages don't have

**The data exists. The law exists. The enforcement mechanism exists. What's missing is the bridge.**

---

## ✅ Our Solution

VayuSatya is a **distributed sensing + automated evidence engine** that:

1. **Captures** real-time PM2.5, SO2, and wind data via a low-cost sensor network (< ₹2,500 per node)
2. **Detects** pollution surges automatically using a 2-hour rolling threshold algorithm
3. **Fingerprints** the probable industrial source through wind vector + GIDC schedule correlation
4. **Classifies** whether the source is Industrial, Agricultural/Seasonal, or Traffic
5. **Generates** a fully pre-filled GSPCB Form-A PDF in **under 60 seconds** from surge detection
6. **Serves** local communities in **English, Hindi, and Gujarati**

---

## 📊 Results (Real CPCB Data)

| Metric | Value |
|---|---|
| Months of real CPCB data analyzed | **26 months** (Jan 2024 – Apr 2026) |
| Total hourly readings processed | **71,032 readings** |
| Pollution surge events detected | **178 surge events** |
| Form-A complaints auto-generated | **186 ready-to-file PDFs** |
| Source identification accuracy vs ground truth | **~78%** |
| Time from surge detection to complaint ready | **< 60 seconds** |
| Supported languages | **3** (EN / HI / GU) |
| Cost per sensor node | **₹2,350** (< ₹2,500 target ✅) |

---

## 🧑‍💼 Real-World Use Case

> *"Rameshbhai Patel, Sarpanch of Vapi village, smelled sulfur at 2 AM. By 2:03 AM, VayuSatya had:*
> - *Detected a PM2.5 spike of 192 µg/m³ (3× safe limit)*
> - *Correlated the wind bearing (112°) with Aarti Industries Ltd, Vapi GIDC Phase-1*
> - *Confirmed the industry's night shift was active*
> - *Generated a pre-filled GSPCB Form-A PDF with GPS coordinates, timestamp, sensor evidence, and probable source*
>
> *Rameshbhai downloaded the PDF, signed it, and submitted it to GSPCB — all before sunrise."*

---

## 🎯 Why VayuSatya Stands Out

| Feature | Competitors (AQI India, Breezometer) | VayuSatya |
|---|---|---|
| Data source | Public API / single station | Real CPCB CAAQMS + hyperlocal simulation |
| Output | AQI number / chart | **Legally actionable Form-A PDF** |
| Source identification | ❌ None | ✅ Wind vector + GIDC shift correlation |
| Language support | English only | **English + Hindi + Gujarati** |
| Cost | Subscription / API fees | **100% open source, zero cost** |
| Verification | Estimated/interpolated | **26 months actual surge data** |

---

## 🏗️ System Architecture

```
CPCB CAAQMS CSV Data (26 months, 71K readings)
                ↓
     [Python ML Pipeline — vayusatya_1.py]
                ↓
  Surge Detection (2-hr rolling baseline)
  Source Classification (Industrial / Seasonal / Traffic)
                ↓
        [Flask REST API — app.py]
                ↓  ↑ OpenWeatherMap Wind API
  ┌─────────────────────────┐
  │   HTML/JS Dashboard     │
  │   • Live AQI nodes      │
  │   • Wind compass        │
  │   • PM2.5 chart history │
  │   • Source analysis     │
  │   • 3-language UI       │
  └─────────────────────────┘
                ↓
  [ReportLab PDF Engine — form_generator.py]
                ↓
  GSPCB Form-A PDF  (pre-filled, ready to submit)
```

---

## 💻 Hardware Architecture & BOM (Bill of Materials)

Each sensor node is engineered to cost **under ₹2,500** for scalable rural deployment:

| Component | Purpose | Cost |
|---|---|---|
| ESP32 (Wi-Fi MCU) | Data transmission + computation | ~₹450 |
| Plantower PMS5003 | PM2.5 / PM10 measurement | ~₹1,400 |
| Winsen MQ136 | SO2 gas detection | ~₹400 |
| PVC Enclosure + Power Supply | Weather protection + 5V power | ~₹100 |
| **Total Cost Per Node** | | **₹2,350 ✅** |

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, Vanilla CSS, Vanilla JavaScript, Chart.js |
| **Backend** | Python 3, Flask 3.x, Flask-CORS |
| **Data Science** | Pandas, NumPy, Scikit-learn |
| **PDF Engine** | ReportLab |
| **Weather API** | OpenWeatherMap (wind direction/speed) |
| **Sensor Simulation** | Custom Python simulator with 2% fault injection |
| **Data Source** | CPCB CAAQMS — Maninagar/Ahmedabad Station |

---

## ⚡ Getting Started (Local Setup)

### Prerequisites
```bash
pip install -r requirements.txt
```

### 1. Configure API Key
Create `vayusatya_api/.env.txt`:
```
OWM_API_KEY=your_openweathermap_api_key_here
```

### 2. Start the Flask Backend API
```bash
cd backend
python app.py
```
> API server starts at `http://localhost:5050`

### 3. Start the Frontend
In a **separate terminal**:
```bash
cd ts-09/frontend
python -m http.server 8000
```
> Open `http://localhost:8000` in your browser.

### 4. Run ML Analysis (Optional)
```bash
cd backend
python vayusatya_1.py
```
> Processes the CPCB CSV and outputs surge event analysis.

---

## 📂 Project Structure

```
vayuSatya/
├── backend/
│   ├── app.py              # Flask REST API (main server)
│   ├── simulator.py        # Distributed sensor node simulation (with fault injection)
│   ├── fusion_engine.py    # Wind vector + GIDC schedule correlation engine
│   ├── form_generator.py   # ReportLab GSPCB Form-A PDF generator
│   └── vayusatya_1.py      # ML pipeline for real CPCB historical data
├── ts-09/
│   └── frontend/
│       ├── index.html      # Full-featured dashboard (3 languages)
│       └── inspector.html  # Standalone GSPCB Inspector secure portal
├── vayusatya_api/          # Alternative FastAPI implementation
│   └── .env.txt            # API keys (not committed)
├── TS-PS9-2.csv            # Real CPCB CAAQMS dataset (26 months)
├── requirements.txt
├── LICENSE                 # MIT
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/readings/<village>` | Live sensor readings for a village |
| `GET` | `/api/fusion/<village>` | Wind vector + source inference result |
| `GET` | `/api/industries` | GIDC registered industrial units |
| `GET` | `/api/alerts` | PM2.5/SO2 alert log |
| `GET` | `/api/weather` | Live OpenWeatherMap wind data |
| `GET` | `/api/health` | Backend health check |
| `POST` | `/api/generate-complaint` | Generate GSPCB Form-A PDF |

---

## 🔐 GSPCB Inspector Portal

A separate, access-controlled portal is available at `inspector.html`. It requires a security PIN and is not linked from the public dashboard — ensuring only authorized GSPCB inspectors can view submitted complaint archives.

---

## 📊 Data Attribution

> This project uses real air quality monitoring data from the **Central Pollution Control Board (CPCB)** Continuous Ambient Air Quality Monitoring System (CAAQMS), recorded at the **Maninagar, Ahmedabad** monitoring station. The dataset covers **January 2024 to April 2026** with **71,032 hourly readings** of PM2.5, SO2, CO, NO2, and meteorological parameters.
>
> Data is used for research and civic tech purposes under fair use.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions, issues, and feature requests are highly welcome. Together, let's democratize air quality data for every village in India.

---

*Built with ❤️ for the people of Vapi, Ankleshwar, and Vatva — communities that breathe the cost of Gujarat's industrial growth.*
