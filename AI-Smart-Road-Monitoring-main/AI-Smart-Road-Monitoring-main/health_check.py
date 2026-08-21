"""
health_check.py
Live status tester for Python AI API
"""

import requests
import json
import os

BASE_URL = "http://127.0.0.1:5000"

TEST_IMAGE = "python_ai/test_samples/test1.jpg"
TEST_SENSOR = "python_ai/test_samples/sample_sensor.csv"


def pretty(resp):
    try:
        return json.dumps(resp.json(), indent=2)
    except:
        return resp.text


def test_endpoint(name, method, url, files=None):
    print(f"\n--- Testing {name} ---")
    try:
        if method == "GET":
            r = requests.get(url, timeout=5)
        else:
            r = requests.post(url, files=files, timeout=10)

        print("Status:", r.status_code)
        print(pretty(r))
    except Exception as e:
        print("FAILED:", e)


def main():
    print("\n======================================")
    print("       SMART ROAD API HEALTH CHECK")
    print("======================================")

    test_endpoint("STATUS", "GET", BASE_URL + "/")

    if os.path.exists(TEST_IMAGE):
        test_endpoint(
            "POTHOLE DETECTION",
            "POST",
            BASE_URL + "/api/predict_potholes",
            files={"images[]": open(TEST_IMAGE, "rb")}
        )
    else:
        print("Skipping pothole test — test image missing")

    if os.path.exists(TEST_SENSOR):
        test_endpoint(
            "SURFACE ANALYSIS",
            "POST",
            BASE_URL + "/api/analyze_surface",
            files={"sensor_file": open(TEST_SENSOR, "rb")}
        )
    else:
        print("Skipping sensor test — file missing")

    # Optional geometry endpoint
    try:
        test_endpoint("GEOMETRY API", "GET", BASE_URL + "/api/geometry_test")
    except:
        print("Geometry endpoint not available")

    print("\nHealth check complete ✓")


if __name__ == "__main__":
    main()
