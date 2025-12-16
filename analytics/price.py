from storage.utils import get_recent_prices

def price_series(symbol, limit=500):
    prices = get_recent_prices(symbol, limit)
    print(f"DEBUG {symbol}: returned {len(prices)} non-zero points")
    return [p for p in prices if p["price"] != 0]
