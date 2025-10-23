# ai_model.py
import joblib
import numpy as np
from datetime import datetime

model = joblib.load('traffic_model.pkl')

def predict_congestion(distance, duration):
    """Predict congestion level using distance, duration, and current hour."""
    hour = datetime.now().hour
    features = np.array([[distance, duration, hour]])
    prediction = model.predict(features)[0]
    return prediction
