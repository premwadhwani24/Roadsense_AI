# dashboard/app.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import cv2
import time
import json
from datetime import datetime
from deep_translator import GoogleTranslator
from models.traffic_ai import get_signal_timing
from mock_data.simulator import is_emergency_vehicle
from detector.detector import detect_vehicles_in_frame, detect_vehicles_by_zone  # ← FIXED IMPORT

# --- PAGE CONFIG ---
st.set_page_config(page_title="🚦 TrafficFlow AI - AIoT Hackathon", layout="wide")
st.title("🚦 Smart Traffic Signal Control for Indian Roads")

# --- LANGUAGE ---
lang = st.sidebar.selectbox("Select Language", ["English", "Hindi", "Tamil"])

# --- INPUT SOURCE SELECTOR ---
input_source = st.sidebar.radio(
    "Select Input Source",
    ["Video File", "Live Webcam"]
)

def translate_text(text, target_lang):
    if target_lang == "English":
        return text
    try:
        lang_code = {"Hindi": "hi", "Tamil": "ta"}.get(target_lang, "en")
        return GoogleTranslator(source='en', target=lang_code).translate(text)
    except Exception as e:
        return text

# --- VIDEO SETUP ---
if input_source == "Video File":
    video_path = "E:\\TrafficFlow_AI\\data\\intersection.mp4"
    cap = cv2.VideoCapture(video_path)
else:  # Live Webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.warning("⚠️ Webcam not found. Switching to demo video...")
        input_source = "Video File"
        video_path = "E:\\TrafficFlow_AI\\data\\intersection.mp4"
        cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    st.error("❌ Could not open video/webcam. Check path or connection.")
    st.stop()

# --- LOGGING SETUP ---
LOG_FILE = "../data/traffic_log.json"
os.makedirs("../data", exist_ok=True)

# --- DASHBOARD PLACEHOLDER ---
placeholder = st.empty()

frame_skip = 5
frame_count = 0

# --- MAIN LOOP ---
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % frame_skip != 0:
        continue  # Skip this frame

    # 🚗 REAL VEHICLE DETECTION (NOT RANDOM!)
    zone_counts = detect_vehicles_by_zone(frame)
    ns_count = zone_counts["left"] + zone_counts["right"]  # vertical lanes
    ew_count = zone_counts["center"]                        # horizontal lane
    total_vehicles = ns_count + ew_count

    # 🚑 EMERGENCY SIMULATION (Can upgrade to visual detection later)
    emergency = is_emergency_vehicle()

    # 🧠 AI DECISION (Lane-aware, India-trained)
    signal_plan = get_signal_timing(ns_count, ew_count, emergency)

    # 📊 LOG DATA
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ns_vehicles": ns_count,
        "ew_vehicles": ew_count,
        "total_vehicles": total_vehicles,
        "green_ns": signal_plan["green_ns"],
        "green_ew": signal_plan["green_ew"],
        "mode": signal_plan["mode"],
        "emergency": emergency,
        "wait_saved_sec": signal_plan["wait_saved"]
    }

    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        st.warning(f"⚠️ Log write failed: {e}")

    # 🖥️ UPDATE DASHBOARD
    with placeholder.container():
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(translate_text("🚦 Real-Time Signal Control", lang))
            st.metric(translate_text("Mode", lang), translate_text(signal_plan["mode"], lang))
            st.write(translate_text(f"🟢 North-South Green: {signal_plan['green_ns']} sec", lang))
            st.write(translate_text(f"🟢 East-West Green: {signal_plan['green_ew']} sec", lang))
            st.write(translate_text(f"🚗 Total Vehicles: {total_vehicles}", lang))
            st.write(translate_text(f"⬅️ Left Lane: {zone_counts['left']}", lang))
            st.write(translate_text(f"⏺️ Center Lane: {zone_counts['center']}", lang))
            st.write(translate_text(f"➡️ Right Lane: {zone_counts['right']}", lang))
            if emergency:
                st.warning(translate_text("🚑 EMERGENCY VEHICLE DETECTED — GREEN WAVE ACTIVATED", lang))
            st.success(translate_text(f"⏱️ Estimated Wait Time Saved: {signal_plan['wait_saved']} sec", lang))

        with col2:
            st.subheader(translate_text("📹 Live Feed", lang))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            st.image(frame_rgb, use_column_width=True)

        st.markdown("---")

    time.sleep(2)

# --- END ---
cap.release()
st.success(translate_text("✅ Simulation Complete — Ready for Deployment Across India!", lang))