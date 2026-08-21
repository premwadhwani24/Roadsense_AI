#!/usr/bin/env python3
import sys, json, random, time

def fake_analysis(image_path, sensor_json):
    # Pretend to analyze and return pothole info
    time.sleep(0.2)
    result = {
        "detected": True,
        "length_m": round(random.uniform(0.2, 1.5), 3),
        "width_m": round(random.uniform(0.2, 1.2), 3),
        "depth_m": round(random.uniform(0.02, 0.3), 3),
        "image": image_path,
        "gps": json.loads(sensor_json).get("gps", "0,0")
    }
    return result

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(json.dumps({"error":"need image_path and sensor_json"}))
        sys.exit(1)
    img = sys.argv[1]
    sensor = sys.argv[2]
    try:
        sensor_json = json.loads(sensor)
    except Exception:
        sensor_json = {"gps":"0,0"}
    out = fake_analysis(img, sensor_json)
    print(json.dumps(out))
