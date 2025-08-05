import websocket
import json
import time

SESSION_FILE = 'session.json'

def read_session():
    with open(SESSION_FILE, 'r') as f:
        return json.load(f)

def write_session(data):
    with open(SESSION_FILE, 'w') as f:
        json.dump(data, f)

def on_message(ws, message):
    session = read_session()
    data = json.loads(message)

    if data.get('msg_type') == 'authorize':
        session['authorized'] = True
        ws.send(json.dumps({"balance": 1, "subscribe": 1}))
        ws.send(json.dumps({"ticks": "R_10", "subscribe": 1}))

    elif data.get('msg_type') == 'balance':
        session['account_info'] = {
            'balance': data['balance']['balance'],
            'currency': data['balance']['currency'],
            'account_type': data['balance']['loginid']
        }

    elif data.get('msg_type') == 'tick':
        digit = int(data['tick']['quote'][-1])
        session['latest_tick'] = digit
        session['digits'].append(digit)
        if len(session['digits']) > 20:
            session['digits'].pop(0)

        prediction = session.get('current_prediction')
        if session.get('auto_trade') and prediction:
            if (prediction == 'EVEN' and digit % 2 == 0) or (prediction == 'ODD' and digit % 2 != 0):
                session['win_count'] += 1
                session['trade_result'] = "✅ WIN"
            else:
                session['loss_count'] += 1
                session['trade_result'] = "❌ LOSS"
            session['current_prediction'] = None

    write_session(session)

def on_open(ws):
    session = read_session()
    if session.get('token'):
        ws.send(json.dumps({"authorize": session['token']}))
    else:
        print("No token found")

def on_error(ws, error):
    print("WebSocket error:", error)

def on_close(ws, code, msg):
    print("WebSocket closed")

def run_ws():
    while True:
        try:
            ws = websocket.WebSocketApp(
                "wss://ws.deriv.com/websockets/v3",
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever()
        except Exception as e:
            print("Error:", e)
        time.sleep(5)

if __name__ == '__main__':
    run_ws()
