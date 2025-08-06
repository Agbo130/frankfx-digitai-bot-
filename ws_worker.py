import websocket
import json
import time

TOKEN = "PASTE_YOUR_DERIV_TOKEN_HERE"  # 🔁 Replace with your token
SIGNAL_FILE = "ai_signal.json"

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
    data = {
        "latest_digit": digit,
        "prediction": prediction,
        "confidence": f"{confidence}%",
        "safe_entry": safe
    }
    with open(SIGNAL_FILE, "w") as f:
        json.dump(data, f)
    print("✅ Prediction written:", data)

def on_message(ws, message):
    data = json.loads(message)

    if data.get("msg_type") == "authorize":
        print("✅ Authorized")
        ws.send(json.dumps({
            "ticks": "R_10",
            "subscribe": 1
        }))

    elif data.get("msg_type") == "tick":
        digit = int(str(data["tick"]["quote"])[-1])
        recent_digits.append(digit)
        if len(recent_digits) > 10:
            recent_digits.pop(0)

        prediction, confidence, safe = calculate_prediction()
        save_signal(digit, prediction, confidence, safe)

def on_error(ws, error):
    print("❌ Error:", error)

def on_close(ws, code, msg):
    print("🔁 Closed. Reconnecting in 3s...")
    time.sleep(3)
    run_ws()

def on_open(ws):
    print("🔐 Sending token...")
    ws.send(json.dumps({"authorize": TOKEN}))

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
