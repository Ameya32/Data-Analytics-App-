import pandas as pd
from storage.utils import get_recent_prices

def summary_stats(symbol):
    prices = get_recent_prices(symbol)
    df = pd.DataFrame(prices)

    df = df[df.price > 0]

    if df.empty:
        return {"error": "No valid data for this symbol"}

    returns = df.price.pct_change().dropna()

    return {
        "mean_price": df.price.mean(),
        "std_price": df.price.std(),
        "min_price": df.price.min(),
        "max_price": df.price.max(),
        "volatility": returns.std()
    }
