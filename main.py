from flask import Flask, render_template, request, jsonify
import subprocess
import threading
import os
import json

app = Flask(__name__)

# Launch WebSocket worker
def start_ws_worker():
    subprocess.Popen(["python", "ws_worker.py"])

threading.Thread(target=start_ws_worker).start()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/session', methods=['GET'])
def session_data():
    try:
        with open("session.json", "r") as f:
            return jsonify(json.load(f))
    except:
        return jsonify({})

@app.route('/signal', methods=['GET'])
def signal_data():
    try:
        with open("ai_signal.json", "r") as f:
            return jsonify(json.load(f))
    except:
        return jsonify({})

@app.route('/trade', methods=['POST'])
def trade():
    data = request.json
    with open("trade_request.json", "w") as f:
        json.dump(data, f)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
