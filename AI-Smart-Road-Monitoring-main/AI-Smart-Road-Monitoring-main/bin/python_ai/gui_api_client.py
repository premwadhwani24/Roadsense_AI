import requests
import json

API_BASE = "http://127.0.0.1:5000"


# -----------------------------------------------------------
# SAFE JSON PARSER (prevents GUI crash)
# -----------------------------------------------------------
def safe_json(response):
    try:
        return response.json()
    except Exception:
        return {
            "status": "error",
            "message": "Invalid or empty JSON response",
            "raw": response.text
        }


# -----------------------------------------------------------
# 1. UPLOAD IMAGE → PREDICT POTHOLE
# -----------------------------------------------------------
def upload_image_and_predict(image_path):
    try:
        files = {"image": open(image_path, "rb")}
        r = requests.post(f"{API_BASE}/api/predict_potholes", files=files)

        return safe_json(r)

    except Exception as e:
        return {"status": "error", "message": str(e)}


# -----------------------------------------------------------
# 2. UPLOAD SENSOR CSV → SURFACE ANALYSIS
# -----------------------------------------------------------
def upload_sensor_and_analyze(csv_path):
    try:
        files = {"sensor": open(csv_path, "rb")}   # FIXED FIELD NAME
        r = requests.post(f"{API_BASE}/api/analyze_surface", files=files)

        return safe_json(r)

    except Exception as e:
        return {"status": "error", "message": str(e)}


# -----------------------------------------------------------
# 3. CHECK API STATUS
# -----------------------------------------------------------
def check_api_status():
    try:
        r = requests.get(f"{API_BASE}/api/status")
        return safe_json(r)

    except Exception as e:
        return {"status": "error", "message": str(e)}
