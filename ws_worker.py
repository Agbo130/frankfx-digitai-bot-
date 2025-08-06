import websocket
import json
import threading
import time

# Global session storage
session = {}

def on_message(ws, message):
    global session
    data = json.loads(message)

    if 'msg_type' in data:
        if data['msg_type'] == 'authorize':
            session['account'] = data['authorize']['loginid']
            session['balance'] = data['authorize']['balance']
            save_file('session.json', session)

        elif data['msg_type'] == 'balance':
            session['balance'] = data['balance']['balance']
            save_file('session.json', session)

        elif data['msg_type'] == 'tick':
            digit = int(data['tick']['quote']) % 10
            prediction = "EVEN" if digit % 2 == 0 else "ODD"
            confidence = 95  # placeholder
            safe_entry = "Yes" if confidence > 80 else "No"
            save_file('ai_signal.json', {
                "latest_digit": digit,
                "prediction": prediction,
                "confidence": confidence,
                "safe_entry": safe_entry
            })

def on_error(ws, error):
    print("WebSocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def on_open(ws):
    print("WebSocket opened")
    auth_token = session.get("token")
    ws.send(json.dumps({"authorize": auth_token}))
    ws.send(json.dumps({"balance": 1, "subscribe": 1}))
    ws.send(json.dumps({"ticks": "R_10", "subscribe": 1}))

def save_file(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)

def check_token_loop():
    global session
    while True:
        try:
            with open("session.json", "r") as f:
                session = json.load(f)
        except:
            session = {}

        if session.get("token"):
            run_websocket(session["token"])
        time.sleep(5)

def run_websocket(token):
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(
        "wss://ws.derivws.com/websockets/v3?app_id=90203",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

threading.Thread(target=check_token_loop).start()
