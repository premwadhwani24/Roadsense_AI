import os
import sys
import traceback
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# ---------------------------------------------------------
# CREATE FLASK APP (MUST BE FIRST)
# ---------------------------------------------------------
app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------
# PATH FIX (allow imports from python_ai)
# ---------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))   # python_ai/api
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)               # python_ai

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------
# SAFE IMPORTS
# ---------------------------------------------------------
from models.pothole_detection import predict_pothole
from models.road_surface_analysis import analyze_surface
from models.depth_model import calculate_geometry

UPLOAD_IMG = os.path.join(PROJECT_ROOT, "uploads", "images")
UPLOAD_SENSOR = os.path.join(PROJECT_ROOT, "uploads", "sensor")
os.makedirs(UPLOAD_IMG, exist_ok=True)
os.makedirs(UPLOAD_SENSOR, exist_ok=True)

# ---------------------------------------------------------
# ROOT (HEALTH CHECK)
# ---------------------------------------------------------
@app.get("/")
def home():
    return {
        "status": "Python AI API running",
        "time": datetime.now().isoformat()
    }

# ---------------------------------------------------------
# API STATUS
# ---------------------------------------------------------
@app.get("/api/status")
def api_status():
    return jsonify({"status": "API running", "ping": True})

# ---------------------------------------------------------
# SIMPLE GUI PAGE
# ---------------------------------------------------------
@app.get("/gui")
def gui():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Python AI Dashboard</title>
    </head>
    <body style="font-family:Arial; padding:30px;">
        <h2>🚀 Python AI API Dashboard</h2>
        <p>Status: <b style="color:green;">RUNNING</b></p>

        <ul>
            <li>📷 Pothole Detection</li>
            <li>📡 Road Surface Analysis</li>
            <li>📐 Geometry Calculation</li>
        </ul>

        <p>Backend for <b>AI Smart Road Monitoring System</b></p>
    </body>
    </html>
    """

# ---------------------------------------------------------
# IMAGE → POTHOLE DETECTION
# ---------------------------------------------------------
@app.post("/api/predict_potholes")
def api_predict_potholes():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image provided"}), 400

        f = request.files["image"]
        path = os.path.join(UPLOAD_IMG, f.filename)
        f.save(path)

        result = predict_pothole(path)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

# ---------------------------------------------------------
# SENSOR → SURFACE ANALYSIS
# ---------------------------------------------------------
@app.post("/api/analyze_surface")
def api_analyze_surface():
    try:
        f = request.files.get("sensor")
        if not f:
            return jsonify({"error": "No sensor file"}), 400

        path = os.path.join(UPLOAD_SENSOR, f.filename)
        f.save(path)

        result = analyze_surface(path)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------
# DEPTH → GEOMETRY
# ---------------------------------------------------------
@app.post("/api/calc_geometry")
def api_calc_geometry():
    try:
        payload = request.json
        result = calculate_geometry(payload)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------
# START SERVER (MUST BE LAST)
# ---------------------------------------------------------
if __name__ == "__main__":
    print("\n🚀 Python AI API running")
    print("➡ http://127.0.0.1:5000/")
    print("➡ http://127.0.0.1:5000/gui\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
