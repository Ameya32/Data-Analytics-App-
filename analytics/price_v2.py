import pandas as pd
from storage.utils import get_recent_prices

def price_series_v2(symbol, limit=1000, timeframe="1s"):
    rows = get_recent_prices(symbol, limit)

    df = pd.DataFrame(rows, columns=["ts", "price"])
    if df.empty:
        return []

    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # some price are 0
    df = df.dropna()
    df = df[df.price > 0]

    if df.empty:
        return []

    df = (
        df.set_index("ts")
        .resample(timeframe)
        .mean()
        .dropna()
        .reset_index()
    )

    return df.to_dict(orient="records")
