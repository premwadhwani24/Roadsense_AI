# RoadSense — Road Condition Classifier (Flask + Keras)

## What's included
- `app.py` — Flask app that serves the frontend and '/predict' endpoint.
- `train.py` — Training script (Keras) that saves `road_condition_classifier.h5` after training.
- `templates/index.html`, `static/style.css`, `static/app.js` — frontend files.
- `requirements.txt` — dependencies.

## Quick start
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
2. (Optional) Train a model using `train.py` (place dataset in `dataset/train` and `dataset/val`):
   ```bash
   python train.py
   ```
   This creates `road_condition_classifier.h5` in the project root.
3. Run Flask:
   ```bash
   python app.py
   ```
   Open http://localhost:5000 in your browser.

## Notes
- If TensorFlow is not installed or `road_condition_classifier.h5` is not present, the `/predict` endpoint returns a random stub result and a note telling you to add the model.
- The frontend is minimal and intended as a starting point for integration into your dashboard.
