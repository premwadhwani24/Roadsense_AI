import os
import joblib
import pickle
import traceback
from create_new_dummy_model import MODEL_PKL, MODEL_JOBLIB, SCALER_PATH, model, scaler

print("\n==========================================")
print("         MODEL REPAIR TOOL")
print("==========================================\n")

def try_load(path):
    try:
        print(f"🔍 Trying joblib → {path}")
        return joblib.load(path)
    except:
        print("⚠ Joblib failed, trying pickle...")
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except:
            print("❌ Both loaders failed.")
            return None


def repair_model(path):
    print(f"\n🛠 Checking model: {path}")

    m = try_load(path)

    if m is None:
        print("❌ Model is corrupted → Replacing with new dummy model")
        joblib.dump(model, path)
    else:
        print("✔ Model OK")


if __name__ == "__main__":
    repair_model(MODEL_PKL)
    repair_model(MODEL_JOBLIB)

    # Ensure scaler exists
    if not os.path.exists(SCALER_PATH):
        print("\n⚠ Scaler missing → Recreating scaler")
        joblib.dump(scaler, SCALER_PATH)

    print("\n🎉 Model repair complete!\n")
