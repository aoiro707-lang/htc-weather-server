from flask import Flask, request, Response
import requests

app = Flask(__name__)

# API key OpenWeatherMap
OPENWEATHER_API_KEY = "0c60b2b833632e5c653f6c29dada5dfa"

@app.route("/getweather")
def get_weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric", "lang": "vi"}
    r = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params)
    data = r.json()
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<weather>
    <temp>{data['main']['temp']}</temp>
    <humidity>{data['main']['humidity']}</humidity>
    <desc>{data['weather'][0]['description']}</desc>
</weather>"""
    return Response(xml, mimetype="application/xml")

@app.route("/getstaticweather")
def get_staticweather():
    locCode = request.args.get("locCode")
    params = {"q": locCode, "appid": OPENWEATHER_API_KEY, "units": "metric", "lang": "vi"}
    r = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params)
    data = r.json()
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<weather>
    <city>{locCode}</city>
    <temp>{data['main']['temp']}</temp>
    <humidity>{data['main']['humidity']}</humidity>
    <desc>{data['weather'][0]['description']}</desc>
</weather>"""
    return Response(xml, mimetype="application/xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
