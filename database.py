"""
Database initialization and models for RoadSense AI system
Handles users, alerts, work orders, and road condition history
"""
import sqlite3
import os
import json
import time
import random
from datetime import datetime
from typing import List, Dict, Any, Optional

if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/roadsense.db"
    if not os.path.exists(DB_PATH) and os.path.exists("roadsense.db"):
        import shutil
        try:
            shutil.copy("roadsense.db", DB_PATH)
        except Exception:
            pass
else:
    DB_PATH = "roadsense.db"

def init_database():
    """Initialize database schema with all required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'viewer',
            city TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            road_id TEXT NOT NULL,
            road_name TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            assigned_to INTEGER REFERENCES users(id),
            notification_sent BOOLEAN DEFAULT 0
        )
    ''')
    
    # Work Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS work_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            road_id TEXT NOT NULL,
            road_name TEXT NOT NULL,
            work_type TEXT NOT NULL,
            contractor TEXT,
            estimated_cost REAL,
            actual_cost REAL,
            status TEXT DEFAULT 'pending',
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            created_by INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            before_photo TEXT,
            after_photo TEXT,
            notes TEXT
        )
    ''')
    
    # Road History (for trending)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS road_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            road_id TEXT NOT NULL,
            road_name TEXT NOT NULL,
            condition_status TEXT,
            traffic_level REAL,
            weather_condition TEXT,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Citizen Reports (crowdsourced)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS citizen_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            road_id TEXT,
            road_name TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            issue_type TEXT NOT NULL,
            description TEXT,
            image_path TEXT,
            verified BOOLEAN DEFAULT 0,
            verification_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Budget Tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budget_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            year INTEGER NOT NULL,
            allocated_budget REAL,
            spent REAL DEFAULT 0,
            remaining REAL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # IoT Telemetry
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS iot_telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            road_id TEXT NOT NULL,
            vibration_level REAL,
            temperature REAL,
            traffic_load_index REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Vehicle Crowd-Sensing
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicle_crowdsense (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT NOT NULL,
            road_id TEXT,
            latitude REAL,
            longitude REAL,
            anomaly_type TEXT,
            confidence REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Blockchain Ledger
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blockchain_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_index INTEGER NOT NULL,
            prev_hash TEXT NOT NULL,
            block_hash TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Voice Reports Table (LiveSpeak Integration)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voice_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reporter_id INTEGER REFERENCES users(id),
            road_id TEXT,
            audio_url TEXT,
            transcript TEXT,
            sentiment TEXT,
            urgency_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check and add road_material column dynamically if not present
    try:
        cursor.execute("ALTER TABLE alerts ADD COLUMN road_material TEXT DEFAULT 'Asphalt'")
    except sqlite3.OperationalError:
        pass
    
    # Digital Twin States
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS digital_twin_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            road_id TEXT NOT NULL,
            simulated_age_days INTEGER,
            stress_level REAL,
            weather_impact_factor REAL,
            overall_health_score REAL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # RoadBounce Smartphone IRI & Pothole Surveys
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roadbounce_surveys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            road_id TEXT UNIQUE NOT NULL,
            road_name TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            condition_status TEXT NOT NULL, -- 'GREEN', 'YELLOW', 'RED'
            iri_score REAL NOT NULL, -- International Roughness Index (m/km)
            pci_score REAL NOT NULL, -- Pavement Condition Index (0-100)
            vibration_gforce_peak REAL DEFAULT 0.0,
            speed_kmh REAL DEFAULT 40.0,
            pothole_count INTEGER DEFAULT 0,
            crack_severity TEXT DEFAULT 'None',
            proof_image_url TEXT,
            proof_telemetry_json TEXT,
            recommended_action TEXT,
            estimated_cost_inr REAL DEFAULT 0.0,
            remediated_at TIMESTAMP,
            remediated_by TEXT,
            last_surveyed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    
    # Real-Time Detected Defects (CV / Dashcam / Ingest)
    
    # Government Road Segments Registry (GIS Geometries, Hierarchy, Conditions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gov_road_segments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            segment_id TEXT UNIQUE NOT NULL,
            road_name TEXT NOT NULL,
            road_type TEXT NOT NULL,
            highway_code TEXT,
            state TEXT NOT NULL,
            district TEXT NOT NULL,
            city TEXT NOT NULL,
            pincode TEXT,
            jurisdiction_agency TEXT,
            length_km REAL DEFAULT 1.0,
            polyline_json TEXT NOT NULL,
            center_lat REAL NOT NULL,
            center_lng REAL NOT NULL,
            speed_limit_kmh INTEGER DEFAULT 50,
            lanes INTEGER DEFAULT 4,
            condition_status TEXT DEFAULT 'DATA_UNAVAILABLE',
            health_score REAL,
            confidence REAL DEFAULT 0.0,
            iri_score REAL,
            pci_score REAL,
            vibration_gforce_peak REAL DEFAULT 0.25,
            pothole_count INTEGER DEFAULT 0,
            crack_count INTEGER DEFAULT 0,
            last_surveyed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Add dynamic condition_score, zone and proof_image_url columns if not present
    for col_sql in ["condition_score REAL", "zone TEXT DEFAULT 'GREEN'", "proof_image_url TEXT"]:
        try:
            cursor.execute(f"ALTER TABLE gov_road_segments ADD COLUMN {col_sql}")
        except sqlite3.OperationalError:
            pass


    # Road Condition Evidence Records (Camera Photos, Sensor Waveforms, Bounding Boxes)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS road_evidence_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evidence_id TEXT UNIQUE NOT NULL,
            segment_id TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            source_type TEXT NOT NULL, -- 'VEHICLE_CAMERA', 'IOT_SENSOR', 'FIELD_ENGINEER', 'CITIZEN_REPORT'
            device_id TEXT DEFAULT 'VEH-DASHCAM-01',
            image_url TEXT,
            defects_detected_json TEXT,
            confidence REAL DEFAULT 0.9,
            captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            verified_by TEXT,
            FOREIGN KEY (segment_id) REFERENCES gov_road_segments(segment_id)
        )
    ''')

    # Before/After Maintenance Repair Verification Audits
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS repair_verification_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_order_id INTEGER,
            segment_id TEXT NOT NULL,
            road_name TEXT NOT NULL,
            before_photo_url TEXT,
            after_photo_url TEXT,
            verification_status TEXT NOT NULL, -- 'VERIFIED_COMPLIANT', 'REINSPECTION_REQUIRED'
            is_approved BOOLEAN DEFAULT 0,
            pavement_quality_score REAL,
            engineering_findings TEXT,
            prescribed_action TEXT,
            blockchain_tx_hash TEXT,
            inspector_id TEXT DEFAULT 'ENG-INSPECTOR-09',
            verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS realtime_defects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            defect_code TEXT NOT NULL,
            class_name TEXT NOT NULL,
            severity TEXT NOT NULL,
            confidence REAL NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            road_id TEXT,
            image_url TEXT,
            vehicle_id TEXT DEFAULT 'VEH-IN-01',
            data_source TEXT DEFAULT 'LIVE_CV_STREAM',
            captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Live Sensor Telemetry (Vibration, Accelerometer G-Force, GPS Speed)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_telemetry_live (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT NOT NULL,
            road_id TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            speed_kmh REAL DEFAULT 40.0,
            g_force REAL DEFAULT 1.0,
            vibration_index REAL DEFAULT 0.5,
            data_source TEXT DEFAULT 'LIVE_SENSOR',
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Weather Cache
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            latitude REAL,
            longitude REAL,
            weather_json TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Traffic Flow Readings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            road_id TEXT,
            congestion_pct REAL,
            speed_kmh REAL,
            traffic_level TEXT,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    
    # Auto-seed initial all-India RoadBounce survey data if empty
    seed_roadbounce_data()
    seed_gov_road_network()
    seed_damage_road_dataset_evidence()
    print("Database initialized successfully")
def seed_roadbounce_data():
    """Seed comprehensive All-India road condition monitoring dataset with real GPS & proof images"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM roadbounce_surveys")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    import json
    
    sample_roads = [
        # --- DELHI ---
        ("RB-DEL-01", "Ring Road (Lajpat Nagar Stretch)", "New Delhi", "Delhi", 28.5700, 77.2400, "GREEN", 1.8, 94.0, 0.28, 55.0, 0, "None", "/static/assets/damaged_roads/0000000000000000_100913988636_11_jpg.rf.025a17688dbcb644485501867cfa24b4.jpg", "Smooth optimal pavement. IRC:SP:84 compliant.", 0.0),
        ("RB-DEL-02", "Mehrauli-Badarpur Road (Near Saket)", "New Delhi", "Delhi", 28.5150, 77.2050, "YELLOW", 3.4, 66.0, 1.45, 38.0, 3, "Medium", "/static/assets/damaged_roads/alligator-cracks-1_jpg.rf.4d9f0f9bcf0bb53ffb4a6fa8087f9754.jpg", "Moderate longitudinal wear. Scheduled micro-surfacing will restore to GREEN.", 45000.0),
        ("RB-DEL-03", "NH-48 Mahipalpur Junction Underpass", "New Delhi", "Delhi", 28.5450, 77.1250, "RED", 6.8, 32.0, 4.10, 20.0, 12, "Critical", "/static/assets/damaged_roads/speed-hump-ahead-yellow-stripes-260nw-780891661_jpeg_jpg.rf.13e6f34dcce59001a205cc149d73af2f.jpg", "Severe structural failure with multiple deep potholes (>40mm). Full FDR overlay required.", 320000.0),
        
        # --- MAHARASHTRA (Mumbai & Pune) ---
        ("RB-MUM-01", "Bandra-Worli Sea Link Approach", "Mumbai", "Maharashtra", 19.0300, 72.8180, "GREEN", 1.6, 96.0, 0.22, 70.0, 0, "None", "/static/assets/damaged_roads/1_XoUpw9FGhfYh6Clpk_Wsbg-2x_jpg.rf.269bea6ceff5505771851fa8242fa6e0.jpg", "Excellent high-speed concrete ride quality.", 0.0),
        ("RB-MUM-02", "SV Road (Andheri West)", "Mumbai", "Maharashtra", 19.1190, 72.8460, "YELLOW", 3.6, 62.0, 1.65, 30.0, 4, "Medium", "/static/assets/damaged_roads/crack1.jpg", "Surface fatigue due to monsoon runoff. Crack sealing needed to convert to GREEN.", 60000.0),
        ("RB-MUM-03", "LBS Marg (Kurla Junction)", "Mumbai", "Maharashtra", 19.0720, 72.8850, "RED", 7.2, 26.0, 4.45, 18.0, 15, "Critical", "/static/assets/damaged_roads/potholes-cover.webp", "Critical waterlogging crater damage. Complete milled asphalt resurfacing required.", 450000.0),
        ("RB-PUN-01", "FC Road (Shivajinagar)", "Pune", "Maharashtra", 18.5280, 73.8420, "GREEN", 1.9, 91.0, 0.32, 45.0, 0, "None", "/static/assets/damaged_roads/1_XoUpw9FGhfYh6Clpk_Wsbg-2x_jpg.rf.4c6411a8bdc890e1f19411f8e492cc39.jpg", "Optimal urban pavement condition.", 0.0),
        ("RB-PUN-02", "Hinjewadi Phase 1 IT Park Arterial", "Pune", "Maharashtra", 18.5910, 73.7380, "YELLOW", 3.2, 68.0, 1.30, 35.0, 2, "Low", "/static/assets/damaged_roads/234_jpg.rf.0e40fa74f347616f3a060ed54c5da190.jpg", "Minor ravelling along shoulder. Slurry seal treatment will upgrade to GREEN.", 38000.0),
        ("RB-PUN-03", "Katraj-Dehu Road Bypass", "Pune", "Maharashtra", 18.4550, 73.8650, "RED", 6.2, 38.0, 3.85, 25.0, 9, "Critical", "/static/assets/damaged_roads/alligator-cracks-cover.webp", "Major fatigue alligator cracking across both lanes. Heavy vehicle distress.", 290000.0),

        # --- KARNATAKA (Bengaluru) ---
        ("RB-BLR-01", "Electronic City Elevated Expressway", "Bengaluru", "Karnataka", 12.8450, 77.6600, "GREEN", 1.7, 95.0, 0.25, 65.0, 0, "None", "/static/assets/damaged_roads/1_XoUpw9FGhfYh6Clpk_Wsbg-2x_jpg.rf.5f6e08bdff04a014fc7b3de605d363f1.jpg", "Smooth expressway surface.", 0.0),
        ("RB-BLR-02", "Outer Ring Road (Bellandur Stretch)", "Bengaluru", "Karnataka", 12.9280, 77.6780, "YELLOW", 3.5, 64.0, 1.55, 32.0, 4, "Medium", "/static/assets/damaged_roads/2a88d1n_jpg.rf.0ab38483eeb31f5d7a9e1e86035f55ab.jpg", "Moderate edge degradation and rutting. Preventative milling will restore GREEN.", 52000.0),
        ("RB-BLR-03", "Whitefield Main Road (Near ITPL)", "Bengaluru", "Karnataka", 12.9850, 77.7400, "RED", 6.5, 34.0, 4.20, 20.0, 11, "Critical", "/static/assets/damaged_roads/pothole1.jpg", "Severe depression and sub-base subsidence with dangerous potholes.", 360000.0),

        # --- TELANGANA (Hyderabad) ---
        ("RB-HYD-01", "PVNR Elevated Expressway", "Hyderabad", "Telangana", 17.3600, 78.4350, "GREEN", 1.7, 93.0, 0.26, 60.0, 0, "None", "/static/assets/damaged_roads/234_jpg.rf.492fb837914dcc279708e05d4a76a8cb.jpg", "Excellent elevated corridor condition.", 0.0),
        ("RB-HYD-02", "Gachibowli to Financial District Link", "Hyderabad", "Telangana", 17.4200, 78.3450, "YELLOW", 3.1, 71.0, 1.25, 40.0, 2, "Low", "/static/assets/damaged_roads/2a88d1n_jpg.rf.1d7481dd08508a62a9ca59856430802b.jpg", "Minor surface cracking. Polymer seal will convert to GREEN.", 35000.0),
        ("RB-HYD-03", "Old City Charminar Commercial Corridor", "Hyderabad", "Telangana", 17.3610, 78.4740, "RED", 5.9, 41.0, 3.60, 22.0, 8, "High", "/static/assets/damaged_roads/crack2.jpg", "Heavy utility trench cuts and surface craters.", 210000.0),

        # --- TAMIL NADU (Chennai) ---
        ("RB-CHN-01", "OMR IT Expressway (SRP Tools)", "Chennai", "Tamil Nadu", 12.9800, 80.2500, "GREEN", 1.8, 92.0, 0.27, 50.0, 0, "None", "/static/assets/damaged_roads/1_XoUpw9FGhfYh6Clpk_Wsbg-2x_jpg.rf.86b5937fd8c7d082e34aa9fe650e849c.jpg", "Good condition bituminous layer.", 0.0),
        ("RB-CHN-02", "Anna Salai (Guindy to Saidapet)", "Chennai", "Tamil Nadu", 13.0100, 80.2150, "YELLOW", 3.3, 67.0, 1.40, 35.0, 3, "Medium", "/static/assets/damaged_roads/234_jpg.rf.690f187e569d56edf9f35add1be9058d.jpg", "Patchy wear on lane boundaries. Maintenance will upgrade to GREEN.", 42000.0),
        ("RB-CHN-03", "GST Road (Chromepet Junction)", "Chennai", "Tamil Nadu", 12.9520, 80.1410, "RED", 6.4, 36.0, 4.00, 25.0, 10, "Critical", "/static/assets/damaged_roads/potholes-cover.webp", "Severe pothole cluster on inner lane.", 280000.0),

        # --- WEST BENGAL (Kolkata) ---
        ("RB-KOL-01", "Maa Flyover (Park Circus to EM Bypass)", "Kolkata", "West Bengal", 22.5400, 88.3850, "GREEN", 1.9, 90.0, 0.30, 55.0, 0, "None", "/static/assets/damaged_roads/2a88d1n_jpg.rf.55a4f5506b9c0a577a282e070c05543f.jpg", "Smooth flyover pavement.", 0.0),
        ("RB-KOL-02", "VIP Road (Kestopur Stretch)", "Kolkata", "West Bengal", 22.5950, 88.4250, "YELLOW", 3.7, 60.0, 1.70, 32.0, 5, "Medium", "/static/assets/damaged_roads/crack3.jpg", "Moderate wear and faded markings. Seal & repaint to restore GREEN.", 58000.0),
        ("RB-KOL-03", "BT Road (Dunlop Crossing)", "Kolkata", "West Bengal", 22.6550, 88.3750, "RED", 7.0, 29.0, 4.35, 18.0, 14, "Critical", "/static/assets/damaged_roads/alligator-cracks-1_jpg.rf.4d9f0f9bcf0bb53ffb4a6fa8087f9754.jpg", "Major structural disintegration.", 410000.0),

        # --- RAJASTHAN (Jaipur) & GUJARAT (Ahmedabad) ---
        ("RB-JAI-01", "Jawahar Circle JLN Marg", "Jaipur", "Rajasthan", 26.8350, 75.8050, "GREEN", 1.6, 95.0, 0.24, 50.0, 0, "None", "/static/assets/damaged_roads/1_XoUpw9FGhfYh6Clpk_Wsbg-2x_jpg.rf.872fef602b797efe3f63fca748d494ba.jpg", "Flawless arterial pavement.", 0.0),
        ("RB-JAI-02", "Tonk Road (Sanganer Flyover)", "Jaipur", "Rajasthan", 26.8150, 75.7950, "YELLOW", 3.0, 73.0, 1.20, 42.0, 2, "Low", "/static/assets/damaged_roads/234_jpg.rf.a1e5046c1d424df2ebb990b6a6a1839e.jpg", "Thermal surface stress. Upgrade to GREEN with fog seal.", 32000.0),
        ("RB-AHM-01", "SG Highway (Thaltej Crossroad)", "Ahmedabad", "Gujarat", 23.0550, 72.5150, "GREEN", 1.7, 94.0, 0.25, 60.0, 0, "None", "/static/assets/damaged_roads/1_XoUpw9FGhfYh6Clpk_Wsbg-2x_jpg.rf.88f5b055a3768a3bfc443b52dd8659a5.jpg", "High-capacity commercial corridor in great shape.", 0.0),
        ("RB-AHM-02", "Narol-Sarkhej Industrial Bypass", "Ahmedabad", "Gujarat", 22.9900, 72.5500, "RED", 6.6, 33.0, 4.15, 22.0, 11, "Critical", "/static/assets/damaged_roads/speed-hump-ahead-yellow-stripes-260nw-780891661_jpeg_jpg.rf.13e6f34dcce59001a205cc149d73af2f.jpg", "Heavy axle rutting and cratering.", 340000.0),

        # --- UTTAR PRADESH (Lucknow) & BIHAR (Patna) ---
        ("RB-LKO-01", "Amar Shaheed Path Ring Highway", "Lucknow", "Uttar Pradesh", 26.7900, 80.9850, "GREEN", 1.8, 93.0, 0.26, 65.0, 0, "None", "/static/assets/damaged_roads/2a88d1n_jpg.rf.0ab38483eeb31f5d7a9e1e86035f55ab.jpg", "Standard NHAI bypass quality.", 0.0),
        ("RB-LKO-02", "Faizabad Road (Polytechnic Chauraha)", "Lucknow", "Uttar Pradesh", 26.8750, 80.9950, "YELLOW", 3.4, 65.0, 1.48, 35.0, 3, "Medium", "/static/assets/damaged_roads/crack1.jpg", "Surface wear at intersection. Hot-mix patching will convert to GREEN.", 46000.0),
        ("RB-PAT-01", "Ganga Marine Drive (Digha to PMCH)", "Patna", "Bihar", 25.6250, 85.1450, "GREEN", 1.7, 94.0, 0.24, 55.0, 0, "None", "/static/assets/damaged_roads/1_XoUpw9FGhfYh6Clpk_Wsbg-2x_jpg.rf.269bea6ceff5505771851fa8242fa6e0.jpg", "New riverfront expressway condition.", 0.0),
        ("RB-PAT-02", "Bailey Road (Saguna More)", "Patna", "Bihar", 25.6100, 85.0550, "RED", 6.9, 30.0, 4.30, 19.0, 13, "Critical", "/static/assets/damaged_roads/pothole1.jpg", "Multiple deep monsoon potholes causing major vehicular deceleration.", 390000.0),

        # --- OTHER PROMINENT STATES (J&K, Punjab, Assam, Kerala, MP) ---
        ("RB-SRI-01", "Dal Lake Boulevard Road", "Srinagar", "Jammu & Kashmir", 34.0950, 74.8450, "GREEN", 1.9, 91.0, 0.30, 40.0, 0, "None", "/static/assets/damaged_roads/234_jpg.rf.acac6a5cbd70790652e420a208bd59ea.jpg", "Pristine tourist corridor.", 0.0),
        ("RB-ASR-01", "GT Road (Amritsar Bypass)", "Amritsar", "Punjab", 31.6300, 74.8850, "YELLOW", 3.2, 70.0, 1.35, 45.0, 2, "Low", "/static/assets/damaged_roads/234_jpg.rf.0e40fa74f347616f3a060ed54c5da190.jpg", "Minor transverse cracks. Quick repair will upgrade to GREEN.", 34000.0),
        ("RB-GUW-01", "GS Road (Dispur Capital Stretch)", "Guwahati", "Assam", 26.1450, 91.7900, "YELLOW", 3.5, 63.0, 1.60, 35.0, 4, "Medium", "/static/assets/damaged_roads/crack2.jpg", "High humidity surface distress. Resurfacing converts to GREEN.", 49000.0),
        ("RB-KOC-01", "Seaport-Airport Road", "Kochi", "Kerala", 10.0250, 76.3450, "GREEN", 1.8, 92.0, 0.28, 50.0, 0, "None", "/static/assets/damaged_roads/1_XoUpw9FGhfYh6Clpk_Wsbg-2x_jpg.rf.4fdae995ebd261f49e24bd03ba81affb.jpg", "Heavy rainfall resilient surface.", 0.0),
        ("RB-GWL-01", "City Centre Road", "Gwalior", "Madhya Pradesh", 26.2100, 78.1900, "RED", 6.1, 39.0, 3.75, 24.0, 7, "High", "/static/assets/damaged_roads/alligator-cracks-cover.webp", "Severe edge drop-off and base wear.", 220000.0)
    ]
    
    for r in sample_roads:
        telemetry = {
            "accelerometer_hz": 100,
            "waveform_sample": [round(0.1 + (r[8]*0.15), 2), round(0.2 + (r[8]*0.3), 2), round(r[8], 2), round(0.3, 2)],
            "speed_kmh": r[9],
            "irc_compliance": "PASS" if r[6] == "GREEN" else ("WARN_MARGINAL" if r[6] == "YELLOW" else "FAIL_CRITICAL")
        }
        cursor.execute('''
            INSERT INTO roadbounce_surveys 
            (road_id, road_name, city, state, latitude, longitude, condition_status, iri_score, pci_score, 
             vibration_gforce_peak, speed_kmh, pothole_count, crack_severity, proof_image_url, 
             proof_telemetry_json, recommended_action, estimated_cost_inr)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], json.dumps(telemetry), r[14], r[15]))
    
    conn.commit()
    conn.close()
    print(f"RoadBounce All-India dataset seeded ({len(sample_roads)} road segments)")


def seed_gov_road_network():
    """Seeds the official pan-India government road network into SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM gov_road_segments")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    from gis_road_network import GISRoadNetworkEngine
    import json
    
    green_images = [
        "/static/assets/damaged_roads/1_XoUpw9FGhfYh6Clpk_Wsbg-2x_jpg.rf.269bea6ceff5505771851fa8242fa6e0.jpg",
        "/static/assets/damaged_roads/1_XoUpw9FGhfYh6Clpk_Wsbg-2x_jpg.rf.4c6411a8bdc890e1f19411f8e492cc39.jpg",
        "/static/assets/damaged_roads/1_XoUpw9FGhfYh6Clpk_Wsbg-2x_jpg.rf.5f6e08bdff04a014fc7b3de605d363f1.jpg",
        "/static/assets/damaged_roads/1_XoUpw9FGhfYh6Clpk_Wsbg-2x_jpg.rf.86b5937fd8c7d082e34aa9fe650e849c.jpg",
    ]
    yellow_images = [
        "/static/assets/damaged_roads/crack1.jpg",
        "/static/assets/damaged_roads/crack2.jpg",
        "/static/assets/damaged_roads/alligator-cracks-1_jpg.rf.4d9f0f9bcf0bb53ffb4a6fa8087f9754.jpg",
        "/static/assets/damaged_roads/bade gwalior.jpg",
        "/static/assets/damaged_roads/baradari gwalior.jpg",
    ]
    red_images = [
        "/static/assets/damaged_roads/pothole1.jpg",
        "/static/assets/damaged_roads/potholes-cover.webp",
        "/static/assets/damaged_roads/Naya bazar gwalior.jpg",
        "/static/assets/damaged_roads/gwalior fort road.jpg",
        "/static/assets/damaged_roads/damaged-asphalt-road-with-deep-pothole-american-highway-surface-ruined-roadway-urgent-need-repair_127089-31444.avif",
        "/static/assets/damaged_roads/national highway delhi.webp",
        "/static/assets/damaged_roads/guda gudi ka naka gwalior.jpg",
        "/static/assets/damaged_roads/shitla road.avif",
    ]
    img_idx = 0

    for seg in GISRoadNetworkEngine.PAN_INDIA_REGISTRY:
        s_id = seg["segment_id"]
        # Determine authentic initial condition state
        if "01" in s_id:
            status = "GREEN"
            health = 92.5
            iri = 1.8
            pci = 94.0
            potholes = 0
            cracks = 0
            proof_img = green_images[img_idx % len(green_images)]
        elif "02" in s_id:
            status = "YELLOW"
            health = 64.0
            iri = 3.4
            pci = 66.0
            potholes = 2
            cracks = 3
            proof_img = yellow_images[img_idx % len(yellow_images)]
        elif "03" in s_id:
            status = "RED"
            health = 32.0
            iri = 6.4
            pci = 32.0
            potholes = 9
            cracks = 8
            proof_img = red_images[img_idx % len(red_images)]
        else:
            status = "DATA_UNAVAILABLE"
            health = None
            iri = None
            pci = None
            potholes = 0
            cracks = 0
            proof_img = ""
        img_idx += 1

        cursor.execute('''
            INSERT INTO gov_road_segments (
                segment_id, road_name, road_type, highway_code, state, district, city, pincode,
                jurisdiction_agency, length_km, polyline_json, center_lat, center_lng,
                speed_limit_kmh, lanes, condition_status, health_score, confidence, iri_score, pci_score,
                vibration_gforce_peak, pothole_count, crack_count, proof_image_url, last_surveyed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            seg["segment_id"], seg["road_name"], seg["road_type"], seg["highway_code"],
            seg["state"], seg["district"], seg["city"], seg["pincode"],
            seg["jurisdiction_agency"], seg["length_km"], json.dumps(seg["polyline"]),
            seg["center_lat"], seg["center_lng"], seg["speed_limit_kmh"], seg["lanes"],
            status, health, 0.92 if status != 'DATA_UNAVAILABLE' else 0.0,
            iri, pci, 0.28 if status == 'GREEN' else (1.45 if status == 'YELLOW' else 4.10),
            potholes, cracks, proof_img
        ))

    conn.commit()
    conn.close()
    print("Government Road Network seeded successfully.")


def seed_damage_road_dataset_evidence():
    """Seeds authentic real-world damage road dataset images into SQLite road_evidence_records."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    import json
    dataset_records = [
        ("EV-GWL-01", "PWD-GWL-CITY-01", 26.2150, 78.1750, "FIELD_ENGINEER", "PWD-GWL-CAM-01", "/static/assets/damaged_roads/Naya bazar gwalior.jpg", json.dumps([{"label": "Pothole", "confidence": 96.2, "severity": "CRITICAL", "measurements": {"estimated_depth_cm": 7.2, "surface_area_sq_m": 1.60}}]), 0.96),
        ("EV-GWL-02", "PWD-GWL-CITY-02", 26.2050, 78.1650, "VEHICLE_CAMERA", "VEH-GWL-02", "/static/assets/damaged_roads/aamko gwalior.jpg", json.dumps([{"label": "Pothole", "confidence": 93.8, "severity": "HIGH", "measurements": {"estimated_depth_cm": 5.4, "surface_area_sq_m": 1.10}}]), 0.94),
        ("EV-GWL-03", "PWD-GWL-CITY-03", 26.2180, 78.1720, "CITIZEN_REPORT", "WHATSAPP-BOT", "/static/assets/damaged_roads/bade gwalior.jpg", json.dumps([{"label": "Crack", "confidence": 88.5, "severity": "MEDIUM", "measurements": {"crack_width_mm": 12.0, "crack_length_m": 4.5}}]), 0.88),
        ("EV-GWL-04", "PWD-GWL-MORAR-01", 26.2280, 78.2250, "FIELD_ENGINEER", "FIELD-GWL-04", "/static/assets/damaged_roads/baradari gwalior.jpg", json.dumps([{"label": "Crack", "confidence": 90.0, "severity": "HIGH", "measurements": {"crack_width_mm": 18.0, "crack_length_m": 6.2}}]), 0.90),
        ("EV-GWL-05", "PWD-GWL-NAKA-01", 26.1950, 78.1550, "VEHICLE_CAMERA", "VEH-GWL-05", "/static/assets/damaged_roads/guda gudi ka naka gwalior.jpg", json.dumps([{"label": "Pothole", "confidence": 95.0, "severity": "CRITICAL", "measurements": {"estimated_depth_cm": 8.0, "surface_area_sq_m": 2.1}}]), 0.95),
        ("EV-GWL-06", "PWD-GWL-FORT-01", 26.2300, 78.1680, "FIELD_ENGINEER", "FIELD-GWL-06", "/static/assets/damaged_roads/gwalior fort road.jpg", json.dumps([{"label": "Pothole", "confidence": 97.1, "severity": "CRITICAL", "measurements": {"estimated_depth_cm": 9.5, "surface_area_sq_m": 2.8}}]), 0.97),
        ("EV-GWL-07", "PWD-GWL-HAZIRA-01", 26.2450, 78.1950, "VEHICLE_CAMERA", "VEH-GWL-07", "/static/assets/damaged_roads/hariza road gwalior.jpg", json.dumps([{"label": "Crack", "confidence": 89.2, "severity": "HIGH", "measurements": {"crack_width_mm": 15.0, "crack_length_m": 8.0}}]), 0.89),
        ("EV-GWL-08", "PWD-GWL-LAXMI-01", 26.2100, 78.1600, "CITIZEN_REPORT", "CITIZEN-APP-08", "/static/assets/damaged_roads/laxmiganj gwalior.jpg", json.dumps([{"label": "Crack", "confidence": 87.0, "severity": "MEDIUM", "measurements": {"crack_width_mm": 10.0, "crack_length_m": 3.5}}]), 0.87),
        ("EV-DEL-01", "NHAI-DEL-NH48-01", 28.5450, 77.1250, "VEHICLE_CAMERA", "NHAI-PATROL-01", "/static/assets/damaged_roads/national highway delhi.webp", json.dumps([{"label": "Pothole", "confidence": 94.5, "severity": "CRITICAL", "measurements": {"estimated_depth_cm": 6.8, "surface_area_sq_m": 1.45}}]), 0.94),
        ("EV-PUN-01", "PWD-PUN-RING-01", 18.4550, 73.8650, "FIELD_ENGINEER", "PWD-PUN-01", "/static/assets/damaged_roads/pune mahasatra.jpg", json.dumps([{"label": "Pothole", "confidence": 92.4, "severity": "HIGH", "measurements": {"estimated_depth_cm": 6.0, "surface_area_sq_m": 1.30}}]), 0.92),
        ("EV-GWL-09", "PWD-GWL-SHITLA-01", 26.2350, 78.1800, "CITIZEN_REPORT", "WHATSAPP-BOT", "/static/assets/damaged_roads/shitla road.avif", json.dumps([{"label": "Pothole", "confidence": 96.0, "severity": "CRITICAL", "measurements": {"estimated_depth_cm": 7.8, "surface_area_sq_m": 1.75}}]), 0.96),
        ("EV-DEL-02", "PWD-DEL-RING-01", 28.5700, 77.2400, "IOT_SENSOR", "IOT-CHAMBER-02", "/static/assets/damaged_roads/21_11_2023-chamber_o.jpg", json.dumps([{"label": "Pothole", "confidence": 91.0, "severity": "HIGH", "measurements": {"estimated_depth_cm": 4.5, "surface_area_sq_m": 0.85}}]), 0.91),
        ("EV-DEL-03", "NHAI-DEL-NH44-01", 28.7041, 77.1025, "VEHICLE_CAMERA", "NHAI-PATROL-02", "/static/assets/damaged_roads/damaged-asphalt-road-with-deep-pothole-american-highway-surface-ruined-roadway-urgent-need-repair_127089-31444.avif", json.dumps([{"label": "Pothole", "confidence": 98.2, "severity": "CRITICAL", "measurements": {"estimated_depth_cm": 11.2, "surface_area_sq_m": 3.4}}]), 0.98)
    ]

    for rec in dataset_records:
        cursor.execute('''
            INSERT OR REPLACE INTO road_evidence_records 
            (evidence_id, segment_id, latitude, longitude, source_type, device_id, image_url, defects_detected_json, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', rec)

    conn.commit()
    conn.close()
    print(f"Damage Road Dataset evidence seeded ({len(dataset_records)} records)")


class DatabaseManager:
    """Manager for all database operations"""
    
    @staticmethod
    def add_user(username: str, email: str, password_hash: str, role: str = 'viewer', 
                 city: str = None, phone: str = None) -> int:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (username, email, password_hash, role, city, phone) VALUES (?, ?, ?, ?, ?, ?)',
                (username, email, password_hash, role, city, phone)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return user_id
        finally:
            conn.close()
    
    @staticmethod
    def get_user(username: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    @staticmethod
    def add_alert(road_id: str, road_name: str, severity: str, description: str = None) -> int:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO alerts (road_id, road_name, severity, description) VALUES (?, ?, ?, ?)',
                (road_id, road_name, severity, description)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    @staticmethod
    def get_alerts(status: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            if status:
                cursor.execute('SELECT * FROM alerts WHERE status = ? ORDER BY created_at DESC LIMIT ?', 
                             (status, limit))
            else:
                cursor.execute('SELECT * FROM alerts ORDER BY created_at DESC LIMIT ?', (limit,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    @staticmethod
    def add_work_order(road_id: str, road_name: str, work_type: str, created_by: int,
                      contractor: str = None, estimated_cost: float = None, notes: str = None) -> int:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO work_orders (road_id, road_name, work_type, created_by, contractor, estimated_cost, notes) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (road_id, road_name, work_type, created_by, contractor, estimated_cost, notes)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    @staticmethod
    def get_work_orders(status: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            if status:
                cursor.execute('SELECT * FROM work_orders WHERE status = ? ORDER BY created_at DESC LIMIT ?',
                             (status, limit))
            else:
                cursor.execute('SELECT * FROM work_orders ORDER BY created_at DESC LIMIT ?', (limit,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    @staticmethod
    def update_work_order_cost(work_order_id: int, actual_cost: float):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE work_orders SET actual_cost = ? WHERE id = ?', 
                         (actual_cost, work_order_id))
            conn.commit()
        finally:
            conn.close()
    
    @staticmethod
    def add_road_history(road_id: str, road_name: str, condition_status: str, 
                        traffic_level: float = None, weather_condition: str = None):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO road_history (road_id, road_name, condition_status, traffic_level, weather_condition) '
                'VALUES (?, ?, ?, ?, ?)',
                (road_id, road_name, condition_status, traffic_level, weather_condition)
            )
            conn.commit()
        finally:
            conn.close()
    
    @staticmethod
    def get_road_history(road_id: str, days: int = 30) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute(
                'SELECT * FROM road_history WHERE road_id = ? AND recorded_at > datetime("now", "-' + str(days) + ' days") '
                'ORDER BY recorded_at DESC',
                (road_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    @staticmethod
    def add_citizen_report(latitude: float, longitude: float, issue_type: str, 
                          description: str = None, road_id: str = None, road_name: str = None) -> int:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO citizen_reports (road_id, road_name, latitude, longitude, issue_type, description) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                (road_id, road_name, latitude, longitude, issue_type, description)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    @staticmethod
    def get_citizen_reports(status: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            if status:
                cursor.execute('SELECT * FROM citizen_reports WHERE status = ? ORDER BY created_at DESC LIMIT ?',
                             (status, limit))
            else:
                cursor.execute('SELECT * FROM citizen_reports ORDER BY created_at DESC LIMIT ?', (limit,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def add_iot_telemetry(road_id: str, vibration_level: float, temperature: float, traffic_load_index: float) -> int:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO iot_telemetry (road_id, vibration_level, temperature, traffic_load_index) VALUES (?, ?, ?, ?)',
                (road_id, vibration_level, temperature, traffic_load_index)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def get_iot_telemetry(road_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM iot_telemetry WHERE road_id = ? ORDER BY recorded_at DESC LIMIT ?', (road_id, limit))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def add_vehicle_anomaly(vehicle_id: str, road_id: str, latitude: float, longitude: float, anomaly_type: str, confidence: float) -> int:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO vehicle_crowdsense (vehicle_id, road_id, latitude, longitude, anomaly_type, confidence) VALUES (?, ?, ?, ?, ?, ?)',
                (vehicle_id, road_id, latitude, longitude, anomaly_type, confidence)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    # =========================================================================
    # ROADBOUNCE DATA OPERATIONS
    # =========================================================================
    @staticmethod

    @staticmethod
    def get_roadbounce_survey_by_id(road_id: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM roadbounce_surveys WHERE road_id = ?", (road_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def get_roadbounce_surveys() -> List[Dict[str, Any]]:
        return DatabaseManager.get_roadbounce_roads()

    def get_roadbounce_roads(city: Optional[str] = None, state: Optional[str] = None, 
                             status: Optional[str] = None, min_iri: Optional[float] = None,
                             search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch filtered all-India road segments from SQLite database"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            query = "SELECT * FROM roadbounce_surveys WHERE 1=1"
            params = []
            if city and city.upper() != 'ALL':
                query += " AND UPPER(city) LIKE ?"
                params.append(f"%{city.upper()}%")
            if state and state.upper() != 'ALL':
                query += " AND UPPER(state) LIKE ?"
                params.append(f"%{state.upper()}%")
            if status and status.upper() != 'ALL':
                query += " AND condition_status = ?"
                params.append(status.upper())
            if min_iri is not None:
                query += " AND iri_score >= ?"
                params.append(min_iri)
            if search:
                query += " AND (UPPER(road_name) LIKE ? OR UPPER(road_id) LIKE ? OR UPPER(city) LIKE ?)"
                params.extend([f"%{search.upper()}%", f"%{search.upper()}%", f"%{search.upper()}%"])
            
            query += " ORDER BY CASE condition_status WHEN 'RED' THEN 1 WHEN 'YELLOW' THEN 2 ELSE 3 END, iri_score DESC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def remediate_road(road_id: str, target_status: str = 'GREEN', 
                       remediated_by: str = 'Municipal Road Maintenance Crew', 
                       notes: str = '') -> Optional[Dict[str, Any]]:
        """Improve and convert a Yellow road into Green, or Red road into Yellow/Green"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM roadbounce_surveys WHERE road_id = ?", (road_id,))
            row = cursor.fetchone()
            if not row:
                return None
            
            orig = dict(row)
            # New improved metrics based on target_status
            if target_status.upper() == 'GREEN':
                new_iri = 1.6
                new_pci = 95.0
                new_gforce = 0.22
                new_potholes = 0
                new_cracks = 'None'
                new_action = f"Successfully remediated to GREEN by {remediated_by}. {notes}".strip()
                new_cost = 0.0
            else: # YELLOW
                new_iri = 3.0
                new_pci = 70.0
                new_gforce = 1.10
                new_potholes = 1
                new_cracks = 'Low'
                new_action = f"Emergency stabilization applied. Final resurfacing scheduled. {notes}".strip()
                new_cost = 25000.0

            cursor.execute('''
                UPDATE roadbounce_surveys 
                SET condition_status = ?, iri_score = ?, pci_score = ?, vibration_gforce_peak = ?,
                    pothole_count = ?, crack_severity = ?, recommended_action = ?, estimated_cost_inr = ?,
                    remediated_at = CURRENT_TIMESTAMP, remediated_by = ?, updated_at = CURRENT_TIMESTAMP
                WHERE road_id = ?
            ''', (target_status.upper(), new_iri, new_pci, new_gforce, new_potholes, new_cracks, new_action, new_cost, remediated_by, road_id))
            conn.commit()

            cursor.execute("SELECT * FROM roadbounce_surveys WHERE road_id = ?", (road_id,))
            return dict(cursor.fetchone())
        finally:
            conn.close()

    @staticmethod
    def ingest_roadbounce_survey(data: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest live smartphone accelerometer + GPS + Camera survey data"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        import json
        try:
            road_id = data.get("road_id")
            iri = float(data.get("iri_score", 2.2))
            pci = float(data.get("pci_score", 85.0))
            gforce = float(data.get("vibration_gforce_peak", 0.5))
            status = "GREEN" if iri < 2.5 else ("YELLOW" if iri <= 4.0 else "RED")
            
            cursor.execute('''
                INSERT INTO roadbounce_surveys 
                (road_id, road_name, city, state, latitude, longitude, condition_status, iri_score, pci_score, 
                 vibration_gforce_peak, speed_kmh, pothole_count, crack_severity, proof_image_url, 
                 proof_telemetry_json, recommended_action, estimated_cost_inr)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(road_id) DO UPDATE SET
                    condition_status = excluded.condition_status,
                    iri_score = excluded.iri_score,
                    pci_score = excluded.pci_score,
                    vibration_gforce_peak = excluded.vibration_gforce_peak,
                    pothole_count = excluded.pothole_count,
                    last_surveyed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
            ''', (
                road_id,
                data.get("road_name", "Surveyed Route"),
                data.get("city", "New Delhi"),
                data.get("state", "Delhi"),
                float(data.get("latitude", 28.6139)),
                float(data.get("longitude", 77.2090)),
                status,
                iri,
                pci,
                gforce,
                float(data.get("speed_kmh", 45.0)),
                int(data.get("pothole_count", 0)),
                data.get("crack_severity", "None"),
                data.get("proof_image_url", "/static/assets/damaged_roads/0000000000000000_100913988636_11_jpg.rf.025a17688dbcb644485501867cfa24b4.jpg"),
                json.dumps(data.get("telemetry", {})),
                data.get("recommended_action", "Automated mobile survey update"),
                float(data.get("estimated_cost_inr", 0.0))
            ))
            conn.commit()
            cursor.execute("SELECT * FROM roadbounce_surveys WHERE road_id = ?", (road_id,))
            return dict(cursor.fetchone())
        finally:
            conn.close()

    @staticmethod
    def get_roadbounce_kpis() -> Dict[str, Any]:
        """Aggregate national condition metrics and cost savings"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) as total, AVG(iri_score) as avg_iri, AVG(pci_score) as avg_pci FROM roadbounce_surveys")
            overall = dict(cursor.fetchone())
            
            cursor.execute("SELECT condition_status, COUNT(*) as count FROM roadbounce_surveys GROUP BY condition_status")
            status_counts = {"GREEN": 0, "YELLOW": 0, "RED": 0}
            for row in cursor.fetchall():
                status_counts[row['condition_status']] = row['count']

            cursor.execute("SELECT COUNT(DISTINCT city) as total_cities, COUNT(DISTINCT state) as total_states FROM roadbounce_surveys")
            geo = dict(cursor.fetchone())

            cursor.execute("SELECT SUM(estimated_cost_inr) as total_repair_backlog FROM roadbounce_surveys")
            backlog = cursor.fetchone()['total_repair_backlog'] or 0.0

            cursor.execute("SELECT COUNT(*) as remediated_count FROM roadbounce_surveys WHERE remediated_at IS NOT NULL")
            remediated = cursor.fetchone()['remediated_count']

            return {
                "total_roads_monitored": overall['total'],
                "national_avg_iri": round(overall['avg_iri'] or 0.0, 2),
                "national_avg_pci": round(overall['avg_pci'] or 0.0, 1),
                "green_count": status_counts.get("GREEN", 0),
                "yellow_count": status_counts.get("YELLOW", 0),
                "red_count": status_counts.get("RED", 0),
                "total_cities": geo['total_cities'],
                "total_states": geo['total_states'],
                "total_repair_backlog_inr": backlog,
                "remediated_roads_count": remediated,
                "preventative_cost_saved_inr": remediated * 125000.0 # Estimated savings per early yellow->green fix
            }
        finally:
            conn.close()


    @staticmethod
    def add_realtime_defect(defect_code: str, class_name: str, severity: str, confidence: float,
                            latitude: float, longitude: float, road_id: str = None, 
                            image_url: str = None, vehicle_id: str = 'VEH-IN-01', 
                            data_source: str = 'LIVE_CV_STREAM') -> int:
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO realtime_defects (defect_code, class_name, severity, confidence, latitude, longitude, road_id, image_url, vehicle_id, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (defect_code, class_name, severity, confidence, latitude, longitude, road_id, image_url, vehicle_id, data_source))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def get_realtime_defects(lat: float = None, lng: float = None, radius_km: float = 25.0, 
                             road_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            if road_id:
                cursor.execute("SELECT * FROM realtime_defects WHERE road_id = ? ORDER BY captured_at DESC LIMIT ?", (road_id, limit))
                return [dict(row) for row in cursor.fetchall()]
            
            cursor.execute("SELECT * FROM realtime_defects ORDER BY captured_at DESC LIMIT ?", (limit * 2,))
            rows = [dict(row) for row in cursor.fetchall()]
            
            if lat is not None and lng is not None:
                import math
                def dist(lat1, lon1, lat2, lon2):
                    R = 6371.0
                    dlat = math.radians(lat2 - lat1)
                    dlon = math.radians(lon2 - lon1)
                    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
                    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                
                filtered = []
                for r in rows:
                    d = dist(lat, lng, r['latitude'], r['longitude'])
                    if d <= radius_km:
                        r['distance_km'] = round(d, 2)
                        filtered.append(r)
                return sorted(filtered, key=lambda x: x.get('distance_km', 0))[:limit]
            
            return rows[:limit]
        finally:
            conn.close()

    @staticmethod
    def add_live_telemetry(vehicle_id: str, latitude: float, longitude: float, 
                           speed_kmh: float = 40.0, g_force: float = 1.0, 
                           vibration_index: float = 0.5, road_id: str = None, 
                           data_source: str = 'LIVE_SENSOR') -> int:
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sensor_telemetry_live (vehicle_id, road_id, latitude, longitude, speed_kmh, g_force, vibration_index, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (vehicle_id, road_id, latitude, longitude, speed_kmh, g_force, vibration_index, data_source))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def get_latest_telemetry(road_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            if road_id:
                cursor.execute("SELECT * FROM sensor_telemetry_live WHERE road_id = ? ORDER BY recorded_at DESC LIMIT ?", (road_id, limit))
            else:
                cursor.execute("SELECT * FROM sensor_telemetry_live ORDER BY recorded_at DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_nearby_roadbounce_roads(lat: float, lng: float, radius_km: float = 50.0) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM roadbounce_surveys")
            roads = [dict(r) for r in cursor.fetchall()]
            
            import math
            def dist(lat1, lon1, lat2, lon2):
                R = 6371.0
                dlat = math.radians(lat2 - lat1)
                dlon = math.radians(lon2 - lon1)
                a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
                return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

            nearby = []
            for road in roads:
                d = dist(lat, lng, road['latitude'], road['longitude'])
                if d <= radius_km:
                    road['distance_km'] = round(d, 2)
                    nearby.append(road)
            
            # Sort by distance
            nearby.sort(key=lambda x: x['distance_km'])
            return nearby
        finally:
            conn.close()


    # =========================================================================
    # GOVERNMENT ROAD REGISTRY & EVIDENCE OPERATIONS
    # =========================================================================
    @staticmethod
    def add_or_update_gov_segment(seg_data: Dict[str, Any]) -> str:
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.cursor()
            
            # Compute score and zone
            c_score = seg_data.get("condition_score")
            if c_score is None:
                c_score = seg_data.get("health_score")
            if c_score is not None:
                try:
                    c_score = float(c_score)
                except (ValueError, TypeError):
                    c_score = None
                    
            zone = seg_data.get("zone")
            if not zone and c_score is not None:
                if c_score < 40.0:
                    zone = "RED"
                elif c_score <= 70.0:
                    zone = "YELLOW"
                else:
                    zone = "GREEN"
            elif not zone:
                zone = seg_data.get("condition_status", "GREEN")
                if zone not in ["RED", "YELLOW", "GREEN"]:
                    zone = "GREEN"

            cursor.execute('''
                INSERT INTO gov_road_segments (
                    segment_id, road_name, road_type, highway_code, state, district, city, pincode,
                    jurisdiction_agency, length_km, polyline_json, center_lat, center_lng,
                    speed_limit_kmh, lanes, condition_status, health_score, confidence, iri_score, pci_score,
                    vibration_gforce_peak, pothole_count, crack_count, last_surveyed_at,
                    condition_score, zone
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(segment_id) DO UPDATE SET
                    condition_status = excluded.condition_status,
                    health_score = excluded.health_score,
                    condition_score = excluded.condition_score,
                    zone = excluded.zone,
                    confidence = excluded.confidence,
                    iri_score = excluded.iri_score,
                    pci_score = excluded.pci_score,
                    vibration_gforce_peak = excluded.vibration_gforce_peak,
                    pothole_count = excluded.pothole_count,
                    crack_count = excluded.crack_count,
                    last_surveyed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
            ''', (
                seg_data["segment_id"],
                seg_data["road_name"],
                seg_data.get("road_type", "Urban Arterial"),
                seg_data.get("highway_code", ""),
                seg_data.get("state", "Delhi"),
                seg_data.get("district", "Central"),
                seg_data.get("city", "New Delhi"),
                seg_data.get("pincode", "110001"),
                seg_data.get("jurisdiction_agency", "Public Works Department"),
                float(seg_data.get("length_km", 1.0)),
                json.dumps(seg_data.get("polyline", [])),
                float(seg_data["center_lat"]),
                float(seg_data["center_lng"]),
                int(seg_data.get("speed_limit_kmh", 50)),
                int(seg_data.get("lanes", 4)),
                seg_data.get("condition_status", zone),
                c_score if c_score is not None else seg_data.get("health_score"),
                float(seg_data.get("confidence", 0.0)),
                seg_data.get("iri_score"),
                seg_data.get("pci_score"),
                float(seg_data.get("vibration_gforce_peak", 0.25)),
                int(seg_data.get("pothole_count", 0)),
                int(seg_data.get("crack_count", 0)),
                seg_data.get("last_surveyed_at"),
                c_score,
                zone
            ))
            conn.commit()
            return seg_data["segment_id"]
        finally:
            conn.close()

    @staticmethod
    def get_gov_segments(state: str = None, district: str = None, city: str = None, 
                         status: str = None, pincode: str = None) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM gov_road_segments WHERE 1=1"
            params = []
            if state and state.upper() != 'ALL':
                query += " AND UPPER(state) = ?"
                params.append(state.upper())
            if district and district.upper() != 'ALL':
                query += " AND UPPER(district) = ?"
                params.append(district.upper())
            if city and city.upper() != 'ALL':
                query += " AND UPPER(city) = ?"
                params.append(city.upper())
            if pincode:
                query += " AND pincode = ?"
                params.append(pincode)
            if status and status.upper() != 'ALL':
                query += " AND condition_status = ?"
                params.append(status.upper())

            cursor.execute(query, params)
            rows = [dict(r) for r in cursor.fetchall()]
            for r in rows:
                if r.get("polyline_json"):
                    try:
                        r["polyline"] = json.loads(r["polyline_json"])
                    except:
                        r["polyline"] = []
            return rows
        finally:
            conn.close()

    @staticmethod
    def get_gov_segment_by_id(segment_id: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gov_road_segments WHERE segment_id = ?", (segment_id,))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                if d.get("polyline_json"):
                    try:
                        d["polyline"] = json.loads(d["polyline_json"])
                    except:
                        d["polyline"] = []
                return d
            return None
        finally:
            conn.close()

    @staticmethod
    def add_road_evidence(segment_id: str, latitude: float, longitude: float, source_type: str,
                          device_id: str, image_url: str, defects_json: str, confidence: float = 0.9) -> int:
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.cursor()
            ev_id = f"EV-{int(time.time())}-{random.randint(100, 999)}"
            cursor.execute('''
                INSERT INTO road_evidence_records (evidence_id, segment_id, latitude, longitude, source_type, device_id, image_url, defects_detected_json, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (ev_id, segment_id, latitude, longitude, source_type, device_id, image_url, defects_json, confidence))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def get_road_evidence(segment_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM road_evidence_records WHERE segment_id = ? ORDER BY captured_at DESC LIMIT ?", (segment_id, limit))
            rows = [dict(r) for r in cursor.fetchall()]
            for r in rows:
                if r.get("defects_detected_json"):
                    try:
                        r["defects"] = json.loads(r["defects_detected_json"])
                    except:
                        r["defects"] = []
            return rows
        finally:
            conn.close()

    @staticmethod
    def add_repair_verification_log(work_order_id: int, segment_id: str, road_name: str,
                                   before_photo_url: str, after_photo_url: str,
                                   verification_status: str, is_approved: bool,
                                   pavement_quality_score: float, engineering_findings: str,
                                   prescribed_action: str, blockchain_tx_hash: str = None) -> int:
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO repair_verification_logs (
                    work_order_id, segment_id, road_name, before_photo_url, after_photo_url,
                    verification_status, is_approved, pavement_quality_score, engineering_findings,
                    prescribed_action, blockchain_tx_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                work_order_id, segment_id, road_name, before_photo_url, after_photo_url,
                verification_status, 1 if is_approved else 0, pavement_quality_score,
                engineering_findings, prescribed_action, blockchain_tx_hash
            ))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

if __name__ == "__main__":
    init_database()
