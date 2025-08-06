import websocket
import json
import time
import ssl

DERIV_TOKEN = "Ooxgq24HmB3MG2q"  # Replace with your real token
APP_ID = "82752"

# Save session data
def update_session(account_id, balance):
    session = {
        "account_id": account_id,
        "balance": f"{balance:.2f}"
    }
    with open("session.json", "w") as f:
        json.dump(session, f)

# Save AI signal data
def update_ai_signal(latest_digit, prediction, confidence, safe_entry):
    signal = {
        "latest_digit": str(latest_digit),
        "prediction": prediction,
        "confidence": f"{confidence:.0f}%",
        "safe_entry": safe_entry
    }
    with open("ai_signal.json", "w") as f:
        json.dump(signal, f)

def on_open(ws):
    print("✅ Connected to Deriv WebSocket")

    # Authenticate
    auth_msg = {
        "authorize": DERIV_TOKEN
    }
    ws.send(json.dumps(auth_msg))

def on_message(ws, message):
    data = json.loads(message)

    if "msg_type" not in data:
        return

    if data["msg_type"] == "authorize":
        account_id = data["authorize"]["loginid"]
        balance = data["authorize"]["balance"]
        update_session(account_id, balance)

        # Subscribe to ticks
        tick_msg = {
            "ticks": "R_10",
            "subscribe": 1
        }
        ws.send(json.dumps(tick_msg))

    elif data["msg_type"] == "tick":
        digit = int(str(data["tick"]["quote"])[-1])
        prediction = "EVEN" if digit % 2 == 0 else "ODD"
        confidence = 90.0  # mock logic for now
        safe_entry = "YES" if digit in [2, 4, 6, 8] else "NO"
        update_ai_signal(digit, prediction, confidence, safe_entry)

def on_error(ws, error):
    print(f"❌ WebSocket error: {error}")

def on_close(ws):
    print("❌ Disconnected")

if __name__ == "__main__":
    while True:
        try:
            ws = websocket.WebSocketApp(
                f"wss://ws.derivws.com/websockets/v3?app_id={APP_ID}",
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        except Exception as e:
            print(f"WebSocket crashed: {e}")
            time.sleep(3)
