"""
create_restructure.py
Final stable version — validated for:
E:\Project-Sakshi\ai_smart_road_monitoring_system_application
"""

import os
import json
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))

PYTHON_AI = os.path.join(BASE, "python_ai")

REQUIRED_FOLDERS = [
    os.path.join(PYTHON_AI, "uploads"),
    os.path.join(PYTHON_AI, "uploads", "images"),
    os.path.join(PYTHON_AI, "uploads", "sensor"),
    os.path.join(PYTHON_AI, "logs"),
    os.path.join(PYTHON_AI, "models"),
    os.path.join(PYTHON_AI, "analysis"),
    os.path.join(PYTHON_AI, "test_samples"),
    os.path.join(PYTHON_AI, "data"),
]

SAFE_DATASET_FOLDERS = [
    "ai_dummy_dataset",
    "ai_dummy_dataset_large",
    "dummy_data_files",
]

JSON_TEMPLATES = {
    "dashboard_data.json": [],
    "dummy_image_list.json": [],
    "dummy_pothole_data.json": [],
    "dummy_sensor_stream.json": [],
    "dummy_surface_data.csv": "",
    "gps_sample_data.json": [],
    "potholes_data.json": [],
    "road_data.json": [],
    "sample_sensor.csv": "timestamp,value\n"
}


def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"[CREATE] {path}")
    else:
        print(f"[OK] Folder exists: {path}")


def ensure_json_files():
    data_path = os.path.join(PYTHON_AI, "data")
    for filename, default_content in JSON_TEMPLATES.items():
        file_path = os.path.join(data_path, filename)

        if not os.path.exists(file_path):
            print(f"[CREATE] Missing data file → {filename}")
            if filename.endswith(".json"):
                with open(file_path, "w") as f:
                    json.dump(default_content, f, indent=4)
            else:
                with open(file_path, "w") as f:
                    f.write(default_content)
        else:
            print(f"[OK] Data file exists: {filename}")


def clean_empty_folders():
    """Remove empty folders except dataset folders"""
    for root, dirs, files in os.walk(BASE, topdown=False):
        for d in dirs:
            full_path = os.path.join(root, d)

            # Never delete dataset folders
            if any(ds in full_path for ds in SAFE_DATASET_FOLDERS):
                continue

            if os.path.isdir(full_path) and not os.listdir(full_path):
                print(f"[REMOVE] Empty folder removed: {full_path}")
                os.rmdir(full_path)


def main():
    print("\n============================================")
    print("   SMART ROAD — PROJECT RESTRUCTURE TOOL")
    print("============================================")

    print("\n▶ Ensuring required python_ai folders...\n")
    for folder in REQUIRED_FOLDERS:
        ensure_folder(folder)

    print("\n▶ Ensuring json/csv files in python_ai/data ...\n")
    ensure_json_files()

    print("\n▶ Cleaning empty unused folders...\n")
    clean_empty_folders()

    print("\n============================================")
    print(" Restructure Complete ✓")
    print("============================================\n")


if __name__ == "__main__":
    main()
