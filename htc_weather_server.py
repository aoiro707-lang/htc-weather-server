from flask import Flask, request, Response
import requests

app = Flask(__name__)

API_KEY = "0c60b2b833632e5c653f6c29dada5dfa"

# --- Map weather OWM -> HTC ---
def map_condition(cond):
    mapping = {
        "Clear": "Sunny",
        "Clouds": "Cloudy",
        "Rain": "Rain",
        "Drizzle": "Showers",
        "Thunderstorm": "Thunderstorms",
        "Snow": "Snow",
        "Mist": "Fog",
        "Fog": "Fog",
        "Haze": "Hazy"
    }
    return mapping.get(cond, "Cloudy")


# =========================
# 🌦 GET WEATHER (lat/lon)
# =========================
@app.route("/getweather")
def get_weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    url = "https://api.openweathermap.org/data/2.5/weather"
    r = requests.get(url, params={
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    })
    data = r.json()

    condition = map_condition(data["weather"][0]["main"])

    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<weatherdata>
  <weather location="{data['name']}"
           temperature="{round(data['main']['temp'])}"
           humidity="{data['main']['humidity']}"
           wind="{data['wind']['speed']}"
           condition="{condition}" />
</weatherdata>
"""
    return Response(xml, mimetype="application/xml")


# =========================
# 🌍 STATIC WEATHER (city)
# =========================
@app.route("/getstaticweather")
def get_static_weather():
    loc = request.args.get("locCode", "HANOI")

    url = "https://api.openweathermap.org/data/2.5/weather"
    r = requests.get(url, params={
        "q": loc,
        "appid": API_KEY,
        "units": "metric"
    })
    data = r.json()

    condition = map_condition(data["weather"][0]["main"])

    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<weatherdata>
  <weather location="{data['name']}"
           temperature="{round(data['main']['temp'])}"
           humidity="{data['main']['humidity']}"
           wind="{data['wind']['speed']}"
           condition="{condition}" />
</weatherdata>
"""
    return Response(xml, mimetype="application/xml")


# =========================
# 📈 STOCK API (fake demo)
# =========================
@app.route("/getstocks")
def get_stocks():
    imei = request.args.get("imei", "TEST")

    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<stockdata>
  <stock symbol="AAPL" price="190.25" change="+1.25"/>
  <stock symbol="GOOG" price="2800.10" change="-5.10"/>
</stockdata>
"""
    return Response(xml, mimetype="application/xml")


@app.route("/")
def home():
    return "HTC HD2 Weather/Stock Server is running!"
