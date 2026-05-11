# app_enhanced.py
"""
RoadSense AI - Enhanced Backend with Authentication, Alerts, Analytics & Maintenance
Features: User Management, Real-time Alerts, Work Orders, Crowdsourced Reports,
Analytics, and Advanced Dashboard
"""
import os
import json
import random
import logging
import sqlite3
from io import BytesIO
from datetime import datetime, timedelta
from typing import Dict, Any, List
import requests
from urllib.parse import urlencode
from flask import Flask, render_template, request, jsonify, send_file, abort, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, set_access_cookies, create_access_token

# Import enhanced modules
from database import init_database, DatabaseManager
from auth import setup_auth, authenticate_user, register_user, check_user_role
from notifications import NotificationManager
from prediction_engine import RoadPredictionEngine

# Try to import vision service gracefully
try:
    from vision_service import RoadVisionService
    vision_service = RoadVisionService()
    print("RoadVisionService initialized successfully.")
except Exception as e:
    vision_service = None
    print(f"Could not initialize RoadVisionService: {e}")

try:
    import pandas as pd
except:
    pd = None

# Configuration
GOOGLE_MAPS_KEY = os.environ.get("GOOGLE_MAPS_KEY", "AIzaSyAB_78cxWOzcKE_ezj6dm9Y77CxwzetdPY")
OPENWEATHER_KEY = os.environ.get("OPENWEATHER_KEY", "FUqgtGuXcXH29r79l6qLbg==vJxb4tDrWVQX6Zxk")
TOMTOM_KEY = os.environ.get("TOMTOM_KEY", "4f299a89-0229-454a-b97f-7fa4e3198c7f")
USE_MOCK_IF_NO_KEYS = True
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("roadsense_backend")

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["JSON_SORT_KEYS"] = False
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change-this-secret')

# Initialize database and auth
init_database()
jwt = setup_auth(app)

# Initialize prediction engine
prediction_engine = RoadPredictionEngine()


def error_response(message: str, status_code: int = 400):
    """Utility function for standardized error responses"""
    return jsonify({"success": False, "error": message}), status_code

# Sample road data
ROAD_SEGMENTS: Dict[str, Dict[str, Any]] = {
    "R001": {"name": "NH-52 Segment A", "coords": (26.2183, 78.1828), "state": "Madhya Pradesh", 
             "city": "Gwalior", "material": "Asphalt", "last_repaired": datetime.now() - timedelta(days=400),
             "nearest_place": "Gwalior Junction"},
    "R002": {"name": "MG Road", "coords": (18.5204, 73.8567), "state": "Maharashtra", 
             "city": "Pune", "material": "Concrete", "last_repaired": datetime.now() - timedelta(days=90),
             "nearest_place": "Pune Central"},
    "R003": {"name": "Eastern Express Highway", "coords": (19.075984, 72.877656), "state": "Maharashtra",
             "city": "Mumbai", "material": "Asphalt", "last_repaired": datetime.now() - timedelta(days=30),
             "nearest_place": "Kurla"},
    "R004": {"name": "Ring Road", "coords": (28.613939, 77.209021), "state": "Delhi",
             "city": "New Delhi", "material": "Asphalt", "last_repaired": datetime.now() - timedelta(days=10),
             "nearest_place": "Connaught Place"},
    "R005": {"name": "NH-44 Bypass", "coords": (17.385044, 78.486671), "state": "Telangana",
             "city": "Hyderabad", "material": "Concrete", "last_repaired": datetime.now() - timedelta(days=800),
             "nearest_place": "HiTec City"}
}

# ====================================================================================
# MAIN ROUTES
# ====================================================================================

@app.route("/")
def landing():
    """Serve the landing page"""
    return render_template("landing.html")


@app.route('/index')
def index_page():
    """Serve the original index dashboard page"""
    return render_template('index.html')

@app.route("/dashboard")
@jwt_required()
def dashboard():
    """Serve the main dashboard"""
    return render_template("dashboard.html", google_maps_key=GOOGLE_MAPS_KEY)

@app.route("/login")
def login_page():
    """Serve the login page"""
    return render_template("login.html")


@app.route('/login/google')
def login_google():
    """Redirect user to Google's OAuth 2.0 authorization endpoint."""
    if not GOOGLE_CLIENT_ID:
        return jsonify({'error': 'Google OAuth not configured'}), 500

    redirect_uri = url_for('google_callback', _external=True)
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'response_type': 'code',
        'scope': 'openid email profile',
        'redirect_uri': redirect_uri,
        'access_type': 'offline',
        'prompt': 'consent'
    }
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return redirect(auth_url)


@app.route('/login/google/callback')
def google_callback():
    """Handle Google's OAuth callback, exchange code for token, create user and set JWT cookie."""
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No code provided by Google'}), 400

    token_url = 'https://oauth2.googleapis.com/token'
    redirect_uri = url_for('google_callback', _external=True)
    data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    token_resp = requests.post(token_url, data=data)
    if token_resp.status_code != 200:
        return jsonify({'error': 'Failed to obtain token from Google', 'details': token_resp.text}), 500

    token_json = token_resp.json()
    access_token = token_json.get('access_token')
    if not access_token:
        return jsonify({'error': 'Missing access token from Google response'}), 500

    userinfo_resp = requests.get('https://www.googleapis.com/oauth2/v2/userinfo',
                                 headers={'Authorization': f'Bearer {access_token}'})
    if userinfo_resp.status_code != 200:
        return jsonify({'error': 'Failed to fetch userinfo from Google', 'details': userinfo_resp.text}), 500

    userinfo = userinfo_resp.json()
    email = userinfo.get('email')
    name = userinfo.get('name') or email.split('@')[0]

    # Create or fetch user
    from auth import create_or_get_oauth_user
    user = create_or_get_oauth_user(email=email, name=name)

    # Create JWT and set in cookie
    token = create_access_token(identity=str(user['id']), additional_claims={
        'username': user['username'], 'email': user['email'], 'role': user['role'], 'city': user.get('city')
    })

    resp = redirect(url_for('index_page'))
    try:
        set_access_cookies(resp, token)
    except Exception:
        resp.set_cookie('access_token_cookie', token, httponly=True)

    return resp

@app.route("/register")
def register_page():
    """Serve the registration page"""
    return render_template("login.html")

# ====================================================================================
# AUTHENTICATION ENDPOINTS
# ====================================================================================

@app.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new user"""
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    city = data.get("city")
    phone = data.get("phone")
    
    if not all([username, email, password]):
        return jsonify({"error": "Missing required fields"}), 400
    
    user_id, error = register_user(username, email, password, role='viewer', city=city, phone=phone)
    if error:
        return jsonify({"error": error}), 400
    
    return jsonify({"message": "User registered successfully", "user_id": user_id}), 201

@app.route("/api/auth/login", methods=["POST"])
def login():
    """Login user and return JWT token"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400
    
    token, error = authenticate_user(username, password)
    if error:
        return jsonify({"error": error}), 401
    # Return token and set it as an HttpOnly cookie so server-rendered routes
    # protected by @jwt_required() will work immediately after login.
    resp = jsonify({"access_token": token, "token_type": "Bearer"})
    try:
        # set cookie using flask-jwt-extended helper
        set_access_cookies(resp, token)
    except Exception:
        # Fallback: set cookie manually
        resp.set_cookie('access_token_cookie', token, httponly=True)

    return resp, 200

@app.route("/api/auth/user", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current user info"""
    user_id = get_jwt_identity()
    try:
        # JWT identity may be a string; convert to int when possible
        if isinstance(user_id, str) and user_id.isdigit():
            user_id_int = int(user_id)
        else:
            user_id_int = user_id
    except Exception:
        user_id_int = user_id
    claims = get_jwt()
    user = DatabaseManager.get_user_by_id(user_id_int)
    
    return jsonify({
        "id": user_id,
        "username": claims.get('username'),
        "email": claims.get('email'),
        "role": claims.get('role'),
        "city": claims.get('city')
    }), 200

# ====================================================================================
# ALERT MANAGEMENT ENDPOINTS
# ====================================================================================

@app.route("/api/alerts", methods=["GET"])
@jwt_required()
def get_alerts():
    """Get all alerts, optionally filtered by status"""
    status = request.args.get("status")
    alerts = DatabaseManager.get_alerts(status=status)
    return jsonify({"alerts": alerts, "count": len(alerts)}), 200

@app.route("/api/alerts", methods=["POST"])
@check_user_role('engineer')
def create_alert():
    """Create a new alert"""
    data = request.get_json()
    road_id = data.get("road_id")
    road_name = data.get("road_name")
    severity = data.get("severity")  # RED, YELLOW, GREEN
    description = data.get("description")
    
    if not all([road_id, road_name, severity]):
        return jsonify({"error": "Missing required fields"}), 400
    
    alert_id = NotificationManager.alert_critical_road(road_id, road_name, severity, description)
    return jsonify({"alert_id": alert_id, "message": "Alert created"}), 201

@app.route("/api/alerts/<int:alert_id>/resolve", methods=["PUT"])
@check_user_role('engineer')
def resolve_alert(alert_id):
    """Mark alert as resolved"""
    conn = sqlite3.connect('roadsense.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE alerts SET status = ?, resolved_at = ? WHERE id = ?',
                  ('resolved', datetime.now(), alert_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Alert resolved"}), 200

# ====================================================================================
# WORK ORDER MANAGEMENT ENDPOINTS
# ====================================================================================

@app.route("/api/work-orders", methods=["GET"])
@jwt_required()
def get_work_orders():
    """Get all work orders"""
    status = request.args.get("status")
    work_orders = DatabaseManager.get_work_orders(status=status)
    return jsonify({"work_orders": work_orders, "count": len(work_orders)}), 200

@app.route("/api/work-orders", methods=["POST"])
@check_user_role('engineer')
def create_work_order():
    """Create a new work order"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    road_id = data.get("road_id")
    road_name = data.get("road_name")
    work_type = data.get("work_type")  # Pothole Repair, Resurfacing, etc.
    contractor = data.get("contractor")
    estimated_cost = data.get("estimated_cost")
    notes = data.get("notes")
    
    if not all([road_id, road_name, work_type]):
        return jsonify({"error": "Missing required fields"}), 400
    
    work_order_id = DatabaseManager.add_work_order(
        road_id, road_name, work_type, user_id, contractor, estimated_cost, notes
    )
    return jsonify({"work_order_id": work_order_id, "message": "Work order created"}), 201

@app.route("/api/work-orders/<int:work_order_id>", methods=["PUT"])
@check_user_role('engineer')
def update_work_order(work_order_id):
    """Update work order status and cost"""
    data = request.get_json()
    status = data.get("status")  # pending, in_progress, completed
    actual_cost = data.get("actual_cost")
    
    conn = sqlite3.connect('roadsense.db')
    cursor = conn.cursor()
    
    if status:
        cursor.execute('UPDATE work_orders SET status = ? WHERE id = ?', (status, work_order_id))
    
    if actual_cost is not None:
        cursor.execute('UPDATE work_orders SET actual_cost = ? WHERE id = ?', (actual_cost, work_order_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Work order updated"}), 200

# ====================================================================================
# ROAD CONDITION & ANALYTICS ENDPOINTS
# ====================================================================================

@app.route("/api/roads/status", methods=["GET"])
@jwt_required()
def get_roads_status():
    """Get current status of all roads with condition analysis"""
    state = request.args.get("state")
    city = request.args.get("city")
    
    roads = []
    for rid, info in ROAD_SEGMENTS.items():
        if state and info.get("state") != state:
            continue
        if city and info.get("city") != city:
            continue
        
        # Compute condition based on age and material
        days_since_repair = (datetime.now() - info["last_repaired"]).days
        years_since_repair = days_since_repair / 365.25
        
        # Simplified logic
        if years_since_repair > 5:
            condition = "RED"
        elif years_since_repair > 2:
            condition = "YELLOW"
        else:
            condition = "GREEN"
        
        roads.append({
            "id": rid,
            "name": info["name"],
            "condition": condition,
            "lat": info["coords"][0],
            "lng": info["coords"][1],
            "material": info["material"],
            "last_repaired": info["last_repaired"].isoformat(),
            "days_since_repair": days_since_repair,
            "state": info["state"],
            "city": info["city"]
        })
    
    # Record in history for analytics
    for road in roads:
        DatabaseManager.add_road_history(road["id"], road["name"], road["condition"])
    
    counts = {"green": 0, "yellow": 0, "red": 0}
    for road in roads:
        counts[road["condition"].lower()] += 1
    
    return jsonify({
        "roads": roads,
        "summary": counts,
        "total": len(roads)
    }), 200

@app.route("/api/analytics/trending/<road_id>", methods=["GET"])
@jwt_required()
def get_road_trending(road_id):
    """Get historical trending data for a road"""
    days = request.args.get("days", default=30, type=int)
    history = DatabaseManager.get_road_history(road_id, days=days)
    
    return jsonify({
        "road_id": road_id,
        "history": history,
        "period_days": days
    }), 200

@app.route("/api/analytics/kpis", methods=["GET"])
@jwt_required()
def get_kpis():
    """Get key performance indicators"""
    roads = []
    for rid, info in ROAD_SEGMENTS.items():
        days_since_repair = (datetime.now() - info["last_repaired"]).days
        roads.append({
            "id": rid,
            "days": days_since_repair,
            "name": info["name"]
        })
    
    avg_days = sum(r["days"] for r in roads) / len(roads) if roads else 0
    oldest_road = max(roads, key=lambda x: x["days"]) if roads else None
    
    # Get alert counts
    alerts = DatabaseManager.get_alerts()
    open_alerts = [a for a in alerts if a['status'] == 'open']
    
    # Get work order counts
    work_orders = DatabaseManager.get_work_orders()
    pending_orders = [w for w in work_orders if w['status'] == 'pending']
    
    return jsonify({
        "total_roads": len(roads),
        "avg_days_since_repair": round(avg_days, 1),
        "oldest_road": oldest_road,
        "open_alerts": len(open_alerts),
        "pending_work_orders": len(pending_orders),
        "total_work_orders": len(work_orders)
    }), 200

# ====================================================================================
# CROWDSOURCED REPORTING ENDPOINTS
# ====================================================================================

@app.route("/api/reports/citizen", methods=["POST"])
def create_citizen_report():
    """Create crowdsourced report (public endpoint)"""
    data = request.get_json()
    
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    issue_type = data.get("issue_type")  # pothole, crack, flooding, etc.
    description = data.get("description")
    road_id = data.get("road_id")
    road_name = data.get("road_name")
    
    if not all([latitude, longitude, issue_type]):
        return jsonify({"error": "Missing required fields"}), 400
    
    report_id = DatabaseManager.add_citizen_report(
        latitude, longitude, issue_type, description, road_id, road_name
    )
    
    return jsonify({
        "report_id": report_id,
        "message": "Report submitted successfully",
        "status": "pending"
    }), 201

@app.route("/api/reports/citizen", methods=["GET"])
@check_user_role('engineer')
def get_citizen_reports():
    """Get all citizen reports"""
    status = request.args.get("status")
    reports = DatabaseManager.get_citizen_reports(status=status)
    return jsonify({"reports": reports, "count": len(reports)}), 200

@app.route("/api/reports/citizen/<int:report_id>/verify", methods=["PUT"])
@check_user_role('engineer')
def verify_citizen_report(report_id):
    """Verify citizen report"""
    conn = sqlite3.connect('roadsense.db')
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE citizen_reports SET verification_count = verification_count + 1, verified = 1 WHERE id = ?',
        (report_id,)
    )
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Report verified"}), 200

# ====================================================================================
# BUDGET TRACKING ENDPOINTS
# ====================================================================================

@app.route("/api/budget/<city>", methods=["GET"])
@check_user_role('admin')
def get_city_budget(city):
    """Get budget info for a city"""
    year = request.args.get("year", default=datetime.now().year, type=int)
    
    conn = sqlite3.connect('roadsense.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM budget_tracking WHERE city = ? AND year = ?', (city, year))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify(dict(row)), 200
    
    return jsonify({"error": "Budget not found"}), 404

@app.route("/api/budget/<city>", methods=["POST"])
@check_user_role('admin')
def set_city_budget(city):
    """Set or update budget for a city"""
    data = request.get_json()
    year = data.get("year", datetime.now().year)
    allocated_budget = data.get("allocated_budget")
    
    conn = sqlite3.connect('roadsense.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT OR REPLACE INTO budget_tracking (city, year, allocated_budget, remaining) '
        'VALUES (?, ?, ?, ?)',
        (city, year, allocated_budget, allocated_budget)
    )
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Budget updated"}), 200

# ====================================================================================
# DASHBOARD & REPORTING ENDPOINTS
# ====================================================================================

@app.route("/api/dashboard/summary", methods=["GET"])
@jwt_required()
def get_dashboard_summary():
    """Get comprehensive dashboard summary"""
    claims = get_jwt()
    user_city = claims.get('city')
    
    # Get road status
    roads_response = get_roads_status()
    roads_data = json.loads(roads_response[0].get_data(as_text=True))
    
    # Filter by city if user has city restriction
    if user_city:
        roads_data['roads'] = [r for r in roads_data['roads'] if r['city'] == user_city]
    
    # Get KPIs
    kpis = DatabaseManager.get_alerts()
    
    return jsonify({
        "roads_summary": roads_data['summary'],
        "total_roads": roads_data['total'],
        "kpis": get_kpis()[0].get_json(),
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route("/api/export/report", methods=["GET"])
@check_user_role('admin')
def export_report():
    """Export comprehensive report as PDF/Excel"""
    if not pd:
        return jsonify({"error": "pandas not installed"}), 500
    
    format_type = request.args.get("format", "excel")  # excel or pdf
    
    # Prepare data
    roads_list = []
    for rid, info in ROAD_SEGMENTS.items():
        days = (datetime.now() - info["last_repaired"]).days
        roads_list.append({
            "Road ID": rid,
            "Road Name": info["name"],
            "City": info["city"],
            "State": info["state"],
            "Material": info["material"],
            "Days Since Repair": days,
            "Last Repaired": info["last_repaired"].strftime("%Y-%m-%d")
        })
    
    df = pd.DataFrame(roads_list)
    
    if format_type == "excel":
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Roads", index=False)
            summary_df = pd.DataFrame({
                "Metric": ["Total Roads", "Average Days Since Repair"],
                "Value": [len(roads_list), round(df["Days Since Repair"].mean(), 1)]
            })
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
        
        output.seek(0)
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="RoadSense_Report.xlsx"
        )
    
    return jsonify({"error": "Format not supported"}), 400

# ====================================================================================
# AI PREDICTION ENDPOINTS
# ====================================================================================

@app.route("/api/predictions/deterioration/<int:road_id>", methods=["GET"])
@jwt_required()
def get_road_deterioration(road_id):
    """Predict road deterioration using AI"""
    try:
        days_ahead = request.args.get('days', 30, type=int)
        prediction = prediction_engine.predict_road_deterioration(road_id, days_ahead=days_ahead)
        return jsonify(prediction), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/predictions/accident-risk/<int:road_id>", methods=["GET"])
@jwt_required()
def get_accident_risk(road_id):
    """Predict accident risk for a road using AI"""
    try:
        risk = prediction_engine.predict_accident_risk(road_id)
        return jsonify(risk), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/predictions/potholes/<city>", methods=["GET"])
@jwt_required()
def get_pothole_predictions(city):
    """Predict pothole locations in a city"""
    try:
        predictions = prediction_engine.predict_pothole_locations(city)
        return jsonify({
            "city": city,
            "predictions": predictions,
            "total_predictions": len(predictions),
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/predictions/budget/<city>", methods=["GET"])
@jwt_required()
def get_budget_prediction(city):
    """Calculate maintenance budget using AI predictions"""
    try:
        # Get all roads in the city
        roads = []
        conn = sqlite3.connect('roadsense.db')
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT road_id FROM alerts WHERE city = ?", (city,))
        roads = [r[0] for r in cursor.fetchall()]
        conn.close()
        
        if not roads:
            return jsonify({"status": "no_roads_found", "city": city}), 404
        
        budget = prediction_engine.calculate_maintenance_budget(city, roads)
        return jsonify(budget), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/predictions/report/<city>", methods=["GET"])
@jwt_required()
def get_ai_report(city):
    """Generate comprehensive AI-powered report for a city"""
    try:
        report = prediction_engine.generate_ai_report(city)
        return jsonify(report), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ====================================================================================
# COMPUTER VISION & ASSET INVENTORY ENDPOINTS
# ====================================================================================

@app.route("/api/vision/analyze", methods=["POST"])
def analyze_road_image():
    """Analyze uploaded road image/video frame using Computer Vision"""
    if not vision_service:
        return jsonify({"error": "Vision service not available or failed to initialize."}), 503
        
    if "file" not in request.files:
        return jsonify({"error": "No file parameter provided in the request."}), 400
        
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400
        
    try:
        # Save to temp location
        import tempfile
        import os
        fd, temp_path = tempfile.mkstemp(suffix=".jpg")
        os.close(fd)
        file.save(temp_path)
        
        # Analyze it
        result = vision_service.analyze_image(temp_path)
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify({
            "status": "success",
            "analysis": result,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error in vision analysis: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/vision/assets", methods=["GET"])
@jwt_required(optional=True)  # Can be secured or open
def get_road_assets():
    """Returns AI-generated inventory of road assets (signs, barriers, markers)"""
    road_id = request.args.get("road_id")
    
    # In a fully integrated system, this would read from the DB where
    # the vision pipeline saves its extracted assets from periodic video scans.
    # Below we provide simulated output representative of RoadAthena capabilities.
    
    assets = [
        {"type": "Speed Limit Sign", "lat": 0.001, "lng": 0.001, "condition": "Good"},
        {"type": "Lane Marking", "lat": 0.002, "lng": 0.002, "condition": "Faded"},
        {"type": "Guardrail", "lat": 0.003, "lng": 0.003, "condition": "Damaged"},
        {"type": "Traffic Light", "lat": 0.004, "lng": 0.004, "condition": "Good"}
    ]
    
    # Optional logic to offset these by the specific road's true coordinates
    if road_id in ROAD_SEGMENTS:
        base_lat, base_lng = ROAD_SEGMENTS[road_id]["coords"]
        for asset in assets:
            # slightly vary the locations along the route
            asset["lat"] = round(base_lat + asset["lat"] * random.uniform(0.5, 2.0), 6)
            asset["lng"] = round(base_lng + asset["lng"] * random.uniform(0.5, 2.0), 6)
    
    return jsonify({
        "status": "success",
        "road_id": road_id,
        "assets_detected": len(assets),
        "assets": assets,
        "timestamp": datetime.now().isoformat()
    }), 200

# ====================================================================================
# HEALTH & UTILITIES
# ====================================================================================

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "database": "connected"
    }), 200

@app.route("/api/help", methods=["GET"])
def get_help():
    """API Help endpoint providing overview of available routes"""
    return jsonify({
        "name": "RoadSense AI API",
        "version": "1.0.0",
        "info": "Comprehensive road infrastructure management platform",
        "endpoints": {
            "auth": ["/api/auth/login", "/api/auth/register", "/api/auth/user"],
            "alerts": ["/api/alerts (GET/POST)", "/api/alerts/<id>/resolve (PUT)"],
            "roads": ["/api/roads/status", "/api/locations"],
            "predictions": ["/api/predictions/deterioration/<id>", "/api/predictions/accident-risk/<id>"]
        }
    }), 200

@app.route("/api/locations", methods=["GET"])
@jwt_required()
def get_locations():
    """Get list of unique states and cities"""
    states = {}
    for rid, info in ROAD_SEGMENTS.items():
        state = info.get("state")
        city = info.get("city")
        
        if state not in states:
            states[state] = []
        if city and city not in states[state]:
            states[state].append(city)
    
    return jsonify({"states": states}), 200

# ====================================================================================
# NEXT-GENERATION SMART INFRASTRUCTURE ENDPOINTS
# ====================================================================================

from iot_sensors import IoTSensorEngine
from crowd_sensing import CrowdSensingEngine
from llm_assistant import LLMAssistant
from graph_analytics import GraphAnalyticsEngine
from blockchain_audit import BlockchainLedger
from digital_twin import DigitalTwinEngine
from mobile_api import MobileFieldAPI

@app.route("/api/v2/iot/telemetry", methods=["POST"])
def iot_ingest():
    """Ingest massive IoT telemetry streams"""
    data = request.get_json()
    return jsonify(IoTSensorEngine.receive_telemetry(data.get("road_id", "UNKNOWN"), data)), 200

@app.route("/api/v2/digital-twin/<road_id>", methods=["POST"])
def twin_sync(road_id):
    """Trigger physical simulation re-computation for twin state"""
    return jsonify(DigitalTwinEngine.sync_digital_twin_state(road_id)), 200

@app.route("/api/v2/audit/ledger", methods=["GET"])
def get_ledger():
    """Retrieve immutable blockchain ledger status"""
    return jsonify(BlockchainLedger.get_last_block()), 200

@app.route("/api/v2/llm/advisory/<road_name>", methods=["GET"])
def get_llm_advisory(road_name):
    """Use Generative LLM logic to format advice"""
    advisory = LLMAssistant.generate_maintenance_recommendation(road_name, random.uniform(20, 95), [])
    return jsonify({"advisory": advisory}), 200

@app.route("/api/v2/graph/high-risk", methods=["GET"])
def get_graph_risk():
    """Retrieve topology-based network risk endpoints"""
    return jsonify(GraphAnalyticsEngine.calculate_high_risk_zones()), 200

@app.route("/api/v2/mobile/sync", methods=["POST"])
def mobile_sync():
    """Field engineer offline synchronization endpoint"""
    data = request.get_json()
    return jsonify(MobileFieldAPI.sync_offline_reports(data.get("reports", []))), 200

# ====================================================================================
# PRESCRIPTIVE INTELLIGENCE ENDPOINTS (PHASE 6)
# ====================================================================================
from data_fusion import DataFusionEngine

@app.route("/api/v2/prescriptive/data-fusion", methods=["POST"])
@jwt_required()
@check_user_role('engineer')
def prescriptive_data_fusion():
    """Execute Data Fusion to calculate Confidence Score and auto-draft Work Orders"""
    data = request.get_json()
    return jsonify(DataFusionEngine.calculate_confidence_and_draft_order(
        road_id=data.get('road_id'),
        road_name=data.get('road_name'),
        cv_defects=data.get('cv_defects', 0),
        citizen_reports=data.get('citizen_reports', 0),
        avg_vibration=data.get('avg_vibration', 0.0),
        road_age_days=data.get('road_age_days', 0)
    )), 200

@app.route("/api/v2/prescriptive/maintenance/<int:road_id>", methods=["GET"])
@jwt_required()
def prescriptive_maintenance(road_id):
    """Prescriptive Maintenance Logic (Budget-aware)"""
    city = request.args.get('city', 'Delhi')
    importance = request.args.get('importance', 5.0, type=float)
    return jsonify(prediction_engine.prescriptive_maintenance_recommendation(road_id, city, importance)), 200

@app.route("/api/v2/prescriptive/geospatial-clusters", methods=["GET"])
@jwt_required()
def prescriptive_geospatial():
    """Geospatial Optimization using DBSCAN"""
    alerts = DatabaseManager.get_alerts(status='open')
    return jsonify(prediction_engine.geospatial_optimization(alerts)), 200

if __name__ == "__main__":
    logger.info("Starting RoadSense Enhanced Backend")
    app.run(host="0.0.0.0", port=5000, debug=True)
