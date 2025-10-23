# create_model.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# Dummy training data
data = {
    'distance': [1, 3, 5, 7, 10, 2, 8, 4, 6],
    'duration': [3, 10, 18, 25, 40, 6, 30, 15, 20],
    'hour': [8, 9, 18, 19, 12, 22, 17, 8, 10],
    'congestion': ['Low', 'High', 'High', 'High', 'Moderate', 'Low', 'High', 'Moderate', 'Moderate']
}

df = pd.DataFrame(data)

X = df[['distance', 'duration', 'hour']]
y = df['congestion']

model = RandomForestClassifier()
model.fit(X, y)

# Save the trained model
joblib.dump(model, 'traffic_model.pkl')
print("✅ Model trained and saved as traffic_model.pkl")
