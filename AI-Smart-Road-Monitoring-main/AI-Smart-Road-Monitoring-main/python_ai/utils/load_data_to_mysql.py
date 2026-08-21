import json
import csv
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="ai_smart_road_monitoring_system_application"
)
cur = conn.cursor()

# ---------- ROADS ----------
with open("../data/road_data.json") as f:
    roads = json.load(f)

for r in roads:
    cur.execute("""
        INSERT INTO roads (road_name, district, state, latitude, longitude)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        r["road_name"], r["district"], r["state"],
        r["latitude"], r["longitude"]
    ))

# ---------- POTHOLES ----------
with open("../data/potholes_data.json") as f:
    potholes = json.load(f)

for p in potholes:
    cur.execute("""
        INSERT INTO potholes
        (road_id, gps_location, latitude, longitude, length, width, depth, severity, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        p["road_id"], p["gps_location"], p["latitude"], p["longitude"],
        p["length"], p["width"], p["depth"], p["severity"], p["status"]
    ))

conn.commit()
cur.close()
conn.close()

print("✅ Data loaded successfully")
