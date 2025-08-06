import asyncio
import websockets
import json
from datetime import datetime
import random

session_file = "session.json"
ai_signal_file = "ai_signal.json"
trade_file = "trade_request.json"

# Initialize session file if not present
def init_files():
    for file, default in [
        (session_file, {
            "latest_digit": "-",
            "account_id": "-",
            "balance": "0",
            "recent_digits": [],
            "wins": 0,
            "losses": 0
        }),
        (ai_signal_file, {
            "prediction": "-",
            "confidence": "-",
            "safe_entry": "-"
        })
    ]:
        try:
            with open(file, "r") as f:
                json.load(f)
        except:
            with open(file, "w") as f:
                json.dump(default, f)

# Generate fake AI logic (replace this later with real AI model)
def get_ai_prediction(recent_digits):
    if not recent_digits:
        return "-", "-", "-"
    odds = [d for d in recent_digits if d % 2 == 1]
    evens = [d for d in recent_digits if d % 2 == 0]
    prediction = "ODD" if len(odds) > len(evens) else "EVEN"
    confidence = f"{random.randint(75, 95)}%"
    safe_entry = "YES" if len(recent_digits) > 5 else "NO"
    return prediction, confidence, safe_entry

async def run_ws():
    init_files()

    with open("token.txt", "r") as f:
        token = f.read().strip()

    uri = "wss://ws.deriv.com/websockets/v3"

    async with websockets.connect(uri) as ws:
        # Authorize
        await ws.send(json.dumps({"authorize": token}))
        auth_response = json.loads(await ws.recv())
        print("Authorized:", auth_response)

        if "error" in auth_response:
            print("Authorization failed.")
            return

        account_id = auth_response["authorize"]["loginid"]

        # Balance stream
        await ws.send(json.dumps({"balance": 1, "subscribe": 1}))

        # Digit stream
        await ws.send(json.dumps({
            "ticks": "R_10",  # or "1HZ10V" for volatility
            "subscribe": 1
        }))

        recent_digits = []

        while True:
            msg = json.loads(await ws.recv())
            if "tick" in msg:
                digit = int(str(msg["tick"]["quote"])[-1])
                recent_digits.append(digit)
                if len(recent_digits) > 10:
                    recent_digits = recent_digits[-10:]

                prediction, confidence, safe_entry = get_ai_prediction(recent_digits)

                with open(session_file, "r") as f:
                    session = json.load(f)

                session["latest_digit"] = str(digit)
                session["recent_digits"] = recent_digits

                with open(session_file, "w") as f:
                    json.dump(session, f)

                with open(ai_signal_file, "w") as f:
                    json.dump({
                        "prediction": prediction,
                        "confidence": confidence,
                        "safe_entry": safe_entry
                    }, f)

            elif "balance" in msg:
                balance = msg["balance"]["balance"]
                with open(session_file, "r") as f:
                    session = json.load(f)
                session["balance"] = f"{balance / 100:.2f}"
                session["account_id"] = account_id
                with open(session_file, "w") as f:
                    json.dump(session, f)

if __name__ == "__main__":
    asyncio.run(run_ws())
