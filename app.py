from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import requests, os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key in production

# SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movesmart.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Mapbox API configuration
MAPBOX_API_KEY = os.getenv('MAPBOX_API_KEY')
if not MAPBOX_API_KEY:
    raise ValueError("No Mapbox API key found. Set the MAPBOX_API_KEY environment variable.")
MAPBOX_DIRECTIONS_URL = "https://api.mapbox.com/directions/v5/mapbox/driving"
MAPBOX_GEOCODING_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"

# User model for authentication
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Plain text for demo; hash in production!

# Route model for storing routes
class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_location = db.Column(db.String(200), nullable=False)
    end_location = db.Column(db.String(200), nullable=False)
    distance = db.Column(db.Float)         # in kilometers
    duration = db.Column(db.Float)         # in minutes
    congestion_level = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

with app.app_context():
    db.create_all()

    
# Geocode a location name to using Mapbox Geocoding API.
def geocode_location(location):
    url = f"{MAPBOX_GEOCODING_URL}/{requests.utils.quote(location)}.json"
    params = {
        "access_token": MAPBOX_API_KEY,
        "limit": 1
    }
    response = requests.get(url, params=params)
    data = response.json()
    try:
        return data["features"][0]["center"]  # [longitude, latitude]
    except (IndexError, KeyError):
        return None

# Get route data from Mapbox Directions API.
def get_real_time_traffic_data(start_location, end_location):
    start_coords = geocode_location(start_location)
    end_coords = geocode_location(end_location)
    if not start_coords or not end_coords:
        flash("One or both locations could not be geocoded. Please check your input.", "danger")
        return None, None, "Unknown"
    waypoints = f"{start_coords[0]},{start_coords[1]};{end_coords[0]},{end_coords[1]}"
    params = {
        "access_token": MAPBOX_API_KEY,
        "geometries": "geojson",
        "overview": "full"
    }
    url = f"{MAPBOX_DIRECTIONS_URL}/{waypoints}"
    response = requests.get(url, params=params)
    data = response.json()
    if 'routes' in data and data['routes']:
        route = data['routes'][0]
        distance = route['distance'] / 1000  # meters to km
        duration = route['duration'] / 60    # seconds to minutes
        congestion_level = "High" if duration / distance > 2 else "Moderate" if duration / distance > 1 else "Low"
        return round(distance, 2), round(duration, 2), congestion_level
    else:
        flash("Could not retrieve route details from Mapbox.", "danger")
        return None, None, "Unknown"


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose another.", "danger")
            return redirect(url_for('signup'))
        new_user = User(username=username, password=password)  # Hash the password in production!
        db.session.add(new_user)
        db.session.commit()
        flash("Sign up successful! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()  # Use secure password checking in production!
        if user:
            session['user'] = user.username
            flash("Logged in successfully.", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials. Please try again.", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))

# Home route — displays saved routes.
@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    routes = Route.query.order_by(Route.timestamp.desc()).all()
    return render_template('index.html', routes=routes)

# Add new route based on place names.
@app.route('/add_route', methods=['POST'])
def add_route():
    if 'user' not in session:
        return redirect(url_for('login'))
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
        flash("Route added successfully.", "success")
    return redirect(url_for('home'))

# Delete a route.
@app.route('/delete_route/<int:route_id>', methods=['POST'])
def delete_route(route_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    route = Route.query.get(route_id)
    if route:
        db.session.delete(route)
        db.session.commit()
        flash("Route deleted successfully.", "success")
    else:
        flash("Route not found.", "danger")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
