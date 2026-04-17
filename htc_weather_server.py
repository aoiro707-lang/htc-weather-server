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
# FIND LOCATION (HTC STYLE)
# =============================
def find_location(lat, lon):
    node, dist = nearest(KD_TREE, (lat, lon))

    if node:
        loc = node.data

        # phường (rất gần)
        if dist < 0.01:
            return f"{loc['name']}, {loc['district']}"

        # fallback quận
        elif dist < 0.03:
            return loc['district']

    return "Ho Chi Minh City"

# =============================
# ICON MAP
# =============================
def map_icon(main):
    return {
        "Clear": 1,
        "Clouds": 7,
        "Rain": 12,
        "Thunderstorm": 15,
        "Snow": 22,
        "Mist": 11
    }.get(main, 7)

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
    condition = data["weather"][0]["main"]

    icon = map_icon(condition)

    print(f"[LOCATION] {location_name}")
    print(f"[WEATHER] temp={temp} cond={condition}")

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

# =============================
# HOME
# =============================
@app.route("/")
def home():
    return "HTC HD2 Weather Server (KD-tree FULL) OK"
