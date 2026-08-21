import os
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

print("\n==========================================")
print("   Creating NEW Dummy Pothole Model")
print("==========================================\n")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PKL = os.path.join(BASE_DIR, "pothole_model.pkl")
MODEL_JOBLIB = os.path.join(BASE_DIR, "pothole_model.joblib")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")

# Dummy training data
X = np.array([
    [0.2, 0.1, 0.3],
    [0.8, 0.6, 0.7],
    [0.4, 0.5, 0.3],
    [0.9, 0.8, 0.9]
])

y = np.array([0, 1, 0, 1])  # 0 = no pothole, 1 = pothole

# Scale data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Simple model
model = LogisticRegression()
model.fit(X_scaled, y)

# Save model files
joblib.dump(model, MODEL_PKL)
joblib.dump(model, MODEL_JOBLIB)
joblib.dump(scaler, SCALER_PATH)

print(f"✔ Model saved: {MODEL_PKL}")
print(f"✔ Model saved: {MODEL_JOBLIB}")
print(f"✔ Scaler saved: {SCALER_PATH}")

print("\n🎉 Dummy pothole model created successfully!\n")
