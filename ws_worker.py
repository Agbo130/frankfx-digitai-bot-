import websocket
import json
import time

def get_token():
    try:
        with open("session.json", "r") as f:
            return json.load(f).get("token")
    except:
        return None

def update_session(account_id, balance):
    try:
        with open("session.json", "r") as f:
            data = json.load(f)
    except:
        data = {}
    data["account_id"] = account_id
    data["balance"] = f"{balance:.2f}"
    with open("session.json", "w") as f:
        json.dump(data, f)

def update_signal(digit, prediction, confidence, safe):
    signal = {
        "latest_digit": str(digit),
        "prediction": prediction,
        "confidence": f"{confidence}%",
        "safe_entry": safe
    }
    with open("ai_signal.json", "w") as f:
        json.dump(signal, f)

def on_message(ws, message):
    data = json.loads(message)

    if "msg_type" in data:
        if data["msg_type"] == "authorize":
            loginid = data["authorize"]["loginid"]
            balance = data["authorize"]["balance"]
            update_session(loginid, balance)
            ws.send(json.dumps({"ticks": "R_10", "subscribe": 1}))

        elif data["msg_type"] == "tick":
            digit = int(str(data["tick"]["quote"])[-1])
            prediction = "EVEN" if digit % 2 == 0 else "ODD"
            confidence = 85 if digit % 2 == 0 else 78
            safe = "YES" if confidence >= 80 else "NO"
            update_signal(digit, prediction, confidence, safe)

def on_open(ws):
    token = get_token()
    if not token:
        print("❌ No token in session.json")
        return
    ws.send(json.dumps({"authorize": token}))

def on_error(ws, error):
    print("WebSocket Error:", error)

def on_close(ws, *args):
    print("WebSocket Closed. Reconnecting in 5s...")
    time.sleep(5)
    run_ws()

def run_ws():
    ws = websocket.WebSocketApp(
        "wss://ws.binaryws.com/websockets/v3?app_id=90203",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

if __name__ == "__main__":
    run_ws()
