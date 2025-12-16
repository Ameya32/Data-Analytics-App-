from flask import Flask, render_template
from storage.db import Base, engine
from routes.api import api
import threading
from ingestion.binance_ws import start_ws

app = Flask(__name__)
app.register_blueprint(api)

Base.metadata.create_all(engine)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    symbols = ["btcusdt", "ethusdt"] 
    for sym in symbols:
        threading.Thread(target=start_ws, args=(sym,), daemon=True).start()
    app.run(debug=True)
