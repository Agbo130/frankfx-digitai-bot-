import websocket
import json
import time

SESSION_FILE = "session.json"
SIGNAL_FILE = "ai_signal.json"

def read_token():
    try:
        with open(SESSION_FILE, "r") as f:
            return json.load(f).get("token")
    except:
        return None

def write_session(account_id, balance):
    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
    except:
        data = {}
    data["account_id"] = account_id
    data["balance"] = "{:.2f}".format(balance)
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f)

def write_signal(digit, prediction, confidence, safe):
    signal = {
        "latest_digit": str(digit),
        "prediction": prediction,
        "confidence": f"{confidence}%",
        "safe_entry": safe
    }
    with open(SIGNAL_FILE, "w") as f:
        json.dump(signal, f)

def on_message(ws, message):
    data = json.loads(message)

    if "authorize" in data:
        acc = data["authorize"]["loginid"]
        bal = data["authorize"]["balance"]
        write_session(acc, bal)
        ws.send(json.dumps({"ticks": "R_10", "subscribe": 1}))

    elif "tick" in data:
        digit = int(str(data["tick"]["quote"])[-1])
        prediction = "EVEN" if digit % 2 == 0 else "ODD"
        confidence = 85 if prediction == "EVEN" else 75
        safe = "YES" if confidence >= 80 else "NO"
        write_signal(digit, prediction, confidence, safe)

def on_open(ws):
    token = read_token()
    if token:
        ws.send(json.dumps({"authorize": token}))
    else:
        print("No token found.")

def run_ws():
    while True:
        try:
            ws = websocket.WebSocketApp(
                "wss://ws.derivws.com/websockets/v3",
                on_open=on_open,
                on_message=on_message
            )
            ws.run_forever()
        except Exception as e:
            print("WebSocket Error:", e)
            time.sleep(3)

if __name__ == "__main__":
    run_ws()
