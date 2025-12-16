import pandas as pd
import numpy as np
from storage.utils import get_recent_prices

def alerts_v2(s1, s2, limit=1000, z_threshold=2.0, timeframe="1s"):
    df1 = pd.DataFrame(get_recent_prices(s1, limit), columns=["ts", "price"])
    df2 = pd.DataFrame(get_recent_prices(s2, limit), columns=["ts", "price"])

    if df1.empty or df2.empty:
        return []

    for df in (df1, df2):
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df.dropna(inplace=True)
        df = df[df.price > 0]

    df1 = df1.set_index("ts").resample(timeframe).mean()
    df2 = df2.set_index("ts").resample(timeframe).mean()

    df = df1.join(df2, lsuffix="_1", rsuffix="_2").dropna()
    if len(df) < 5:
        return []

    df["spread"] = df["price_1"] - df["price_2"]
    std = df["spread"].std()

    if std == 0 or np.isnan(std):
        return []

    df["zscore"] = (df["spread"] - df["spread"].mean()) / std

    alerts = df[np.abs(df["zscore"]) >= z_threshold]
    print("Alertsokok",alerts)
    return [
        {
            "ts": ts.isoformat(),
            "spread": float(row.spread),
            "zscore": float(row.zscore),
        }
        for ts, row in alerts.iterrows()
    ]
