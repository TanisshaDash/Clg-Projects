from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

# SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movesmart.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Google Maps API Key (use your actual key)
GOOGLE_MAPS_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"
DISTANCE_MATRIX_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"

# Route model
class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_location = db.Column(db.String(200), nullable=False)
    end_location = db.Column(db.String(200), nullable=False)
    distance = db.Column(db.Float)
    duration = db.Column(db.Float)
    congestion_level = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# Initialize database
with app.app_context():
    db.create_all()

# Fetch real-time data from Google Maps
def get_real_time_traffic_data(start_location, end_location):
    params = {
        "origins": start_location,
        "destinations": end_location,
        "key": GOOGLE_MAPS_API_KEY
    }
    response = requests.get(DISTANCE_MATRIX_URL, params=params)
    data = response.json()

    if data['status'] == 'OK':
        elements = data['rows'][0]['elements'][0]
        if elements['status'] == 'OK':
            distance = elements['distance']['value'] / 1000  # meters to km
            duration = elements['duration']['value'] / 60  # seconds to minutes
            congestion_level = "High" if duration / distance > 3 else "Moderate" if duration / distance > 1.5 else "Low"
            return round(distance, 2), round(duration, 2), congestion_level
    return None, None, "Unknown"

# Home route
@app.route('/')
def home():
    routes = Route.query.all()
    return render_template('index.html', routes=routes)

# Add route and show results immediately
@app.route('/add_route', methods=['POST'])
def add_route():
    start_location = request.form['start_location']
    end_location = request.form['end_location']

    distance, duration, congestion_level = get_real_time_traffic_data(start_location, end_location)

    if distance is not None and duration is not None:
        new_route = Route(
            start_location=start_location,
            end_location=end_location,
            distance=distance,
            duration=duration,
            congestion_level=congestion_level
        )
        db.session.add(new_route)
        db.session.commit()

    return render_template('index.html', routes=Route.query.all(), result=(start_location, end_location, distance, duration, congestion_level))

if __name__ == '__main__':
    app.run(debug=True)
