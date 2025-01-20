from flask import Flask, request, jsonify
import requests
import math

app = Flask(__name__)

# Replace with your API keys
OPENWEATHER_API_KEY = "your_openweather_api_key"
GOOGLE_PLACES_API_KEY = "your_google_places_api_key"

def get_weather(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=imperial"
    response = requests.get(url).json()
    return response

def get_places(lat, lon, radius, activity_type):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius={radius}&type={activity_type}&key={GOOGLE_PLACES_API_KEY}"
    response = requests.get(url).json()
    return response.get("results", [])

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    lat = data.get("latitude")
    lon = data.get("longitude")
    preferences = data.get("preferences", [])  # e.g., ["hike", "museum", "park"]
    
    # Get current weather
    weather = get_weather(lat, lon)
    weather_condition = weather["weather"][0]["main"].lower()
    
    # Filter activity types based on weather
    if weather_condition in ["rain", "snow", "thunderstorm"]:
        preferences = [pref for pref in preferences if pref not in ["hike", "park"]]
    elif weather_condition in ["clear", "clouds"]:
        preferences = [pref for pref in preferences if pref not in ["indoor"]]
    
    # Fetch places based on preferences
    recommendations = []
    for activity_type in preferences:
        places = get_places(lat, lon, 40000, activity_type)  # 40 miles in meters
        for place in places[:3]:  # Limit to 3 recommendations
            recommendations.append({
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "type": activity_type
            })
    
    # Limit total recommendations to 3
    recommendations = recommendations[:3]
    
    return jsonify({
        "weather": weather_condition,
        "recommendations": recommendations
    })

if __name__ == "__main__":
    app.run(debug=True)
