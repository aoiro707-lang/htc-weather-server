from flask import Flask, request, jsonify
from flask_cors import CORS   # 👈 THÊM

app = Flask(__name__)
CORS(app)   # 👈 CHO PHÉP TẤT CẢ ORIGIN

relay_state = "OFF"

@app.route("/")
def home():
    return "ESP01 Relay Server Running"

@app.route("/relay", methods=["GET", "POST"])
def relay():
    global relay_state

    if request.method == "POST":
        data = request.get_json(silent=True)
        if data and "state" in ["ON", "OFF"]:
            relay_state = data["state"]
        return jsonify({"ok": True, "state": relay_state})

    return jsonify({"state": relay_state})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
