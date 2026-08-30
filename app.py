# app.py
"""
RoadSense AI - Backend
Author: Generated for user
Description:
    - Flask backend for RoadSense AI dashboard.
    - Provides endpoints:
        /                    -> renders index.html (injects google maps key)
        /api/locations       -> list of states -> cities
        /api/roads           -> list of road segments (optionally filtered by state/city)
        /api/aggregate       -> aggregated counts, avg traffic, oldest/newest repair
        /api/weather         -> proxy to weather provider (OpenWeather) or mock
        /api/traffic_flow    -> TomTom Flow for single point (or mock)
        /api/traffic_incidents -> TomTom Incidents in bbox (or mock)
        /api/get_current_status -> full realtime analysis combining traffic+weather+ml
        /api/bad_roads       -> returns only roads considered "not good"
        /api/classify        -> run classifier (rule-based / optional ML hook)
        /report/generate     -> generate Excel report from historical data
Notes:
    - Uses simulated sample road data if you don't have a DB.
    - To enable real traffic/weather set environment variables TOMTOM_KEY and OPENWEATHER_KEY
    - To customize, modify ROAD_SEGMENTS below or switch to a DB.
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
from flask import Flask, render_template, request, jsonify, send_file, abort

# Optional dependencies for Excel report generation
try:
    import pandas as pd  # used for report generation
except Exception as e:
    pd = None  # we'll check and raise helpful error if user tries to generate excel without pandas

# ---------------------------------------------------------------------------
# Configuration (set via env vars in production). Defaults here are for demo.
# ---------------------------------------------------------------------------
GOOGLE_MAPS_KEY = os.environ.get("GOOGLE_MAPS_KEY", "AIzaSyAB_78cxWOzcKE_ezj6dm9Y77CxwzetdPY")  # user-provided earlier
OPENWEATHER_KEY = os.environ.get("OPENWEATHER_KEY", "FUqgtGuXcXH29r79l6qLbg==vJxb4tDrWVQX6Zxk")  # user-provided earlier (assumed)
TOMTOM_KEY = os.environ.get("TOMTOM_KEY", "")  # if empty, code will use mock traffic
CARTO_API_KEY = os.environ.get("CARTO_API_KEY", "cb1_2k8n_1_26eca1d9286363e9242b4224")
USE_MOCK_IF_NO_KEYS = True  # allow local mock data when external keys missing

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("roadsense_backend")

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["JSON_SORT_KEYS"] = False

# ---------------------------------------------------------------------------
# Sample application data (fallback if you don't provide a DB or simulated_data file)
# - ROAD_SEGMENTS: dictionary keyed by ID with meta data and last_repaired datetime
# - HISTORICAL_DATA: small synthetic time series
# - CAUSAL_MAPPING: mapping of likely causal notes for reporting
# ---------------------------------------------------------------------------
# Note: modify these records to reflect your real dataset or connect to a DB.

ROAD_SEGMENTS: Dict[str, Dict[str, Any]] = {
    "R001": {
        "name": "NH-52 Segment A",
        "coords": (26.2183, 78.1828),
        "state": "Madhya Pradesh",
        "city": "Gwalior",
        "material": "Asphalt",
        "last_repaired": datetime.now() - timedelta(days=400),
        "nearest_place": "Gwalior Junction"
    },
    "R002": {
        "name": "MG Road",
        "coords": (18.5204, 73.8567),
        "state": "Maharashtra",
        "city": "Pune",
        "material": "Concrete",
        "last_repaired": datetime.now() - timedelta(days=90),
        "nearest_place": "Pune Central"
    },
    "R003": {
        "name": "Eastern Express Highway",
        "coords": (19.075984, 72.877656),
        "state": "Maharashtra",
        "city": "Mumbai",
        "material": "Asphalt",
        "last_repaired": datetime.now() - timedelta(days=30),
        "nearest_place": "Kurla"
    },
    "R004": {
        "name": "Ring Road",
        "coords": (28.613939, 77.209021),
        "state": "Delhi",
        "city": "New Delhi",
        "material": "Asphalt",
        "last_repaired": datetime.now() - timedelta(days=10),
        "nearest_place": "Connaught Place"
    },
    "R005": {
        "name": "NH-44 Bypass",
        "coords": (17.385044, 78.486671),
        "state": "Telangana",
        "city": "Hyderabad",
        "material": "Concrete",
        "last_repaired": datetime.now() - timedelta(days=800),
        "nearest_place": "HiTec City"
    }
}

# Small synthetic historical time series: date -> {road_id: {"zone": "GREEN"}}
HISTORICAL_DATA: Dict[str, Dict[str, Dict[str, Any]]] = {}
base_date = datetime.now().date() - timedelta(days=90)
for i in range(0, 91, 7):
    d = (base_date + timedelta(days=i)).isoformat()
    HISTORICAL_DATA[d] = {}
    for rid in ROAD_SEGMENTS:
        # create synthetic zones with some randomness
        p = random.random()
        if p > 0.85:
            z = "RED"
        elif p > 0.6:
            z = "YELLOW"
        else:
            z = "GREEN"
        HISTORICAL_DATA[d][rid] = {"zone": z}

CAUSAL_MAPPING: Dict[str, Dict[str, str]] = {
    "RED": {
        "R001": "Severe rutting and heavy truck traffic. Foundation weakening. Immediate structural repair required.",
        "R003": "Recurring flooding due to blocked drains; surface delamination."
    },
    "YELLOW": {
        "R002": "Surface cracking and localized potholes; schedule patching.",
        "R004": "Minor rutting, monitor for drainage issues."
    }
}

# ---------------------------------------------------------------------------
# Utility / Helper functions
# ---------------------------------------------------------------------------
def safe_get_road_list(state: str = None, city: str = None) -> List[Dict[str, Any]]:
    """Return list of roads optionally filtered by state and/or city."""
    results = []
    for rid, info in ROAD_SEGMENTS.items():
        if state and info.get("state") != state:
            continue
        if city and info.get("city") != city:
            continue
        r = {
            "id": rid,
            "name": info["name"],
            "lat": info["coords"][0],
            "lng": info["coords"][1],
            "state": info.get("state"),
            "city": info.get("city"),
            "road_material": info.get("material"),
            "last_repaired": info.get("last_repaired").isoformat()
        }
        results.append(r)
    return results

def compute_material_degradation(last_repaired_iso: str) -> float:
    """Return a degradation factor 0.1..1.0 given ISO last repaired date string."""
    try:
        last = datetime.fromisoformat(last_repaired_iso)
        years = max(0.0, (datetime.now() - last).days / 365.25)
        # scale: 0 years -> 0.1 ; 10+ years -> 1.0
        val = min(1.0, 0.1 + (years / 10.0) * 0.9)
        return round(val, 3)
    except Exception:
        return 0.5

def summarize_counts(zones: List[str]) -> Dict[str, int]:
    counts = {"Green": 0, "Yellow": 0, "Red": 0}
    for z in zones:
        if not z:
            continue
        zc = z.capitalize()
        if zc in counts:
            counts[zc] += 1
    return counts

# ---------------------------------------------------------------------------
# External API helpers (OpenWeather & TomTom). If keys are missing, return mocks.
# ---------------------------------------------------------------------------
def fetch_openweather(lat: float, lon: float) -> Dict[str, Any]:
    """Fetch current weather conditions for a point from OpenWeather; fallback to simulated."""
    if not OPENWEATHER_KEY:
        # Mock
        mock = {
            "temp": round(random.uniform(18, 36), 1),
            "humidity": random.randint(30, 95),
            "weather_main": random.choice(["Clear", "Clouds", "Rain"]),
            "weather_desc": random.choice(["clear sky", "scattered clouds", "light rain"]),
            "rain_1h": round(random.uniform(0, 15), 2)
        }
        logger.debug("OpenWeather mock: %s", mock)
        return mock

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}&units=metric"
        r = requests.get(url, timeout=6)
        r.raise_for_status()
        j = r.json()
        rain_1h = 0.0
        if isinstance(j.get("rain"), dict):
            rain_1h = float(j["rain"].get("1h", 0.0) or 0.0)
        out = {
            "temp": j["main"]["temp"],
            "humidity": j["main"]["humidity"],
            "weather_main": j["weather"][0]["main"],
            "weather_desc": j["weather"][0]["description"],
            "rain_1h": rain_1h
        }
        logger.debug("OpenWeather fetched: %s", out)
        return out
    except Exception as e:
        logger.warning("OpenWeather fetch failed: %s - returning mock", e)
        return {
            "temp": round(random.uniform(18, 36), 1),
            "humidity": random.randint(30, 95),
            "weather_main": "Clear",
            "weather_desc": "mocked",
            "rain_1h": 0.0
        }

def fetch_tomtom_flow(lat: float, lon: float) -> Dict[str, Any]:
    """
    Use TomTom Flow Segment API to retrieve currentSpeed & freeFlowSpeed.
    If TOMTOM_KEY is missing, return a plausible mock congestion value.
    Returns: { current_speed, free_flow_speed, congestion_score (0..1) }
    """
    if not TOMTOM_KEY:
        # Mock congestion derived randomly but biased by proximity to big cities (roughly)
        congestion = round(random.uniform(0.2, 0.95), 3)
        return {"current_speed": round(random.uniform(10, 60), 1), "free_flow_speed": round(random.uniform(60, 100), 1), "congestion": congestion, "source": "mock"}
    try:
        url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={lat},{lon}&unit=KMPH&key={TOMTOM_KEY}"
        r = requests.get(url, timeout=6)
        r.raise_for_status()
        j = r.json()
        fs = j.get("flowSegmentData", {})
        current = float(fs.get("currentSpeed") or 0.0)
        free = float(fs.get("freeFlowSpeed") or 0.0)
        congestion = 0.0
        if free > 0:
            congestion = max(0.0, min(1.0, 1.0 - (current / free)))
        return {"current_speed": current, "free_flow_speed": free, "congestion": round(congestion, 3), "source": "tomtom"}
    except Exception as e:
        logger.warning("TomTom Flow fetch failed: %s", e)
        return {"current_speed": round(random.uniform(10, 60), 1), "free_flow_speed": round(random.uniform(60, 100), 1), "congestion": round(random.uniform(0.2, 0.85), 3), "source": "error"}

def fetch_tomtom_incidents_bbox(min_lat: float, min_lon: float, max_lat: float, max_lon: float) -> List[Dict[str, Any]]:
    """
    Query TomTom incidents in bbox. If no key, return empty or mock.
    Use timeValidityFilter=present to get active incidents.
    """
    if not TOMTOM_KEY:
        # Possibly return rare mock incidents for demo
        if random.random() < 0.2:
            return [{"id": "mock-1", "type": "ACCIDENT", "description": "Mock accident"}]
        return []
    try:
        bbox = f"{min_lon},{min_lat},{max_lon},{max_lat}"
        # The TomTom incidents endpoint is flexible; request a concise fields response
        fields = "{incidents{type,geometry{type,coordinates},properties{iconCategory}}}"
        url = f"https://api.tomtom.com/traffic/services/5/incidentDetails?bbox={bbox}&timeValidityFilter=present&fields={fields}&key={TOMTOM_KEY}"
        r = requests.get(url, timeout=6)
        r.raise_for_status()
        j = r.json()
        inc = j.get("incidents") or []
        return inc
    except Exception as e:
        logger.warning("TomTom Incidents fetch failed: %s", e)
        return []

# ---------------------------------------------------------------------------
# Business logic: Risk scoring and classification
# ---------------------------------------------------------------------------
def compute_risk_score(traffic_congestion: float, rain_mm: float, material_degradation: float) -> Dict[str, Any]:
    """
    Weighted rule-based scoring model (interpretable).
    - traffic_congestion: 0..1
    - rain_mm: millimeters in last 1 hour (cap at 20 mm)
    - material_degradation: 0..1
    Returns dict: {zone, score, reason}
    """
    # Weights
    w_traffic = 0.45
    w_weather = 0.30
    w_material = 0.25

    t_score = float(traffic_congestion) * w_traffic
    rain_factor = min(20.0, float(rain_mm)) / 20.0  # map 0..20mm -> 0..1
    w_score = rain_factor * w_weather
    m_score = float(material_degradation) * w_material

    total = t_score + w_score + m_score
    total = max(0.0, min(1.0, total))

    if total >= 0.75:
        zone = "RED"
        reason = f"Critical: score={total:.2f}. High congestion and surface stress. Immediate action required."
    elif total >= 0.5:
        zone = "YELLOW"
        reason = f"High risk: score={total:.2f}. Schedule preventative maintenance."
    else:
        zone = "GREEN"
        reason = f"Normal: score={total:.2f}."

    return {"zone": zone, "score": round(total, 3), "reason": reason}

# ---------------------------------------------------------------------------
# Flask endpoints
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """
    Render the front-end index.html and inject Google Maps API key.
    The front-end expects endpoints like /api/locations, /api/roads, /api/aggregate, /api/get_current_status
    """
    return render_template("index.html", google_maps_key=GOOGLE_MAPS_KEY, carto_api_key=CARTO_API_KEY)

# --- Locations endpoint: serves states -> cities mapping ---
@app.route("/api/locations")
def api_locations():
    # Build mapping from ROAD_SEGMENTS (fast)
    mapping: Dict[str, List[str]] = {}
    for info in ROAD_SEGMENTS.values():
        st = info.get("state", "Unknown")
        ct = info.get("city", "Unknown")
        mapping.setdefault(st, set()).add(ct)
    # convert sets to sorted lists
    mapping_l = {k: sorted(list(v)) for k, v in mapping.items()}
    return jsonify(mapping_l)

# --- Roads endpoint: returns roads (with live traffic attached optionally) ---
@app.route("/api/roads")
def api_roads():
    state = request.args.get("state")
    city = request.args.get("city")
    attach_live = request.args.get("live", "true").lower() != "false"

    roads = safe_get_road_list(state, city)
    if attach_live:
        for r in roads:
            lat = r["lat"]; lng = r["lng"]
            weather = fetch_openweather(lat, lng)
            traffic = fetch_tomtom_flow(lat, lng)
            r["traffic"] = traffic
            r["weather"] = weather
            r["traffic_load"] = traffic.get("congestion", 0.0)
    return jsonify(roads)

# --- Aggregate endpoint: counts, avg traffic, oldest/newest repaired ---
@app.route("/api/aggregate")
def api_aggregate():
    state = request.args.get("state")
    city = request.args.get("city")
    roads = safe_get_road_list(state, city)

    zones = []
    traffic_vals = []
    oldest = None
    newest = None
    sample_roads = []

    for r in roads:
        # try to attach stored current zone if possible (use historical last known)
        # For demo, we will compute a proxy zone using last_repaired age & random
        degradation = compute_material_degradation(r["last_repaired"])
        # small proxy for zone: degrade->increase chance of yellow/red
        p = random.random() + degradation * 0.2
        zone = "Green"
        if p > 1.05:
            zone = "Red"
        elif p > 0.7:
            zone = "Yellow"
        zones.append(zone)
        # traffic simulated / fetched
        traffic = fetch_tomtom_flow(r["lat"], r["lng"])
        traffic_vals.append(traffic.get("congestion", 0.0))
        sample_roads.append({
            "id": r["id"], "name": r["name"], "lat": r["lat"], "lng": r["lng"], "zone": zone
        })
        # last repaired date parse
        try:
            d = datetime.fromisoformat(r["last_repaired"])
            if oldest is None or d < oldest:
                oldest = d
            if newest is None or d > newest:
                newest = d
        except Exception:
            pass

    avg_traffic = round(sum(traffic_vals) / len(traffic_vals), 3) if traffic_vals else None
    counts = summarize_counts(zones)
    return jsonify({
        "total_roads": len(sample_roads),
        "counts": counts,
        "avg_traffic_load": avg_traffic,
        "oldest_repaired_date": oldest.isoformat() if oldest else None,
        "newest_repaired_date": newest.isoformat() if newest else None,
        "sample_roads": sample_roads[:50]
    })

# --- Weather proxy: returns concise weather for a point ---
@app.route("/api/weather")
def api_weather():
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    if not lat or not lng:
        return jsonify({"error": "lat & lng required"}), 400
    try:
        lat_f = float(lat); lng_f = float(lng)
    except ValueError:
        return jsonify({"error": "lat & lng must be numeric"}), 400
    w = fetch_openweather(lat_f, lng_f)
    return jsonify(w)

# --- Traffic flow proxy for a single point ---
@app.route("/api/traffic_flow")
def api_traffic_flow():
    lat = request.args.get("lat"); lng = request.args.get("lng")
    if not lat or not lng:
        return jsonify({"error": "lat & lng required"}), 400
    try:
        lat_f = float(lat); lng_f = float(lng)
    except ValueError:
        return jsonify({"error": "lat & lng must be numeric"}), 400
    t = fetch_tomtom_flow(lat_f, lng_f)
    return jsonify(t)

# --- Traffic incidents proxy (bbox) ---
@app.route("/api/traffic_incidents")
def api_traffic_incidents():
    # Accept bbox params or center+radius
    min_lat = request.args.get("min_lat")
    min_lng = request.args.get("min_lng")
    max_lat = request.args.get("max_lat")
    max_lng = request.args.get("max_lng")
    radius = request.args.get("radius")  # radius in degrees ~ 0.01 ~= ~1km depending on lat
    if min_lat and min_lng and max_lat and max_lng:
        try:
            min_lat_f = float(min_lat); min_lng_f = float(min_lng)
            max_lat_f = float(max_lat); max_lng_f = float(max_lng)
        except ValueError:
            return jsonify({"error": "bbox params must be numeric"}), 400
        inc = fetch_tomtom_incidents_bbox(min_lat_f, min_lng_f, max_lat_f, max_lng_f)
        return jsonify({"incidents": inc})
    elif request.args.get("lat") and request.args.get("lng") and radius:
        try:
            lat_f = float(request.args.get("lat")); lng_f = float(request.args.get("lng"))
            rdeg = float(radius)
        except ValueError:
            return jsonify({"error": "lat,lng,radius must be numeric"}), 400
        min_lat_f = lat_f - rdeg; min_lng_f = lng_f - rdeg
        max_lat_f = lat_f + rdeg; max_lng_f = lng_f + rdeg
        inc = fetch_tomtom_incidents_bbox(min_lat_f, min_lng_f, max_lat_f, max_lng_f)
        return jsonify({"incidents": inc})
    else:
        return jsonify({"error": "Provide either bbox or lat+lng+radius"}), 400

# --- Core realtime status endpoint (combines data & runs classifier) ---
@app.route("/api/get_current_status")
def api_get_current_status():
    """
    Returns list of segments with:
        - traffic: flow data
        - weather: current weather
        - incidents: nearby incidents
        - computed material degradation & risk score
    Accepts optional ?state=...&city=...
    """
    state = request.args.get("state")
    city = request.args.get("city")
    only_bad = request.args.get("only_bad", "false").lower() == "true"
    result_segments = []
    total_traffic = 0.0
    total_segments = 0
    total_red = 0

    roads = safe_get_road_list(state, city)

    for r in roads:
        lat = r["lat"]; lng = r["lng"]
        # live fetches (with graceful fallback)
        weather = fetch_openweather(lat, lng)
        traffic = fetch_tomtom_flow(lat, lng)
        # small bbox for incidents (0.02 deg ~ ~2km)
        incs = fetch_tomtom_incidents_bbox(lat - 0.02, lng - 0.02, lat + 0.02, lng + 0.02)

        mat_deg = compute_material_degradation(r["last_repaired"])
        score = compute_risk_score(traffic_congestion=traffic.get("congestion", 0.0),
                                   rain_mm=weather.get("rain_1h", weather.get("rain_1h", 0.0)),
                                   material_degradation=mat_deg)

        entry = {
            "id": r["id"],
            "name": r["name"],
            "lat": lat,
            "lng": lng,
            "state": r.get("state"),
            "city": r.get("city"),
            "road_material": r.get("road_material"),
            "last_repaired": r.get("last_repaired"),
            "material_degradation": mat_deg,
            "traffic": traffic,
            "weather": weather,
            "incidents": incs,
            "risk": score
        }

        total_segments += 1
        total_traffic += traffic.get("congestion", 0.0)
        if score["zone"] == "RED":
            total_red += 1

        # filter if requested
        if only_bad:
            if score["zone"] == "RED" or (incs and len(incs) > 0):
                result_segments.append(entry)
        else:
            result_segments.append(entry)

    avg_traffic = round(total_traffic / total_segments, 3) if total_segments else None

    current_factors = {
        "total_segments": total_segments,
        "total_red_zones": total_red,
        "avg_traffic_load": avg_traffic,
        "oldest_repair_date": min((datetime.fromisoformat(r["last_repaired"]) for r in roads), default=None).isoformat() if roads else None,
        "newest_repair_date": max((datetime.fromisoformat(r["last_repaired"]) for r in roads), default=None).isoformat() if roads else None
    }

    return jsonify({"segments": result_segments, "current_factors": current_factors})

# --- Return only bad roads quickly ---
@app.route("/api/bad_roads")
def api_bad_roads():
    state = request.args.get("state")
    city = request.args.get("city")
    resp = api_get_current_status()
    # resp is a Flask Response object; get the JSON
    try:
        data = resp.get_json()
    except Exception:
        # fallback: call logic directly
        data = api_get_current_status().get_json()
    segs = data.get("segments", [])
    bad = [s for s in segs if s.get("risk", {}).get("zone") == "RED" or (s.get("incidents") and len(s.get("incidents")) > 0)]
    return jsonify(bad)

# --- Classifier endpoint (accepts JSON) ---
@app.route("/api/classify", methods=["POST"])
def api_classify():
    """
    Expects JSON payload with fields:
        traffic_load (0..1), road_material, weather_condition (string), last_repaired (ISO)
    Returns: {zone, score, reason}
    """
    j = request.json or {}
    try:
        traffic_load = float(j.get("traffic_load", 0.5))
    except Exception:
        traffic_load = 0.5
    road_material = j.get("road_material", "Asphalt")
    weather_condition = j.get("weather_condition", "").lower()
    last_repaired_iso = j.get("last_repaired")
    mat_deg = compute_material_degradation(last_repaired_iso) if last_repaired_iso else 0.5
    rain_mm = 0.0
    # infer rain from weather_condition if provided
    if "rain" in weather_condition:
        rain_mm = 8.0
    elif "storm" in weather_condition or "heavy" in weather_condition:
        rain_mm = 15.0

    out = compute_risk_score(traffic_congestion=traffic_load, rain_mm=rain_mm, material_degradation=mat_deg)
    return jsonify(out)

# --- Report generation (Excel) ---
@app.route("/report/generate", methods=["POST"])
def report_generate():
    """
    Generate an Excel report covering a date range and (optional) area filter.
    POST JSON:
        { startDate: "YYYY-MM-DD", endDate: "YYYY-MM-DD", area: "Maharashtra" }
    """
    if pd is None:
        return jsonify({"error": "Pandas is required to generate Excel reports. Install pandas and openpyxl."}), 500

    j = request.json or {}
    start = j.get("startDate")
    end = j.get("endDate")
    area = j.get("area", "ALL")

    if not start or not end:
        return jsonify({"error": "startDate and endDate are required (YYYY-MM-DD)"}), 400

    try:
        start_d = datetime.strptime(start, "%Y-%m-%d").date()
        end_d = datetime.strptime(end, "%Y-%m-%d").date()
    except Exception:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    # Build report rows by analyzing HISTORICAL_DATA between dates
    rows = []
    for rid, info in ROAD_SEGMENTS.items():
        if area != "ALL" and info.get("state") != area and info.get("city") != area:
            # support filtering by state or city named as area
            continue
        # determine max zone in period
        max_zone = "GREEN"
        transitions = []
        for dstr, per_day in HISTORICAL_DATA.items():
            try:
                d = datetime.strptime(dstr, "%Y-%m-%d").date()
            except Exception:
                continue
            if not (start_d <= d <= end_d):
                continue
            entry = per_day.get(rid)
            if not entry:
                continue
            z = entry.get("zone", "GREEN")
            transitions.append(f"{dstr}:{z}")
            if z == "RED":
                max_zone = "RED"
            elif z == "YELLOW" and max_zone != "RED":
                max_zone = "YELLOW"
        # causal mapping
        causal = ""
        if max_zone == "RED":
            causal = CAUSAL_MAPPING.get("RED", {}).get(rid, "Structural study recommended.")
        elif max_zone == "YELLOW":
            causal = CAUSAL_MAPPING.get("YELLOW", {}).get(rid, "Surface/Drainage maintenance recommended.")
        rows.append({
            "Road ID": rid,
            "Road Name": info.get("name"),
            "Area": f"{info.get('state')} / {info.get('city')}",
            "Max Zone (Period)": max_zone,
            "Zone Transitions": "; ".join(transitions) or "No data",
            "Causal Factor (AI)": causal,
            "Recommended Action": "Immediate Repair" if max_zone == "RED" else ("Preventive Maintenance" if max_zone == "YELLOW" else "Routine Check"),
            "Last Repaired": info.get("last_repaired").strftime("%Y-%m-%d")
        })

    df = pd.DataFrame(rows)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="RoadSense_Report", index=False)
        # summary sheet
        summary = {
            "Metric": ["Report Period", "Area Filter", "Total Roads", "Red Zones"],
            "Value": [f"{start} to {end}", area, len(df), len(df[df["Max Zone (Period)"] == "RED"])]
        }
        pd.DataFrame(summary).to_excel(writer, sheet_name="Summary", index=False)
    output.seek(0)
    filename = f"RoadSense_Report_{start}_to_{end}.xlsx"
    return send_file(output, as_attachment=True, download_name=filename, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ---------------------------------------------------------------------------
# Startup hook: log configuration and health-check endpoint
# ---------------------------------------------------------------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat() + "Z"})

if __name__ == "__main__":
    logger.info("Starting RoadSense backend - GoogleKeyProvided=%s OpenWeather=%s TomTom=%s", bool(GOOGLE_MAPS_KEY), bool(OPENWEATHER_KEY), bool(TOMTOM_KEY))
    # Run dev server
    app.run(host="0.0.0.0", port=5000, debug=True)
