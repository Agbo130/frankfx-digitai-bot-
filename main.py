# ✅ main.py (Final Fully Working Version)

from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

SESSION_FILE = os.path.join(os.path.dirname(__file__), 'session.json')

# Utility to read session.json
def read_session():
    if not os.path.exists(SESSION_FILE):
        return {}
    with open(SESSION_FILE, 'r') as f:
        return json.load(f)

# Utility to write session.json
def write_session(data):
    with open(SESSION_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/connect', methods=['POST'])
def connect():
    token = request.json.get('token')
    session = read_session()
    session['token'] = token
    session['authorized'] = False
    write_session(session)
    return jsonify({"message": "Token saved. Waiting for authorization..."})

@app.route('/session')
def session_data():
    session = read_session()
    return jsonify(session)

@app.route('/trade', methods=['POST'])
def trade():
    data = request.json
    prediction = data.get('prediction')
    amount = data.get('amount')

    session = read_session()
    session['current_prediction'] = prediction
    session['auto_trade'] = True
    session['trade_amount'] = amount
    write_session(session)

    return jsonify({"message": f"Trade request: {prediction.lower()} {amount}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
