import os
import sys
import subprocess

print("\n==========================================")
print("     AUTO REPAIR MODEL SYSTEM (FINAL)")
print("==========================================\n")

# -------------------------------------------------
# Determine correct python_ai root
# -------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))    # python_ai/
MODELS_STORE = os.path.join(CURRENT_DIR, "models_store")

REPAIR_SCRIPT = os.path.join(MODELS_STORE, "repair_model.py")
CREATE_DUMMY_SCRIPT = os.path.join(MODELS_STORE, "create_new_dummy_model.py")

print("📁 Working directory:", CURRENT_DIR)
print("📁 models_store:", MODELS_STORE)


def scan_models():
    """Returns list of model files inside models_store."""
    print("\n🔍 Scanning model files...\n")

    if not os.path.exists(MODELS_STORE):
        print("❌ ERROR: models_store folder does not exist.")
        return []

    files = []
    for f in os.listdir(MODELS_STORE):
        if f.endswith(".pkl") or f.endswith(".joblib"):
            files.append(f)
            print("✔ Found model:", f)

    if not files:
        print("⚠ No models found in models_store.")

    return files


def run_python(script_path):
    """Runs a python script safely."""
    if not os.path.exists(script_path):
        print(f"❌ ERROR: Script not found → {script_path}")
        return

    print(f"\n🚀 Running → {os.path.basename(script_path)}")
    subprocess.run([sys.executable, script_path], shell=True)


def start_repair():
    models = scan_models()

    # -------------------------------------------------
    # Case 1: No model files → Generate new model
    # -------------------------------------------------
    if not models:
        print("\n➡ No models found. Creating NEW model...")
        run_python(CREATE_DUMMY_SCRIPT)
        print("\n🎉 New dummy model created successfully!")
        return

    # -------------------------------------------------
    # Case 2: Try repairing existing model
    # -------------------------------------------------
    print("\n🔧 Attempting model repair...")
    run_python(REPAIR_SCRIPT)

    print("\n🎉 Model repair complete!")


if __name__ == "__main__":
    start_repair()
