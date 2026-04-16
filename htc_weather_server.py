from flask import Flask, request, Response
import requests
import time
import datetime

app = Flask(__name__)

API_KEY = "0c60b2b833632e5c653f6c29dada5dfa"

# =============================
# CACHE (giảm lag Render)
# =============================
CACHE = {}

def get_cache(key):
    now = time.time()
    if key in CACHE:
        data, ts = CACHE[key]
        if now - ts < 600:  # 10 phút
            print(f"[CACHE HIT] {key}")
            return data
    return None

def set_cache(key, data):
    CACHE[key] = (data, time.time())


# =============================
# Parse locCode HTC
# =============================
def parse_loccode(locCode):
    try:
        return locCode.split("|")[-1]
    except:
        return locCode


# =============================
# Day/Night detection
# =============================
def is_night(dt, sunrise, sunset):
    return dt < sunrise or dt > sunset


# =============================
# Map icon HTC
# =============================
def map_icon(data, sunrise, sunset):
    main = data["weather"][0]["main"]
    desc = data["weather"][0]["description"]
    dt = data["dt"]

    icon = 7

    if main == "Clear":
        icon = 1
    elif main == "Clouds":
        if "few" in desc:
            icon = 3
        elif "scattered" in desc:
            icon = 4
        elif "broken" in desc:
            icon = 6
        else:
            icon = 7
    elif main == "Rain":
        icon = 12
    elif main == "Thunderstorm":
        icon = 15
    elif main == "Snow":
        icon = 22
    elif main in ["Mist", "Fog", "Haze"]:
        icon = 11

    # night mode
    if is_night(dt, sunrise, sunset):
        if icon <= 32:
            icon += 32

    return icon


# =============================
# BUILD XML RESPONSE
# =============================
def build_xml(location, current, forecast_xml):
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<weatherdata>
  <weather location="{location}">
    {current}
    {forecast_xml}
  </weather>
</weatherdata>
"""
    return xml


# =============================
# 🌦 GET WEATHER (GPS)
# =============================
@app.route("/getweather")
def get_weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    device = request.remote_addr

    print(f"\n[REQUEST GPS] Device={device} lat={lat} lon={lon}")

    if not lat or not lon:
        print("[ERROR] GPS missing → fallback static")
        return get_static_weather()

    cache_key = f"gps_{lat}_{lon}"
    data = get_cache(cache_key)

    if not data:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
        )
        data = r.json()
        set_cache(cache_key, data)

    return process_weather(data, device)


# =============================
# 🌍 STATIC WEATHER (CITY)
# =============================
@app.route("/getstaticweather")
def get_static_weather():
    locCode = request.args.get("locCode", "HANOI")
    city = parse_loccode(locCode)
    device = request.remote_addr

    print(f"\n[REQUEST STATIC] Device={device} locCode={locCode} → city={city}")

    cache_key = f"city_{city}"
    data = get_cache(cache_key)

    if not data:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={"q": city, "appid": API_KEY, "units": "metric"}
        )
        data = r.json()
        set_cache(cache_key, data)

    return process_weather(data, device)


# =============================
# PROCESS WEATHER CORE
# =============================
def process_weather(data, device):

    city = data["city"]["name"]
    sunrise = data["city"]["sunrise"]
    sunset = data["city"]["sunset"]

    # ===== CURRENT =====
    current_data = data["list"][0]

    icon = map_icon(current_data, sunrise, sunset)
    temp = round(current_data["main"]["temp"])
    humidity = current_data["main"]["humidity"]
    wind = current_data["wind"]["speed"]

    current_xml = f"""
<current temperature="{temp}" icon="{icon}" />
"""

    print(f"[CURRENT] {city} temp={temp} icon={icon}")

    # ===== FORECAST =====
    days = {}
    for item in data["list"]:
        date = item["dt_txt"].split(" ")[0]
        if date not in days:
            days[date] = []
        days[date].append(item)

    forecast_xml = ""
    count = 0

    for date, items in days.items():
        if count >= 5:
            break

        temps = [i["main"]["temp"] for i in items]
        high = round(max(temps))
        low = round(min(temps))

        icon_day = map_icon(items[0], sunrise, sunset)

        day_name = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%a")

        forecast_xml += f"""
<forecast day="{day_name}" high="{high}" low="{low}" icon="{icon_day}" />
"""

        print(f"[FORECAST] {day_name} {high}/{low} icon={icon_day}")

        count += 1

    xml = build_xml(city, current_xml, forecast_xml)

    print(f"[RESPONSE SENT] → Device {device}")
    print(xml)

    return Response(xml, mimetype="application/xml")


# =============================
# HOME
# =============================
@app.route("/")
def home():
    return "HTC HD2 Weather Server OK"
