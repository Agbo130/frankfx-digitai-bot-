from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# === Shared Session (via JSON or Redis in full setup)
session_data = {
    'latest_tick': None,
    'digits': [],
    'trade_result': None,
    'account_info': {},
    'auto_trade': False,
    'current_prediction': None,
    'win_count': 0,
    'loss_count': 0,
    'token': None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set-token', methods=['POST'])
def set_token():
    session_data['token'] = request.json.get('token')
    return jsonify({"status": "Token received"})

@app.route('/latest')
def latest():
    return jsonify({
        "digit": session_data['latest_tick'],
        "digits": session_data['digits'],
        "result": session_data['trade_result'],
        "account": session_data['account_info'],
        "win": session_data['win_count'],
        "loss": session_data['loss_count']
    })

@app.route('/trade', methods=['POST'])
def trade():
    direction = request.json.get('direction')
    amount = float(request.json.get('amount', 1))
    session_data['current_prediction'] = direction.upper()
    # ws_worker will pick this up in background
    return jsonify({"status": f"Trade request: {direction} {amount}"})

@app.route('/auto-toggle', methods=['POST'])
def auto_toggle():
    session_data['auto_trade'] = request.json.get('state')
    return jsonify({"status": f"Auto mode {'enabled' if session_data['auto_trade'] else 'disabled'}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
