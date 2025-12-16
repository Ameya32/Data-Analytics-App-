from sqlalchemy.orm import Session
from storage.db import SessionLocal
from storage.models import Tick, HourlySummary
import pandas as pd
from datetime import datetime, timedelta
#for now we can use admin api to call this function
def compute_hourly_summary(symbol1: str, symbol2: str):
    """
    Compute hourly summary for two symbols and store it in HourlySummary table.
    """
    db: Session = SessionLocal()
    
    try:
        # 1. Fetch all relevant tick data for last 24 hours
        now = datetime.utcnow()
        start_time = now - timedelta(hours=24)

        ticks1 = db.query(Tick).filter(Tick.symbol == symbol1, Tick.timestamp >= start_time).all()
        ticks2 = db.query(Tick).filter(Tick.symbol == symbol2, Tick.timestamp >= start_time).all()

        if not ticks1 or not ticks2:
            print("No data found for the given symbols")
            return

        # 2. Convert to DataFrames
        df1 = pd.DataFrame([{"ts": t.timestamp, "price": t.price} for t in ticks1])
        df2 = pd.DataFrame([{"ts": t.timestamp, "price": t.price} for t in ticks2])

        df1.set_index("ts", inplace=True)
        df2.set_index("ts", inplace=True)

        # Resample hourly
        df1_hourly = df1.resample("1H").agg(["first", "max", "min", "last", "mean", "std"])
        df2_hourly = df2.resample("1H").agg(["first", "max", "min", "last", "mean", "std"])

        # Merge to compute spread and correlation
        df = pd.merge(df1["price"], df2["price"], left_index=True, right_index=True, suffixes=("_1", "_2"))
        df = df.resample("1H").agg(["mean", "std"])

        # Loop through each hour
        for hour_ts in df1_hourly.index:
            # Price stats
            p_stats = df1_hourly.loc[hour_ts]
            q_stats = df2_hourly.loc[hour_ts]

            # Spread stats
            spread_series = df1["price"].resample("1H").mean() - df2["price"].resample("1H").mean()
            z_series = (df1["price"] - df2["price"]).resample("1H").mean()  # simple z-like metric

            # Correlation stats
            corr_series = df1["price"].resample("1H").corr(df2["price"])

            summary = HourlySummary(
                ts=hour_ts,
                symbol1=symbol1,
                symbol2=symbol2,
                
                # Price stats for symbol1
                price_first=p_stats["first"],
                price_max=p_stats["max"],
                price_min=p_stats["min"],
                price_last=p_stats["last"],
                price_mean=p_stats["mean"],
                price_std=p_stats["std"],

                # Spread stats
                spread_mean=spread_series.get(hour_ts, None),
                spread_std=z_series.get(hour_ts, None),
                z_mean=z_series.get(hour_ts, None),
                z_max=z_series.get(hour_ts, None),

                # Correlation stats
                corr_mean=corr_series if corr_series is not None else None,
                corr_min=corr_series if corr_series is not None else None,
                corr_max=corr_series if corr_series is not None else None,
                corr_std=0  # optional, compute if you want
            )

            db.merge(summary)  # merge will insert or update if primary key exists

        db.commit()
        print(f"Hourly summary saved for {symbol1} & {symbol2}")

    except Exception as e:
        db.rollback()
        print("Error computing hourly summary:", e)

    finally:
        db.close()
