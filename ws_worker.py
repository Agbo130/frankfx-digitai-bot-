import websocket
import json
import time

TOKEN = "BjAkf7K1UN88uaH"
SIGNAL_FILE = "ai_signal.json"
SESSION_FILE = "session.json"

recent_digits = []

def calculate_prediction():
    odd = sum(1 for d in recent_digits if d % 2 != 0)
    even = len(recent_digits) - odd
    if even > odd:
        prediction = "EVEN"
        confidence = int((even / len(recent_digits)) * 100)
    else:
        prediction = "ODD"
        confidence = int((odd / len(recent_digits)) * 100)
    safe = "YES" if confidence >= 70 else "NO"
    return prediction, confidence, safe

def save_signal(digit, prediction, confidence, safe):
    signal = {
        "latest_digit": digit,
        "prediction": prediction,
        "confidence": f"{confidence}%",
        "safe_entry": safe
    }
    with open(SIGNAL_FILE, "w") as f:
        json.dump(signal, f)
    print("✅ AI Prediction written:", signal)

def save_balance(balance, loginid):
    try:
        with open(SESSION_FILE, "r") as f:
            session = json.load(f)
    except:
        session = {}

    session["balance"] = balance
    session["account_id"] = loginid
    with open(SESSION_FILE, "w") as f:
        json.dump(session, f)

def on_message(ws, message):
    data = json.loads(message)

    if data.get("msg_type") == "authorize":
        print("✅ Authorized to Deriv.")
        ws.send(json.dumps({"balance": 1, "subscribe": 1}))
        ws.send(json.dumps({"ticks": "R_10", "subscribe": 1}))

    elif data.get("msg_type") == "balance":
        bal = data["balance"]["balance"]
        loginid = data["balance"]["loginid"]
        save_balance(bal, loginid)

    elif data.get("msg_type") == "tick":
        digit = int(str(data["tick"]["quote"])[-1])
        recent_digits.append(digit)
        if len(recent_digits) > 10:
            recent_digits.pop(0)
        prediction, confidence, safe = calculate_prediction()
        save_signal(digit, prediction, confidence, safe)

def on_open(ws):
    print("🔐 Authorizing...")
    ws.send(json.dumps({"authorize": TOKEN}))

def on_error(ws, error):
    print("❌ Error:", error)

def on_close(ws, code, msg):
    print("🔁 WebSocket closed. Reconnecting in 5s...")
    time.sleep(5)
    run_ws()

def run_ws():
    ws = websocket.WebSocketApp(
        "wss://ws.deriv.com/websockets/v3",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

if __name__ == "__main__":
    run_ws()
