"""
verify_project_integrity.py
Automatic repair tool for:
E:\Project-Sakshi\ai_smart_road_monitoring_system_application
"""

import os
import json
import importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))
PYTHON_AI = os.path.join(BASE, "python_ai")

REQUIRED_FOLDERS = {
    "uploads/images": [],
    "uploads/sensor": [],
    "logs": [],
    "models": ["pothole_model.joblib", "pothole_model.pkl", "scaler.pkl"],
    "data": [
        "dashboard_data.json",
        "dummy_image_list.json",
        "dummy_pothole_data.json",
        "dummy_sensor_stream.json",
        "dummy_surface_data.csv",
        "gps_sample_data.json",
        "potholes_data.json",
        "road_data.json",
        "sample_sensor.csv",
    ],
}


def check_folder(path):
    full = os.path.join(PYTHON_AI, path)
    return os.path.exists(full)


def check_file(path):
    full = os.path.join(PYTHON_AI, path)
    return os.path.exists(full)


def auto_fix_folder(path):
    full = os.path.join(PYTHON_AI, path)
    os.makedirs(full, exist_ok=True)
    print(f"[FIXED] Created missing folder → {path}")


def auto_fix_json(path):
    full = os.path.join(PYTHON_AI, "data", path)
    print(f"[FIXED] Creating missing JSON → {path}")
    with open(full, "w") as f:
        json.dump([], f, indent=4)


def auto_fix_csv(path):
    full = os.path.join(PYTHON_AI, "data", path)
    print(f"[FIXED] Creating missing CSV → {path}")
    with open(full, "w") as f:
        f.write("timestamp,value\n")


def verify_model_files():
    model_path = os.path.join(PYTHON_AI, "models")
    missing = False

    for model in REQUIRED_FOLDERS["models"]:
        full = os.path.join(model_path, model)
        if not os.path.exists(full):
            print(f"[WARNING] Missing model: {model}")
            missing = True

    if not missing:
        print("[OK] All model files exist ✓")


def verify_python_imports():
    required_modules = [
        "pothole_detection",
        "road_surface_analysis",
        "utils.image_processing",
        "utils.sensor_data_parser",
        "utils.gps_module",
    ]

    print("\n▶ Checking Python import modules...\n")

    for module in required_modules:
        module_path = os.path.join(PYTHON_AI, module.replace(".", "/") + ".py")

        if not os.path.exists(module_path):
            print(f"[ERROR] Missing required module → {module}")
        else:
            print(f"[OK] Module available: {module}")


def main():
    print("\n============================================")
    print("   SMART ROAD — PROJECT INTEGRITY CHECK")
    print("============================================\n")

    # -------------------------
    # Check and repair folders
    # -------------------------
    for folder, files in REQUIRED_FOLDERS.items():
        if not check_folder(folder):
            auto_fix_folder(folder)
        else:
            print(f"[OK] Folder exists: {folder}")

        # Check inside files
        for file in files:
            file_path = os.path.join(folder, file)
            if not check_file(file_path):
                # Auto-repair JSON/CSV
                if file.endswith(".json"):
                    auto_fix_json(file)
                elif file.endswith(".csv"):
                    auto_fix_csv(file)
            else:
                print(f"[OK] File exists: {file}")

    # -------------------------
    # Verify models
    # -------------------------
    print("\n▶ Checking model files...\n")
    verify_model_files()

    # -------------------------
    # Verify Python imports
    # -------------------------
    verify_python_imports()

    print("\n============================================")
    print(" Integrity Check & Auto-Repair Complete ✓")
    print("============================================\n")


if __name__ == "__main__":
    main()
