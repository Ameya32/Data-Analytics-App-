import json
import websocket
from datetime import datetime
from storage.db import SessionLocal
from storage.models import Tick

def on_message(ws, message):
    data = json.loads(message)
    price = float(data["p"])
    if price==0:
        return
    tick = Tick(
        symbol=data["s"].lower(),
        timestamp=datetime.fromtimestamp(data["T"] / 1000),
        price=float(data["p"]),
        size=float(data["q"])
    )

    db = SessionLocal()
    db.add(tick)
    db.commit()
    db.close()

def start_ws(symbol):
    url = f"wss://fstream.binance.com/ws/{symbol}@trade"
    ws = websocket.WebSocketApp(url, on_message=on_message)
    ws.run_forever()
