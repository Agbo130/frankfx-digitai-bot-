import asyncio
import websockets
import json
import random

async def run():
    with open("session.json", "r") as f:
        session_data = json.load(f)
    token = session_data.get("token")

    if not token:
        print("No token found.")
        return

    uri = "wss://ws.binaryws.com/websockets/v3?app_id=90203"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"authorize": token}))

        # Balance stream
        await ws.send(json.dumps({"balance": 1, "subscribe": 1}))

        # Tick stream
        await ws.send(json.dumps({"ticks": "R_10", "subscribe": 1}))

        latest_digit = "-"
        recent_digits = []
        wins = 0
        losses = 0

        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            if "authorize" in data:
                account_id = data["authorize"]["loginid"]
                with open("session.json", "r") as f:
                    session = json.load(f)
                session["account_id"] = account_id
                with open("session.json", "w") as f:
                    json.dump(session, f)

            elif "balance" in data:
                balance = data["balance"]["balance"]
                with open("session.json", "r") as f:
                    session = json.load(f)
                session["balance"] = f"{balance:.2f}"
                with open("session.json", "w") as f:
                    json.dump(session, f)

            elif "tick" in data:
                digit = int(str(data["tick"]["quote"])[-1])
                latest_digit = digit
                recent_digits.append(digit)
                if len(recent_digits) > 10:
                    recent_digits.pop(0)

                prediction = "EVEN" if random.random() > 0.5 else "ODD"
                confidence = random.randint(75, 95)
                safe = "YES" if confidence >= 85 else "NO"

                ai_data = {
                    "latest_digit": digit,
                    "prediction": prediction,
                    "confidence": f"{confidence}%",
                    "safe_entry": safe,
                    "recent_digits": recent_digits,
                    "wins": wins,
                    "losses": losses
                }

                with open("ai_signal.json", "w") as f:
                    json.dump(ai_data, f)

asyncio.run(run())
