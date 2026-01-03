# ESP01s
import threading, time, requests

from flask import Flask, request, jsonify

app = Flask(__name__)

# trạng thái relay lưu trên server
relay_state = "OFF"

@app.route("/")
def home():
    return "HTC IoT Server Running"

# ESP gọi để lấy trạng thái
@app.route("/relay", methods=["GET"])
def get_relay():
    return jsonify({"state": relay_state})

# Phone / app gọi để set trạng thái
@app.route("/relay", methods=["POST"])
def set_relay():
    global relay_state
    data = request.json
    if "state" in data:
        relay_state = data["state"]
        return jsonify({"ok": True, "state": relay_state})
    return jsonify({"ok": False}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
# ESP01s

