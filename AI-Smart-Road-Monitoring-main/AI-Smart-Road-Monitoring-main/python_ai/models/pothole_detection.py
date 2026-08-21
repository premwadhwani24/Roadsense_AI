import os
import joblib
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models_store")
MODEL_PATH = os.path.join(MODEL_DIR, "pothole_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")

def load_model():
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    return model, scaler

model, scaler = load_model()


def predict_pothole(image_path):
    """
    Dummy prediction that ALWAYS returns a valid JSON-safe structure
    """
    prediction_value = float(np.random.random())  # <--- JSON safe float
    severity = "Low"
    if prediction_value > 0.66:
        severity = "High"
    elif prediction_value > 0.33:
        severity = "Medium"

    return {
        "image": os.path.basename(image_path),
        "pothole_score": prediction_value,
        "severity": severity
    }
