import websocket
import json
import time

session_path = "session.json"
signal_path = "ai_signal.json"

def write_session(data):
    with open(session_path, "w") as f:
        json.dump(data, f)

def write_signal(data):
    with open(signal_path, "w") as f:
        json.dump(data, f)

def on_open(ws):
    print("WebSocket opened")
    token = open("token.txt").read().strip()
    auth_req = {
        "authorize": token
    }
    ws.send(json.dumps(auth_req))

def on_message(ws, message):
    data = json.loads(message)

    # AUTH RESPONSE
    if "authorize" in data:
        acc_id = data["authorize"]["loginid"]
        balance_req = {"balance": 1, "subscribe": 1}
        tick_req = {"ticks_history": "R_10", "adjust_start_time": 1, "count": 20, "style": "ticks", "subscribe": 1}
        ws.send(json.dumps(balance_req))
        ws.send(json.dumps(tick_req))
        write_session({"account_id": acc_id, "balance": "-", "latest_digit": "-", "prediction": "-", "confidence": "-", "safe_entry": "-", "recent_digits": [], "wins": 0, "losses": 0})

    # BALANCE
    elif "balance" in data:
        with open(session_path, "r") as f:
            sess = json.load(f)
        sess["balance"] = str(data["balance"]["balance"])
        write_session(sess)

    # DIGITS
    elif "history" in data or "tick" in data:
        try:
            digit = int(str(data.get("tick", {}).get("quote", ""))[-1]) if "tick" in data else int(str(data["history"]["prices"][-1])[-1])
        except:
            digit = "-"
        digits = []
        if "tick" in data:
            digits.append(digit)
        else:
            digits = [int(str(p)[-1]) for p in data["history"]["prices"]]

        odd_count = sum(1 for d in digits if d % 2 != 0)
        even_count = len(digits) - odd_count

        prediction = "EVEN" if even_count > odd_count else "ODD"
        confidence = int((max(even_count, odd_count) / len(digits)) * 100)
        safe_entry = "YES" if confidence >= 70 else "NO"

        with open(session_path, "r") as f:
            sess = json.load(f)
        sess["latest_digit"] = digit
        sess["recent_digits"] = digits[-10:]
        write_session(sess)

        write_signal({
            "prediction": prediction,
            "confidence": confidence,
            "safe_entry": safe_entry
        })

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def run_ws():
    while True:
        try:
            ws = websocket.WebSocketApp("wss://ws.binaryws.com/websockets/v3?app_id=90203",
                                        on_open=on_open,
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close)
            ws.run_forever()
        except:
            time.sleep(5)

if __name__ == "__main__":
    run_ws()
