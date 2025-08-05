from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)
SESSION_FILE = 'session.json'

def read_session():
    with open(SESSION_FILE, 'r') as f:
        return json.load(f)

def write_session(data):
    with open(SESSION_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set-token', methods=['POST'])
def set_token():
    session = read_session()
    session['token'] = request.json.get('token')
    write_session(session)
    return jsonify({"status": "Token saved"})

@app.route('/latest')
def latest():
    session = read_session()
    return jsonify({
        "digit": session['latest_tick'],
        "digits": session['digits'],
        "result": session['trade_result'],
        "account": session['account_info'],
        "win": session['win_count'],
        "loss": session['loss_count']
    })

@app.route('/trade', methods=['POST'])
def trade():
    session = read_session()
    direction = request.json.get('direction')
    amount = float(request.json.get('amount', 1))
    session['current_prediction'] = direction.upper()
    session['trade_result'] = f"Trade request: {direction} {amount}"
    write_session(session)
    return jsonify({"status": session['trade_result']})

@app.route('/auto-toggle', methods=['POST'])
def auto_toggle():
    session = read_session()
    session['auto_trade'] = request.json.get('state')
    write_session(session)
    return jsonify({"status": f"Auto mode {'enabled' if session['auto_trade'] else 'disabled'}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
