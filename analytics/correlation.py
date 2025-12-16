import pandas as pd
import math
from storage.utils import get_recent_prices


def rolling_correlation(sym1, sym2, window=300, freq="1s"):
    """
    Computes rolling correlation between two symbols after
    time alignment using resampling + forward fill.

    Args:
        sym1, sym2 : trading symbols
        window     : rolling window size (default = 300 seconds)
        freq       : resample frequency ("1s", "1min", etc.)

    Returns:
        List of dicts: [{ "ts": timestamp, "corr": value }]
    """

    # ---------------- 1. Fetch & clean data ----------------
    p1 = [x for x in get_recent_prices(sym1) if x["price"] > 0]
    p2 = [x for x in get_recent_prices(sym2) if x["price"] > 0]

    if not p1 or not p2:
        return []

    df1 = pd.DataFrame(p1)
    df2 = pd.DataFrame(p2)

    # ---------------- 2. Timestamp handling ----------------
    df1["ts"] = pd.to_datetime(df1["ts"], errors="coerce")
    df2["ts"] = pd.to_datetime(df2["ts"], errors="coerce")

    df1.dropna(subset=["ts"], inplace=True)
    df2.dropna(subset=["ts"], inplace=True)

    df1.set_index("ts", inplace=True)
    df2.set_index("ts", inplace=True)

    # ---------------- 3. Resample & forward-fill ----------------
    # Align both symbols on a uniform time grid
    df1 = df1.resample(freq).last().ffill()
    df2 = df2.resample(freq).last().ffill()

    # ---------------- 4. Merge aligned data ----------------
    df = pd.merge(
        df1,
        df2,
        left_index=True,
        right_index=True,
        suffixes=("_1", "_2")
    ).dropna()

    if len(df) < window:
        return []

    # ---------------- 5. Rolling correlation ----------------
    corr_series = df["price_1"].rolling(window).corr(df["price_2"])

    # ---------------- 6. Safe JSON output ----------------
    result = []
    for ts, c in corr_series.items():
        if c is None or not math.isfinite(c):
            continue  # skip NaN / inf safely

        result.append({
            "ts": ts.isoformat(),
            "corr": round(float(c), 6)
        })

    return result
