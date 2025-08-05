from flask import Flask, render_template, request, jsonify
import threading
import websocket
import json
import time

app = Flask(__name__)

# Global storage (for demo)
session_data = {
    'token': None,
    'ws': None,
    'authorized': False,
    'latest_tick': None,
    'digits': [],
    'trade_result': None
}

# === WebSocket connection handler ===
def start_ws():
    def on_message(ws, message):
        data = json.loads(message)

        if data.get('msg_type') == 'authorize':
            session_data['authorized'] = True

        elif data.get('msg_type') == 'tick':
            digit = int(data['tick']['quote'][-1])
            session_data['latest_tick'] = digit
            session_data['digits'].append(digit)
            if len(session_data['digits']) > 30:
                session_data['digits'].pop(0)

        elif data.get('msg_type') == 'buy':
            contract_id = data['buy']['contract_id']
            session_data['trade_result'] = f"Trade executed: Contract ID {contract_id}"

    def on_open(ws):
        ws.send(json.dumps({"authorize": session_data['token']}))
        ws.send(json.dumps({"ticks": "R_10", "subscribe": 1}))

    def on_error(ws, error):
        print("WebSocket Error:", error)

    def on_close(ws, close_status_code, close_msg):
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

# === Flask routes ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set-token', methods=['POST'])
def set_token():
    token = request.json.get('token')
    session_data['token'] = token
    session_data['authorized'] = False
    session_data['digits'] = []
    threading.Thread(target=start_ws).start()
    return jsonify({"status": "WebSocket started"})

@app.route('/latest')
def latest():
    return jsonify({
        "digit": session_data['latest_tick'],
        "digits": session_data['digits'],
        "result": session_data['trade_result']
    })

@app.route('/trade', methods=['POST'])
def trade():
    direction = request.json.get('direction')  # 'even' or 'odd'
    amount = float(request.json.get('amount', 1))

    contract_type = "DIGITEVEN" if direction == "even" else "DIGITODD"
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)