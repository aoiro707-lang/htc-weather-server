from flask import Flask, request, jsonify, Response
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

API_KEY = "0c60b2b833632e5c653f6c29dada5dfa"

# Map OpenWeather -> HTC Weather
def map_weather_condition(owm_main, owm_desc):
    mapping = {
        "Clear": "Sunny",
        "Clouds": {
            "few clouds": "Partly Cloudy",
            "scattered clouds": "Partly Cloudy",
            "broken clouds": "Mostly Cloudy",
            "overcast clouds": "Cloudy"
        },
        "Rain": {
            "light rain": "Showers",
            "moderate rain": "Rain",
            "heavy intensity rain": "Heavy Rain"
        },
        "Thunderstorm": "Thunderstorms",
        "Snow": {
            "light snow": "Flurries",
            "snow": "Snow",
            "heavy snow": "Heavy Snow"
        },
        "Drizzle": "Showers",
        "Mist": "Fog",
        "Fog": "Fog",
        "Haze": "Hazy"
    }

    if owm_main in mapping:
        if isinstance(mapping[owm_main], dict):
            return mapping[owm_main].get(owm_desc, owm_main)
        else:
            return mapping[owm_main]

    return owm_main  # fallback nếu chưa map


@app.route("/getstaticweather")
def get_static_weather():
    locCode = request.args.get("locCode", "Hanoi")
    lat, lon = "21.0285", "105.8542"  # test: Hà Nội

    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    data = requests.get(url).json()

    owm_main = data["weather"][0]["main"]
    owm_desc = data["weather"][0]["description"]

    mapped_weather = map_weather_condition(owm_main, owm_desc)

    temp = round(data["main"]["temp"])
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    location = data["name"]

    # --- XML format giống HTC ---
    root = ET.Element("weather")
    ET.SubElement(root, "location").text = location
    ET.SubElement(root, "temperature").text = str(temp)
    ET.SubElement(root, "humidity").text = str(humidity)
    ET.SubElement(root, "wind_speed").text = str(wind_speed)
    ET.SubElement(root, "condition").text = mapped_weather

    xml_data = ET.tostring(root, encoding="utf-8", method="xml")
    return Response(xml_data, mimetype="application/xml")


@app.route("/getstaticweather_json")
def get_static_weather_json():
    # endpoint JSON để debug
    locCode = request.args.get("locCode", "Hanoi")
    lat, lon = "21.0285", "105.8542"

    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    data = requests.get(url).json()

    owm_main = data["weather"][0]["main"]
    owm_desc = data["weather"][0]["description"]

    mapped_weather = map_weather_condition(owm_main, owm_desc)

    response = {
        "location": data["name"],
        "temperature": round(data["main"]["temp"]),
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "weather": mapped_weather
    }

    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
