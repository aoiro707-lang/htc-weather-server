from flask import Flask, request, Response
import json, math, requests, time

app = Flask(__name__)

API_KEY = "0c60b2b833632e5c653f6c29dada5dfa"

# =============================
# LOAD DATA
# =============================
with open("locations_hcm_full.json", "r", encoding="utf-8") as f:
    LOCATIONS = json.load(f)

# =============================
# KD TREE
# =============================
class KDNode:
    def __init__(self, point, data, axis, left=None, right=None):
        self.point = point
        self.data = data
        self.axis = axis
        self.left = left
        self.right = right

def build_kdtree(points, depth=0):
    if not points:
        return None
    axis = depth % 2
    points.sort(key=lambda x: x[0][axis])
    mid = len(points) // 2
    return KDNode(
        points[mid][0],
        points[mid][1],
        axis,
        build_kdtree(points[:mid], depth+1),
        build_kdtree(points[mid+1:], depth+1)
    )

def distance(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def nearest(root, target, best=None):
    if root is None:
        return best

    d = distance(target, root.point)
    if best is None or d < best[1]:
        best = (root, d)

    axis = root.axis
    diff = target[axis] - root.point[axis]

    close = root.left if diff < 0 else root.right
    away = root.right if diff < 0 else root.left

    best = nearest(close, target, best)

    if abs(diff) < best[1]:
        best = nearest(away, target, best)

    return best

POINTS = [((loc["lat"], loc["lon"]), loc) for loc in LOCATIONS]
KD_TREE = build_kdtree(POINTS)

# =============================
# CACHE
# =============================
CACHE = {}

def get_cache(key):
    now = time.time()
    if key in CACHE:
        data, ts = CACHE[key]
        if now - ts < 600:
            print(f"[CACHE HIT] {key}")
            return data
    return None

def set_cache(key, data):
    CACHE[key] = (data, time.time())

# =============================
# DAY / NIGHT
# =============================
def is_night(data):
    now = time.time()
    return now < data["sys"]["sunrise"] or now > data["sys"]["sunset"]

# =============================
# HTC ICON FULL MAP (01–44)
# =============================
def map_icon(data):
    main = data["weather"][0]["main"]
    desc = data["weather"][0]["description"].lower()
    night = is_night(data)

    # CLEAR
    if main == "Clear":
        return "02" if night else "01"

    # CLOUDS
    if main == "Clouds":
        if "few" in desc:
            return "04" if night else "03"
        elif "scattered" in desc:
            return "04" if night else "03"
        elif "broken" in desc:
            return "06"
        else:
            return "07"

    # DRIZZLE
    if main == "Drizzle":
        return "13"

    # RAIN
    if main == "Rain":
        if "light" in desc:
            return "13"
        elif "heavy" in desc:
            return "12"
        else:
            return "12"

    # THUNDER
    if main == "Thunderstorm":
        return "15"

    # SNOW
    if main == "Snow":
        return "22"

    # ATMOSPHERE
    if main in ["Mist", "Fog", "Haze"]:
        return "10"

    # DEFAULT
    return "07"

# =============================
# LOCATION (KD + FALLBACK)
# =============================
def find_location(lat, lon):
    node, dist = nearest(KD_TREE, (lat, lon))

    if node:
        loc = node.data

        if dist < 0.01:
            return f"{loc['name']}, {loc['district']}"

        elif dist < 0.03:
            return loc['district']

    return "Ho Chi Minh City"

# =============================
# API
# =============================
@app.route("/getweather")
def get_weather():
    lat = float(request.args.get("lat"))
    lon = float(request.args.get("lon"))
    device = request.remote_addr

    print(f"\n[REQUEST] {device} lat={lat} lon={lon}")

    location_name = find_location(lat, lon)

    cache_key = f"{lat}_{lon}"
    data = get_cache(cache_key)

    if not data:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
        )
        data = r.json()
        set_cache(cache_key, data)

    temp = round(data["main"]["temp"])
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]

    icon = map_icon(data)

    print(f"[LOCATION] {location_name}")
    print(f"[ICON] {icon}")

    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<weatherdata>
  <weather location="{location_name}"
           temperature="{temp}"
           humidity="{humidity}"
           wind="{wind}"
           icon="{icon}" />
</weatherdata>
"""

    print(f"[RESPONSE SENT] → {device}")

    return Response(xml, mimetype="application/xml")

@app.route("/")
def home():
    return "HTC HD2 Weather Server FULL ICON 44 OK"
