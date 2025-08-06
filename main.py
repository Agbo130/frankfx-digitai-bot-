from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/session', methods=['GET', 'POST'])
def session_data():
    if request.method == 'POST':
        data = request.get_json()
        with open("session.json", "w") as f:
            json.dump(data, f)
        return jsonify({"status": "saved"})
    else:
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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
