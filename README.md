# 🛣️ RoadSense AI — Next-Gen Smart Road Infrastructure Management

RoadSense AI is a comprehensive, next-generation smart infrastructure management ecosystem designed to transform how cities monitor, maintain, and audit their road networks. Built for high-stakes environments like the **Smart India Hackathon (SIH)**, it integrates advanced AI, Computer Vision, IoT telemetry, and Blockchain auditing into a unified, actionable dashboard.

---

## 🌟 The Vision
Traditional road maintenance is reactive, expensive, and often lacks transparency. **RoadSense AI** shifts the paradigm to **Proactive & Prescriptive Maintenance**. By fusing data from citizen reports, vehicle sensors, and satellite/CV imagery, the system predicts failures before they happen and prescribes the most cost-effective repair strategies.

---

## 🚀 Key Modules & Capabilities

### 🧠 1. AI Prediction Engine
- **Deterioration Modeling**: Forecasts road health over 30, 60, and 90-day windows.
- **Accident Risk Mapping**: Identifies high-risk zones using historical data and spatial analysis.
- **Pothole Forecasting**: Spatial prediction of likely defect formations using environmental stressors.

### 👁️ 2. Computer Vision (RoadAthena Integration)
- **Deep Learning Defects**: Real-time detection of cracks, potholes, and surface wear from mobile/CCTV feeds.
- **Automated Asset Inventory**: AI-generated maps of speed signs, guardrails, and traffic lights with condition scoring.

### ⛓️ 3. Blockchain & Auditing
- **Immutable Ledgers**: Every work order, contractor payout, and maintenance action is cryptographically signed.
- **Transparency**: Prevents "ghost repairs" and ensures budget accountability.

### 📡 4. Multi-Source Data Fusion
- **IoT Integration**: Live telemetry from vibration sensors and traffic load monitors.
- **Vehicle Crowd-Sensing**: Aggregates GPS and accelerometer data from everyday commuters to map road roughness (IRI).
- **LLM Decisions**: A Generative AI assistant (LLM) provides plain-language summaries and technical recommendations.

### 📊 5. Financial & Resource Optimization
- **Dynamic Budgeting**: Real-time tracking of municipal funds vs. repair requirements.
- **Geospatial Clustering (DBSCAN)**: Automatically groups proximal defects into "Maintenance Zones" to optimize fuel and labor.

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

### Key API Endpoints
- `GET /api/roads/status`: Fetch real-time road condition map.
- `POST /api/vision/analyze`: Submit images for AI defect detection.
- `GET /api/predictions/report/<city>`: Generate comprehensive AI analysis.
- `GET /api/analytics/kpis`: View system-wide performance metrics.

---

## 🔮 Future Roadmap
- [ ] **Satellite GIS Intel**: Automated macro-scopic monitoring via orbital imagery.
- [ ] **Digital Twin Simulation**: 3D virtual modeling of weather/traffic impacts.
- [ ] **Offline Field App**: Dedicated mobile tool for engineers in remote areas.
- [ ] **Auto-Healing Recommendations**: Lifecycle-integrated repair suggestion engine.

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
