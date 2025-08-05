from flask import Flask, render_template, request, jsonify
import websocket
import json

app = Flask(__name__)

# === SESSION STATE ===
session_data = {
    'token': None,
    'ws': None,
    'authorized': False,
    'latest_tick': None,
    'digits': [],
    'trade_result': None,
    'account_info': {},
    'auto_trade': False,
    'current_prediction': None,
    'strategy': 'even',  # Default
    'win_count': 0,
    'loss_count': 0
}

# === START WEBSOCKET TO DERIV ===
def start_ws():
    def on_message(ws, message):
        data = json.loads(message)

        if data.get('msg_type') == 'authorize':
            session_data['authorized'] = True
            ws.send(json.dumps({"balance": 1, "subscribe": 1}))
            ws.send(json.dumps({"ticks": "R_10", "subscribe": 1}))

        elif data.get('msg_type') == 'balance':
            session_data['account_info'] = {
                'balance': data['balance']['balance'],
                'currency': data['balance']['currency'],
                'account_type': data['balance']['loginid']
            }

        elif data.get('msg_type') == 'tick':
            digit = int(data['tick']['quote'][-1])
            session_data['latest_tick'] = digit
            session_data['digits'].append(digit)
            if len(session_data['digits']) > 20:
                session_data['digits'].pop(0)

            if session_data['auto_trade'] and session_data['current_prediction']:
                if session_data['current_prediction'] == 'EVEN' and digit % 2 == 0:
                    session_data['win_count'] += 1
                elif session_data['current_prediction'] == 'ODD' and digit % 2 != 0:
                    session_data['win_count'] += 1
                else:
                    session_data['loss_count'] += 1

                session_data['current_prediction'] = None

        elif data.get('msg_type') == 'buy':
            contract_id = data['buy']['contract_id']
            session_data['trade_result'] = f"Trade executed: Contract ID {contract_id}"

    def on_open(ws):
        ws.send(json.dumps({"authorize": session_data['token']}))

    def on_error(ws, error):
        print("WebSocket Error:", error)

    def on_close(ws, code, msg):
        print("WebSocket Closed")

    ws = websocket.WebSocketApp(
        "wss://ws.deriv.com/websockets/v3",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    session_data['ws'] = ws
    ws.run_forever()

# === ROUTES ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set-token', methods=['POST'])
def set_token():
    token = request.json.get('token')
    session_data['token'] = token
    session_data['authorized'] = False
    session_data['digits'] = []
    session_data['win_count'] = 0
    session_data['loss_count'] = 0

    # ✅ FIX FOR RAILWAY (run directly, not in thread)
    start_ws()

    return jsonify({"status": "WebSocket started"})

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

    contract_type = "DIGITEVEN" if direction == "even" else "DIGITODD"
    session_data['current_prediction'] = direction.upper()

    trade_request = {
        "buy": "1",
        "price": amount,
        "parameters": {
            "amount": amount,
            "basis": "stake",
            "contract_type": contract_type,
            "currency": "USD",
            "duration": 1,
            "duration_unit": "t",
            "symbol": "R_10"
        }
    }

    if session_data['ws']:
        session_data['ws'].send(json.dumps(trade_request))
        return jsonify({"status": f"Trade sent: {contract_type}"})
    else:
        return jsonify({"error": "WebSocket not connected"})

@app.route('/auto-toggle', methods=['POST'])
def auto_toggle():
    state = request.json.get('state')
    session_data['auto_trade'] = state
    return jsonify({"status": f"Auto mode {'enabled' if state else 'disabled'}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
