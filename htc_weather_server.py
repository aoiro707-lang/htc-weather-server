from flask import Flask, request, Response
import requests
import json
import time
import math

app = Flask(__name__)

API_KEY = "0c60b2b833632e5c653f6c29dada5dfa"

# =============================
# LOAD LOCATION DATA
# =============================
with open("locations_vn_south.json", "r", encoding="utf-8") as f:
    LOCATIONS = json.load(f)

# =============================
# KD-TREE IMPLEMENTATION
# =============================
class KDNode:
    def __init__(self, point, data, axis, left=None, right=None):
        self.point = point  # (lat, lon)
        self.data = data
        self.axis = axis
        self.left = left
        self.right = right


def build_kdtree(points, depth=0):
    if not points:
        return None

    k = 2
    axis = depth % k
    points.sort(key=lambda x: x[0][axis])
    mid = len(points) // 2

    return KDNode(
        point=points[mid][0],
        data=points[mid][1],
        axis=axis,
        left=build_kdtree(points[:mid], depth + 1),
        right=build_kdtree(points[mid + 1:], depth + 1),
    )


def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def nearest_neighbor(root, target, best=None):
    if root is None:
        return best

    d = distance(target, root.point)

    if best is None or d < best[1]:
        best = (root, d)

    axis = root.axis
    diff = target[axis] - root.point[axis]

    close, away = (root.left, root.right) if diff < 0 else (root.right, root.left)

    best = nearest_neighbor(close, target, best)

    if abs(diff) < best[1]:
        best = nearest_neighbor(away, target, best)

    return best


# Build KD-tree once
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
# FIND LOCATION (KD-TREE)
# =============================
def find_location(lat, lon):
    lat = float(lat)
    lon = float(lon)

    node, dist = nearest_neighbor(KD_TREE, (lat, lon))

    if node:
        loc = node.data
        print(f"[KD-TREE] Found {loc['name']} ({dist:.5f})")
        return f"{loc['name']}, {loc['province']}"

    return "Unknown"

# =============================
# ICON MAP
# =============================
def map_icon(main):
    if main == "Clear":
        return 1
    elif main == "Clouds":
        return 7
    elif main == "Rain":
        return 12
    elif main == "Thunderstorm":
        return 15
    elif main == "Snow":
        return 22
    elif main in ["Mist", "Fog"]:
        return 11
    return 7

# =============================
# WEATHER API
# =============================
@app.route("/getweather")
def get_weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    device = request.remote_addr

    print(f"\n[REQUEST] Device={device} lat={lat} lon={lon}")

    if not lat or not lon:
        return "Missing lat/lon"

    location_name = find_location(lat, lon)

    cache_key = f"{lat}_{lon}"
    data = get_cache(cache_key)

    if not data:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": lat,
                "lon": lon,
                "appid": API_KEY,
                "units": "metric"
            }
        )
        data = r.json()
        set_cache(cache_key, data)

    temp = round(data["main"]["temp"])
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]
    condition = data["weather"][0]["main"]

    icon = map_icon(condition)

    print(f"[RESULT] {location_name} temp={temp} condition={condition}")

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
    print(xml)

    return Response(xml, mimetype="application/xml")


# =============================
# HOME
# =============================
@app.route("/")
def home():
    return "KD-Tree Weather Server Running"
