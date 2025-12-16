import numpy as np
import pandas as pd
import math
from storage.utils import get_recent_prices

def spread_and_zscore(sym1, sym2, window=50):
    # Fetch recent prices
    p1 = [x for x in get_recent_prices(sym1) if x["price"] != 0]
    p2 = [x for x in get_recent_prices(sym2) if x["price"] != 0]

    df1 = pd.DataFrame(p1)
    df2 = pd.DataFrame(p2)

    # Convert timestamps, round to nearest second
    df1['ts'] = pd.to_datetime(df1['ts'], errors='coerce').dt.round('1s')
    df2['ts'] = pd.to_datetime(df2['ts'], errors='coerce').dt.round('1s')

    # Drop any invalid timestamps
    df1 = df1.dropna(subset=['ts'])
    df2 = df2.dropna(subset=['ts'])

    df = pd.merge(df1, df2, on="ts", suffixes=("_1", "_2"))

    if df.empty:
        return []

    hedge_ratio = np.polyfit(df.price_2, df.price_1, 1)[0]
    spread = df.price_1 - hedge_ratio * df.price_2
    z = (spread - spread.rolling(window).mean()) / spread.rolling(window).std()

    # Ensure no Inf or NaN
    result = []
    for ts, s, zv in zip(df.ts, spread, z):
        if not math.isfinite(s):
            s = 0
        if not math.isfinite(zv):
            zv = 0
        result.append({
            "ts": str(ts),
            "spread": float(s),
            "zscore": float(zv)
        })

    return result
