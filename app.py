from flask import Flask, request, jsonify, render_template
from models import db, FavoriteLocation
from weather_service import OpenWeatherService,API_KEY
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db.init_app(app)

weather_service = OpenWeatherService()

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/weather', methods=['GET'])
def get_weather():
    city = request.args.get("city")

    if not city or not city.strip():
        return jsonify({"error": "City name cann't be empty."}), 400

    weather_data = weather_service.get_weather_data(city)

    if "error" in weather_data:
        return jsonify({"error": weather_data["error"]}), 400
    

    #Fetching main weather Data

    response= requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric").json()

    if response.get("cod") != 200:
        return jsonify({"error": "Failed to fetch weather data"}), 400

    
    forecast_data = []
    for entry in weather_data.get("list", [])[:5]:  
        forecast_data.append({
            "date": entry["dt_txt"],
            "temp": entry["main"]["temp"],
            "weather": entry["weather"][0]["description"],
            "icon": entry["weather"][0]["icon"]
        })

    return jsonify({
        "city": response["name"],
        "temperature": response["main"]["temp"],
        "weather": response["weather"][0]["description"],
        "icon": response["weather"][0]["icon"],
        "lat": response["coord"]["lat"],
        "lon": response["coord"]["lon"],
        "forecast": forecast_data  # Send 5-day forecast to frontend
    })



@app.route('/favorites', methods=['POST'])
def add_favorite():
    city = request.json.get('city')
    if not city:
        return jsonify({"error": "City is required"}), 400
    
    if FavoriteLocation.query.filter_by(city=city).first():
        return jsonify({"error": "City already in favorites"}), 400
    
    new_fav = FavoriteLocation(city=city)
    db.session.add(new_fav)
    db.session.commit()
    
    return jsonify({"message": "added to Favorites"}), 201



@app.route('/favorites', methods=['GET'])
def get_favorites():
    favorites = FavoriteLocation.query.all()
    return jsonify([fav.city for fav in favorites])



@app.route("/alerts", methods=["GET"])
def get_alerts():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City is required"}), 400

    alert_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(alert_url)
    
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch alerts"}), response.status_code
    
    data = response.json()
    alerts = data.get("weather", [])

    return jsonify({"alerts": alerts, "city": city})




@app.route('/favorites', methods=['DELETE'])
def delete_favorite():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City is required"}), 400

    favorite = FavoriteLocation.query.filter_by(city=city).first()
    if not favorite:
        return jsonify({"error": "City not found in favorites"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Favorite location deleted"}), 200




@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404



@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)



