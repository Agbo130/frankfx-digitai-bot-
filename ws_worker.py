import websocket
import json
import time
import os

SESSION_FILE = 'session.json'

def read_session():
    if not os.path.exists(SESSION_FILE):
        return {
            "token": None,
            "authorized": False,
            "latest_tick": None,
            "digits": [],
            "account_info": {
                "balance": 0,
                "currency": "USD",
                "account_type": ""
            },
            "auto_trade": False,
            "current_prediction": None,
            "win_count": 0,
            "loss_count": 0,
            "trade_result": "-"
        }
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
        # ✅ Request balance
        ws.send(json.dumps({"balance": 1, "subscribe": 1}))
        # ✅ Subscribe to ticks
        ws.send(json.dumps({"ticks": "R_10", "subscribe": 1}))

    elif data.get('msg_type') == 'balance':
        balance_info = data.get('balance', {})
        session['account_info'] = {
            'balance': round(balance_info.get('balance', 0), 2),
            'currency': balance_info.get('currency', 'USD'),
            'account_type': balance_info.get('loginid', '')
        }

    elif data.get('msg_type') == 'tick':
        tick = data.get('tick', {})
        if 'quote' in tick:
            try:
                digit = int(str(tick['quote'])[-1])
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
            except:
                pass

    write_session(session)

def on_open(ws):
    session = read_session()
    token = session.get('token')
    if token:
        ws.send(json.dumps({"authorize": token}))
    else:
        print("❌ No token provided.")

def on_error(ws, error):
    print("WebSocket error:", error)

def on_close(ws, code, msg):
    print("WebSocket closed. Code:", code, "| Msg:", msg)

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
