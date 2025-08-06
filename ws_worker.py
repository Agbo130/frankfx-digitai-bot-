import websocket
import json
import time
import random
import threading

SESSION_FILE = "session.json"
AI_SIGNAL_FILE = "ai_signal.json"

def read_session_token():
    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
            return data.get("token", "")
    except:
        return ""

def update_session(data):
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass

def update_ai_signal(latest_digit, prediction, confidence, safe_entry):
    try:
        with open(AI_SIGNAL_FILE, "w") as f:
            json.dump({
                "latest_digit": str(latest_digit),
                "prediction": prediction,
                "confidence": f"{confidence}%",
                "safe_entry": "YES" if safe_entry else "NO"
            }, f)
    except:
        pass

def generate_prediction(recent_digits):
    if not recent_digits:
        return "-", 0, False

    odd_count = sum(1 for d in recent_digits if d % 2 == 1)
    even_count = len(recent_digits) - odd_count

    prediction = "ODD" if odd_count > even_count else "EVEN"
    confidence = int((max(odd_count, even_count) / len(recent_digits)) * 100)
    safe_entry = confidence >= 70

    return prediction, confidence, safe_entry

def on_message(ws, message):
    data = json.loads(message)

    if "msg_type" in data:
        if data["msg_type"] == "authorize":
            account_id = data["authorize"]["loginid"]
            balance = data["authorize"]["balance"]
            update_session({
                "account_id": account_id,
                "balance": f"{balance:.2f}"
            })

        elif data["msg_type"] == "tick":
            digit = int(str(data["tick"]["quote"])[-1])
            ws.recent_digits.append(digit)
            if len(ws.recent_digits) > 20:
                ws.recent_digits.pop(0)

            prediction, confidence, safe_entry = generate_prediction(ws.recent_digits)
            update_ai_signal(digit, prediction, confidence, safe_entry)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws):
    print("WebSocket closed. Reconnecting...")
    time.sleep(3)
    start_websocket()  # Restart loop

def on_open(ws):
    token = read_session_token()
    if token:
        ws.send(json.dumps({"authorize": token}))
        ws.send(json.dumps({"ticks": "R_10"}))
        ws.recent_digits = []
    else:
        print("Token missing.")
        ws.close()

def start_websocket():
    ws = websocket.WebSocketApp("wss://ws.derivws.com/websockets/v3",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                on_open=on_open)
    ws.run_forever()

if __name__ == "__main__":
    start_websocket()
