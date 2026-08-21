import os
import pandas as pd

def analyze_surface(csv_path):
    df = pd.read_csv(csv_path)

    avg_vibration = float(df["vibration"].mean())   # ensure JSON safe
    avg_speed = float(df["speed"].mean())

    return {
        "file": os.path.basename(csv_path),
        "avg_vibration": avg_vibration,
        "avg_speed": avg_speed,
        "status": "Rough" if avg_vibration > 5 else "Smooth"
    }
