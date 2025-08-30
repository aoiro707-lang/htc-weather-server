from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# API key OpenWeatherMap
API_KEY = "0c60b2b833632e5c653f6c29dada5dfa"

@app.route("/")
def home():
    return "✅ HTC Weather Server is running!"

@app.route("/getstaticweather")
def get_static_weather():
    loc_code = request.args.get("locCode", "HANOI")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={loc_code}&appid={API_KEY}&units=metric"
    resp = requests.get(url)

    if resp.status_code == 200:
        data = resp.json()
        result = {
            "location": data.get("name", loc_code),
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }
        return jsonify(result)
    else:
        return jsonify({"error": "Failed to fetch weather"}), 500

@app.route("/getweather")
def get_weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        return jsonify({"error": "Missing lat/lon"}), 400

    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    resp = requests.get(url)

    if resp.status_code == 200:
        data = resp.json()
        result = {
            "location": data.get("name", f"{lat},{lon}"),
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }
        return jsonify(result)
    else:
        return jsonify({"error": "Failed to fetch weather"}), 500
