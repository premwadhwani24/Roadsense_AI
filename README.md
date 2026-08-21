# 🛣️ RoadSense AI — Next-Gen Smart Road Infrastructure Management

RoadSense AI is a comprehensive, next-generation smart infrastructure management ecosystem designed to transform how cities monitor, maintain, and audit their road networks. Built for high-stakes environments like the **Smart India Hackathon (SIH)**, it integrates advanced AI, Computer Vision, IoT telemetry, and Blockchain auditing into a unified, actionable dashboard.

---

## 🌟 The Vision
Traditional road maintenance is reactive, expensive, and often lacks transparency. **RoadSense AI** shifts the paradigm to **Proactive & Prescriptive Maintenance**. By fusing data from citizen reports, vehicle sensors, and satellite/CV imagery, the system predicts failures before they happen and prescribes the most cost-effective repair strategies.

---

## 🚀 Key Modules & Capabilities

### 🧠 1. AI Prediction & Material Deterioration Engine
- **Deterioration Modeling**: Forecasts road health over 30, 60, and 90-day windows.
- **Material-Specific Wear Analysis**: Calculates risk scores for Asphalt, Concrete, and PCC (Portland Cement Concrete) under moisture and traffic stress.
- **Accident Risk Mapping**: Identifies high-risk zones using historical data and spatial analysis.
- **Pothole Forecasting**: Spatial prediction of likely defect formations using environmental stressors.

### 🚥 2. Adaptive Traffic Signal Control
- **Dynamic Green-Light Timing**: Optimizes signal green durations (15s to 60s) in real time based on intersection vehicle counts and queue lengths (`traffic_engine.py`).
- **Hazard-Avoidance Navigation**: Reroutes urban traffic away from `RED` critical road defect zones to prevent gridlocks and accidents.

### 🎙️ 3. Field Engineer Voice Dispatch & Sentiment Analysis
- **AI Audio Reporting**: Allows field crews to submit spoken defect notes via voice memos or transcripts.
- **Urgency Sentiment Scoring**: Automatically classifies reports into `HIGH_URGENCY`, `MEDIUM_URGENCY`, and `ROUTINE` priority queues.

### 👁️ 4. Computer Vision & Defect Asset Gallery
- **Deep Learning Defects**: Real-time detection of cracks, potholes, and surface wear from mobile/CCTV feeds.
- **Defect Asset Gallery**: Serves categorized defect photo assets and visual evidence for municipal audits.

### ⛓️ 5. Blockchain & Auditing
- **Immutable Ledgers**: Every work order, contractor payout, and maintenance action is cryptographically signed.
- **Transparency**: Prevents "ghost repairs" and ensures budget accountability.

### 📡 6. Real-Time Streaming & Data Fusion
- **Server-Sent Events (SSE)**: Live event stream emitting real-time vibration spikes and sensor node telemetry (`/api/stream`).
- **IoT Integration**: Live telemetry from vibration sensors and traffic load monitors.
- **Vehicle Crowd-Sensing**: Aggregates GPS and accelerometer data from everyday commuters to map road roughness (IRI).
- **LLM Decision Assistant**: Generates plain-language engineering repair booklets and summaries.

### 🏛️ 8. RoadAthena RAMS (Road Asset Management System)
- **320+ Road Asset Categories**: Computer vision multi-label detection tracking pavement distress, safety furniture, W-beam crash barriers, solar blinkers, traffic signages (IRC:67), markings (IRC:35), and drainage manholes.
- **Automated IRC Compliance & CA Clause Audits**: Instant validation of pothole depth, crack severity, and retro-reflectivity against Indian Road Congress standards (`IRC:SP:84`, `IRC:37`, `IRC:67`, `IRC:119`) with penalty risk flags.
- **Domestic Road Reach Analytics**: Pan-India survey intelligence across 20+ states covering 270,000+ km of national highway corridors.
- **AthenaBot IRC AI Assistant**: Intelligent conversational engineering chatbot answering IRC maintenance rules, repair thresholds, and IndiaRAP star safety ratings.
- **High-Impact UI Experience**: Orbital tech preloader, continuous marquee defect galleries, typewriter hero section, interactive state cards, and light/dark theme support.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | Python 3.x, Flask, RESTful API |
| **Database** | SQLite (optimized with custom `DatabaseManager`) |
| **Authentication** | JWT, Role-Based Access Control (RBAC), Google OAuth 2.0 |
| **Machine Learning** | PyTorch, NumPy, Pandas |
| **AI Assistants** | Generative AI / LLM Integration |
| **Infrastructure** | Blockchain (Audit Trail), IoT Data Fusion Engine |

---

## 📂 Project Structure

```text
roadsense_webapp/
├── app_enhanced.py           # Core Backend Entry Point
├── auth.py                   # Secure RBAC & OAuth Logic
├── blockchain_audit.py       # Distributed Ledger Integration
├── crowd_sensing.py          # Mobile Telemetry Processor
├── data_fusion.py            # Multi-Sensor Merging Engine
├── database.py               # Optimized SQLite Wrapper
├── digital_twin.py           # Real-time Infrastructure Simulation
├── graph_analytics.py        # Topological Risk & Network Analysis
├── iot_sensors.py            # IoT Device Management
├── llm_assistant.py          # Decision Support (Generative AI)
├── prediction_engine.py      # AI Forecasting & Risk Analytics
├── vision_service.py         # Computer Vision & Asset Extraction
├── static/                   # Visual Assets & Dashboard Styles
├── templates/                # Responsive HTML5 Dashboards
└── requirements.txt          # System Dependencies
```

---

## 🏁 Getting Started

### Prerequisites
- Python 3.9 or higher
- `pip` package manager

### Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/premwadhwani24/Roadsense_AI.git
   cd Roadsense_AI
   ```

2. **Set up Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Copy the provided `.env.example` to create your local environment file:
   ```bash
   copy .env.example .env    # On Windows
   # or
   cp .env.example .env      # On Linux/macOS
   ```
   Open the `.env` file and populate your custom configuration settings:
   ```env
   FLASK_SECRET_KEY="your-secret-key"
   GOOGLE_MAPS_KEY="your-google-maps-api-key"
   OPENWEATHER_KEY="your-openweather-api-key"
   TOMTOM_KEY="your-tomtom-api-key"
   ```

5. **Initialize Database & Verify Setup**
   Run the setup script to initialize the SQLite schema, verify local environment variables, and create default admin credentials:
   ```bash
   python setup.py
   ```
   *Note: On first run, the database will automatically initialize default admin accounts (e.g. `admin` / `admin123`).*

---

## 🖥️ Usage

Run the enhanced application:
```bash
python app_enhanced.py
```
Access the dashboard at `http://localhost:5000`.

---

## 9. 🚗 RoadBounce Integration & All-India Dynamic Remediation Engine

RoadSense AI incorporates the **RoadBounce (https://roadbounce.com/)** smartphone roughness (IRI) and **PotholeGuard** computer vision philosophy across real geo-tagged road networks throughout India without any hardcoding:

### 🟢 3-Tier Dynamic Classification
- 🟢 **GREEN (Optimal Condition)**: IRI < 2.5 m/km, PCI 85–100, zero critical defects.
- 🟡 **YELLOW (Actionable Wear)**: IRI 2.5–4.0 m/km, PCI 50–84 — Actionable via one-click micro-surfacing/crack seal to **dynamically convert into Green** in the SQLite database.
- 🔴 **RED (Critical Structural Failure)**: IRI > 4.0 m/km, PCI < 50 — Accompanied by **Forensic Visual & Sensor Proofs** (actual camera photos, GPS coordinates, accelerometer G-force spikes, repair budget, and work order dispatch).

### Key RoadBounce Endpoints
- `GET /api/v3/roadbounce/roads`: Live All-India road segments with filtering by status, city, state, and roughness.
- `POST /api/v3/roadbounce/remediate`: One-click repair execution converting Yellow/Red roads into Green in SQLite.
- `POST /api/v3/roadbounce/survey-ingest`: Smartphone accelerometer and camera survey telemetry ingestion.
- `GET /api/v3/roadbounce/kpis`: National roughness averages and preventative cost savings.
- `GET /api/v3/roadbounce/proof/<road_id>`: High-res damage photo proof, GPS geo-tag, and G-force peak.

---

## 10. 🎯 RDD2022 Multi-National Road Damage Dataset & CV Studio

Integrated benchmark dataset and deep learning taxonomy based on **RDD2022 (CRDDC 2022)** comprising **47,420 road images** across 6 countries:
- 🇮🇳 **India**: 9,665 images (Delhi, Gurugram, Haryana - smartphone car mount)
- 🇯🇵 **Japan**: 13,133 images
- 🇳🇴 **Norway**: 10,201 images (ViaPPS dual Basler CMOS)
- 🇺🇸 **United States**: 6,005 images (Google Street View)
- 🇨🇿 **Czech Republic**: 3,538 images (D1/D2/D46 motorways)
- 🇨🇳 **China**: 4,878 images (DJI Drone & Motorbike mounted)

### Standard Damage Codes Tracked
- **D00**: Longitudinal Crack
- **D10**: Transverse Crack
- **D20**: Alligator Fatigue Crack
- **D40**: Pothole Cavity
- **D43**: Crosswalk / Zebra Marking Blur
- **D44**: Lane / Center Line Blur
- **Repair**: Patched Asphalt Monitoring

### Key RDD2022 Endpoints
- `GET /api/v3/rdd/stats`: Global & country dataset splits, resolutions, and benchmark accuracies.
- `GET /api/v3/rdd/classes`: Standard RDD2022 class taxonomy, severity, and repair remedies.
- `POST /api/v3/rdd/detect`: Automated bounding box object detection inference with normalized coordinates.

---


---

## 11. 🛰️ Real-Time Location-Based Road Intelligence & Data Fusion Platform (Phase 7)

Transforms RoadSense AI into an interactive, location-based intelligence platform operating on **both live/current and historical road data**:
- 🔍 **Google Maps Location Search**: Search any Indian city, highway, landmark, or address with automatic Nominatim fallback.
- ⚡ **Multi-Modal Data Fusion**: Combines vehicle dashcam CV, smartphone accelerometer G-force, IoT telematics, TomTom traffic flow, OpenWeatherMap precipitation, and crowdsourced citizen reports.
- 🏷️ **Data Provenance System**: Strictly tags all data streams as `[LIVE]`, `[RECENT]`, `[HISTORICAL]`, or `[AI-PREDICTED]`. Never presents stored baseline records as live data.
- 📉 **Deterioration Forecasting**: Predicts 7, 30, 60, and 90-day deterioration failure risks and remaining useful life (RUL).
- 💡 **Actionable AI Maintenance Recommendations**: Prescribes maintenance priority (P1-P4), urgency timelines, repair methods, estimated cost (₹/km), and IRC standard compliance (IRC:SP:84, IRC:37, IRC:35, IRC:67).
- 📡 **Server-Sent Events (SSE)**: Auto-updating `/api/v3/realtime/stream` pushing instantaneous telemetry without page reload.
- 🇮🇷 **IRRDD (Iran Road Damage Dataset 2022)**: 25,000 additional YOLO-annotated damage images with CLAHE, SunFlare, and RandomShadow augmentation pipeline.

### Key Real-Time Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v3/realtime/location-search?q=...` | Location autocomplete & geocoding proxy |
| `GET` | `/api/v3/realtime/nearby-roads?lat=..&lng=..` | Fused nearby road segments with color-coded health |
| `GET` | `/api/v3/realtime/road-health/<road_id>` | Fused real-time 0-100 road health index |
| `POST` | `/api/v3/realtime/ingest-frame` | Vehicle camera frame ingest & GPS defect detection |
| `GET` | `/api/v3/realtime/defects?lat=..&lng=..` | Real-time GPS-tagged defects proximity query |
| `POST` | `/api/v3/realtime/sensor-ingest` | Accelerometer G-force & GPS speed ingest |
| `GET` | `/api/v3/realtime/weather?city=...` | Real-time weather, precipitation & waterlogging risk |
| `GET` | `/api/v3/realtime/traffic?lat=..&lng=..` | TomTom dynamic traffic congestion index & speed |
| `GET` | `/api/v3/realtime/predictions/<road_id>` | 7/30/60/90-day failure risk probabilities & RUL |
| `GET` | `/api/v3/realtime/recommend/<road_id>` | Actionable AI maintenance guidance & IRC codes |
| `GET` | `/api/v3/realtime/stream` | Live SSE telematics pulse stream |
| `GET` | `/api/v3/rdd/irrdd` | IRRDD dataset statistics and augmentations |

## 🔮 Future Roadmap
- [ ] **Satellite GIS Intel**: Automated macro-scopic monitoring via orbital imagery.
- [ ] **Digital Twin Simulation**: 3D virtual modeling of weather/traffic impacts.
- [ ] **Offline Field App**: Dedicated mobile tool for engineers in remote areas.

---

## 🤝 Contributing
We welcome contributions to the RoadSense ecosystem! 
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

---
**RoadSense AI** — *Building the arteries of the future.*

