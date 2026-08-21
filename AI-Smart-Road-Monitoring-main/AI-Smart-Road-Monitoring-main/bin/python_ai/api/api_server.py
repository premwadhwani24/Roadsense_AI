import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

# ---------------------------------------------------------
# FIX: ensure python_ai root is importable
# ---------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))     # python_ai/api
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)                  # python_ai

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

print("📌 PYTHON PATH (top 3):", sys.path[:3])

# ---------------------------------------------------------
# SAFE IMPORTS (NOW WORK)
# ---------------------------------------------------------
from models.pothole_detection import predict_pothole
from models.road_surface_analysis import analyze_surface
from models.depth_model import calculate_geometry

# ---------------------------------------------------------
# UPLOAD DIRECTORIES
# ---------------------------------------------------------
UPLOAD_IMG = os.path.join(PROJECT_ROOT, "uploads", "images")
UPLOAD_SENSOR = os.path.join(PROJECT_ROOT, "uploads", "sensor")
os.makedirs(UPLOAD_IMG, exist_ok=True)
os.makedirs(UPLOAD_SENSOR, exist_ok=True)

# ---------------------------------------------------------
# FLASK APP
# ---------------------------------------------------------
app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------
# ROOT ENDPOINT (FIXES 404)
# ---------------------------------------------------------
@app.get("/")
def home():
    return jsonify({
        "status": "OK",
        "service": "AI Smart Road Monitoring – Python API",
        "endpoints": [
            "/",
            "/api/status",
            "/api/predict_potholes",
            "/api/analyze_surface",
            "/api/calc_geometry"
        ]
    }), 200

# ---------------------------------------------------------
# API: Pothole Detection
# ---------------------------------------------------------
@app.post("/api/predict_potholes")
def api_predict_potholes():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        f = request.files["image"]
        path = os.path.join(UPLOAD_IMG, f.filename)
        f.save(path)

        return jsonify({
            "status": "ok",
            "prediction": predict_pothole(path)
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

# ---------------------------------------------------------
# API: Surface Analysis
# ---------------------------------------------------------
@app.post("/api/analyze_surface")
def api_analyze_surface():
    try:
        if "sensor" not in request.files:
            return jsonify({"error": "No sensor file"}), 400

        f = request.files["sensor"]
        path = os.path.join(UPLOAD_SENSOR, f.filename)
        f.save(path)

        return jsonify({
            "status": "ok",
            "analysis": analyze_surface(path)
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

# ---------------------------------------------------------
# API: Geometry Calculation
# ---------------------------------------------------------
@app.post("/api/calc_geometry")
def api_calc_geometry():
    try:
        payload = request.json
        if not payload:
            return jsonify({"error": "Missing JSON"}), 400

        return jsonify({
            "status": "ok",
            "geometry": calculate_geometry(payload)
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

# ---------------------------------------------------------
# API HEALTH
# ---------------------------------------------------------
@app.get("/api/status")
def api_status():
    return jsonify({"status": "running", "ping": True})

# ---------------------------------------------------------
if __name__ == "__main__":
    print("\n🚀 Python AI API running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
