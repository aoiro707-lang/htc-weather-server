# =============================
# API (HTC FLOW)
# =============================

@app.route("/getweather")
def get_weather():
    lat = float(request.args.get("lat"))
    lon = float(request.args.get("lon"))
    device = request.remote_addr

    print(f"\n[REQUEST GEO] {device} lat={lat} lon={lon}")

    location_name = find_location(lat, lon)

    # 👉 chuẩn hoá locCode (KHÔNG dấu, không space)
    loc_clean = location_name.upper().replace(" ", "").replace(",", "")
    loc_code = f"NAM|VN|HCM|{loc_clean}"

    print(f"[LOC CODE] {loc_code}")

    # ❗ HTC chỉ cần text
    return loc_code


@app.route("/getstaticweather")
def get_static_weather():
    device = request.remote_addr
    loc = request.args.get("locCode", "UNKNOWN")

    print(f"\n[REQUEST WEATHER] {device} loc={loc}")

    # 👉 TẠM FIX: dùng 1 tọa độ (bạn có thể map ngược sau)
    lat, lon = 10.699347, 106.445808

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

    icon = map_icon(data)

    print(f"[ICON] {icon}")
    print(f"[TEMP] {temp}°C")

    # ❗ XML CHUẨN HTC
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<weatherdata>
  <weather location="{loc}"
           temperature="{temp}"
           humidity="{humidity}"
           wind="{wind}"
           icon="{icon}" />
</weatherdata>
"""

    print(f"[RESPONSE SENT] → {device}")

    return Response(xml, content_type="text/xml")


@app.route("/")
def home():
    return "HTC HD2 Weather Server (HTC FLOW OK)"
