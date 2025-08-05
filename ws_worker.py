import websocket
import json
import time

# === SESSION DATA (simulated memory, replace with shared DB or Redis for production)
session_data = {
    'token': None,
    'authorized': False,
    'latest_tick': None,
    'digits': [],
    'account_info': {},
    'auto_trade': False,
    'current_prediction': None,
    'win_count': 0,
    'loss_count': 0
}

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
            prediction = session_data['current_prediction']
            if (prediction == 'EVEN' and digit % 2 == 0) or (prediction == 'ODD' and digit % 2 != 0):
                session_data['win_count'] += 1
            else:
                session_data['loss_count'] += 1
            session_data['current_prediction'] = None

    elif data.get('msg_type') == 'buy':
        print(f"Trade placed! Contract ID: {data['buy']['contract_id']}")

def on_open(ws):
    if session_data['token']:
        ws.send(json.dumps({"authorize": session_data['token']}))
    else:
        print("Waiting for token...")

def on_error(ws, error):
    print("WebSocket Error:", error)

def on_close(ws, code, msg):
    print("WebSocket Closed")

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
    # Paste your token directly here for now
    session_data['token'] = "PASTE_YOUR_DERIV_TOKEN_HERE"
    session_data['auto_trade'] = True
    run_ws()
