from flask import Flask, request, jsonify

app = Flask(__name__)

# ====== BIẾN LƯU TRẠNG THÁI RELAY ======
relay_state = "OFF"   # ON / OFF

@app.route("/")
def home():
    return "ESP01 Relay Server Running"

@app.route("/relay", methods=["GET", "POST"])
def relay():
    global relay_state

    # ---- POST: set trạng thái ----
    if request.method == "POST":
        data = request.get_json(silent=True)
        if data and "state" in data:
            if data["state"] in ["ON", "OFF"]:
                relay_state = data["state"]
        return jsonify({
            "ok": True,
            "state": relay_state
        })

    # ---- GET: đọc trạng thái ----
    return jsonify({
        "state": relay_state
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
