from flask import Flask, request, Response
import json, math, requests

app = Flask(__name__)

API_KEY = "0c60b2b833632e5c653f6c29dada5dfa"

# =============================
# LOAD DATA
# =============================
with open("locations_hcm_wards.json", "r", encoding="utf-8") as f:
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
# FIND LOCATION
# =============================
def find_location(lat, lon):
    node, dist = nearest(KD_TREE, (lat, lon))

    if node and dist < 0.02:
        loc = node.data
        return f"{loc['name']}, {loc['district']}"

    return "Ho Chi Minh City"

# =============================
# API
# =============================
@app.route("/getweather")
def get_weather():
    lat = float(request.args.get("lat"))
    lon = float(request.args.get("lon"))

    location_name = find_location(lat, lon)

    r = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
    )

    data = r.json()

    temp = round(data["main"]["temp"])
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]
    condition = data["weather"][0]["main"]

    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<weatherdata>
  <weather location="{location_name}"
           temperature="{temp}"
           humidity="{humidity}"
           wind="{wind}"
           condition="{condition}" />
</weatherdata>
"""

    print(f"[GPS] {lat},{lon} → {location_name}")

    return Response(xml, mimetype="application/xml")


@app.route("/")
def home():
    return "HCM Ward KD-Tree Server OK"
