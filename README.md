# 🌿 VayuSatya: Hyperlocal Pollution Evidence Engine

Welcome to **VayuSatya**, a premium, automated, hyperlocal air quality and pollution surge detection engine. Designed specifically to track industrial emissions in the Gujarat industrial corridors (Vapi, Ankleshwar, Vatva), VayuSatya empowers communities and authorities with automated evidence collection and real-time visualization.

## 🚀 Key Features

*   **Live Sensor Dashboard:** Stunning data visualizations combining OpenWeather wind vectors and continuous ambient air quality (CAAQMS) readings (PM2.5, SO2, CO, etc.).
*   **Surge Detection Engine:** Automatically flags unnatural pollution spikes that violate safe limits based on a 2-hour rolling baseline algorithmic approach.
*   **Source Fingerprinting Analysis:** Cross-references wind direction (back-trajectories) with known shifts at the GIDC (Gujarat Industrial Development Corporation) database to accurately identify probable polluters.
*   **Automated Form-A PDF Generation:** Eliminates red tape by instantly compiling forensic evidence into official Government form templates for the Gujarat Pollution Control Board (GSPCB). 
*   **Multilingual Support:** Seamless dashboard toggling across English, Hindi (हिन्दी), and Gujarati (ગુજરાતી) to aid local communities and Sarpanches.

## 🛠️ Technology Stack

*   **Frontend:** HTML5, Modern Vanilla CSS, Javascript.
*   **Backend:** Python 3, Flask, CORS, Pandas.
*   **APIs:** OpenWeatherMap (Wind/Meteorological data).
*   **Libraries:** Chart.js, ReportLab (PDF Generation).
*   **Storage:** JSON-based state persistence and SQLite.

## ⚡ Getting Started (Local Setup)

To run the full engine locally, you will need to start both the Python backend and the web frontend.

### 1. Start the Flask Backend API
```bash
cd backend
python app.py
```
*The API server will spin up on `http://localhost:5050`.*

### 2. Start the Frontend Application
In a separate terminal, run a static file server in the frontend directory:
```bash
cd ts-09/frontend
python -m http.server 8000
```
*Navigate to `http://localhost:8000` to interact with the full dashboard.*

## 💻 Hardware Architecture & BOM (Bill of Materials)
To fulfill the requirements of a low-cost, scalable distributed sensor network, each node is engineered to cost **under ₹2,500**. 
*   **Microcontroller:** ESP32 (Wi-Fi enabled) — ~₹450
*   **Dust Sensor:** Plantower PMS5003 (PM2.5 / PM10) — ~₹1,400
*   **Gas Sensor:** Winsen MQ136 (SO2 detection) — ~₹400
*   **Enclosure & Misc:** PVC Housing + 5V Power Supply — ~₹100
*   **Total Cost Per Node:** **₹2,350** 

## 📂 Project Architecture
*   **`/backend/app.py`**: The central nervous system, processing live feeds, generating synthetic test alerts, and dispensing automated PDFs.
*   **`/backend/vayusatya_1.py`**: Advanced data science and Machine Learning script compiling raw CPCB datasets into fingerprint topologies.
*   **`/ts-09/frontend/`**: Contains the lightning-fast, zero-dependency visual interface built to dynamically ingest the backend's routines.
*   **`/vayusatya_api/`**: Alternative FastAPI backend architecture implementation.

## 🤝 Contributing
Contributions, issues, and feature requests are highly welcome. Start tracking the truth in the air around you!
