
from flask import Flask, render_template, jsonify
import subprocess
import threading
import os
import json

app = Flask(__name__)

def start_ws_worker():
    subprocess.Popen(["python", "ws_worker.py"])

threading.Thread(target=start_ws_worker).start()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/session', methods=['GET'])
def get_session():
    try:
        with open("session.json", "r") as f:
            return jsonify(json.load(f))
    except:
        return jsonify({})

@app.route('/signal', methods=['GET'])
def get_signal():
    try:
        with open("ai_signal.json", "r") as f:
            return jsonify(json.load(f))
    except:
        return jsonify({})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
