from storage.db import SessionLocal
from storage.models import Tick

def get_recent_prices(symbol, limit=700):
    db = SessionLocal()
    rows = (
        db.query(Tick)
        .filter(Tick.symbol == symbol)
        .order_by(Tick.timestamp.desc())
        .limit(limit)
        .all()
    )
    db.close()

    return [
        {"ts": r.timestamp.isoformat(), "price": r.price}
        for r in reversed(rows)
    ]


# utils.py
from storage.db import SessionLocal
from storage.models import Tick, HourlySummary
import pandas as pd
from datetime import datetime
# not used
def compute_hourly_summary(symbol1, symbol2):
    session = SessionLocal()
    
    try:
        # 1. Fetch ticks for both symbols
        ticks1 = session.query(Tick).filter(Tick.symbol==symbol1).all()
        ticks2 = session.query(Tick).filter(Tick.symbol==symbol2).all()
        
        # 2. Convert to DataFrame
        df1 = pd.DataFrame([{"ts": t.timestamp, "price": t.price} for t in ticks1])
        df2 = pd.DataFrame([{"ts": t.timestamp, "price": t.price} for t in ticks2])
        
        if df1.empty or df2.empty:
            return
        
        # 3. Set timestamp as index
        df1.set_index("ts", inplace=True)
        df2.set_index("ts", inplace=True)
        
        # 4. Resample hourly
        df1_hour = df1.resample('1H').agg(['first','max','min','last','mean','std'])
        df2_hour = df2.resample('1H').agg(['first','max','min','last','mean','std'])
        
        # 5. Compute spread and z-score
        df_merge = pd.merge(df1_hour['price']['mean'], df2_hour['price']['mean'], left_index=True, right_index=True, suffixes=('_1','_2'))
        df_merge['spread'] = df_merge['mean_1'] - df_merge['mean_2']
        df_merge['z'] = (df_merge['spread'] - df_merge['spread'].mean()) / df_merge['spread'].std()
        
        # 6. Compute correlation (mean, min, max, std)
        corr_series = df1['price'].rolling(3600).corr(df2['price'])
        
        # 7. Insert/update HourlySummary table
        for ts in df_merge.index:
            summary = HourlySummary(
                ts=ts,
                symbol1=symbol1,
                symbol2=symbol2,
                price_first=df1_hour['price'].loc[ts]['first'],
                price_max=df1_hour['price'].loc[ts]['max'],
                price_min=df1_hour['price'].loc[ts]['min'],
                price_last=df1_hour['price'].loc[ts]['last'],
                price_mean=df1_hour['price'].loc[ts]['mean'],
                price_std=df1_hour['price'].loc[ts]['std'],
                spread_mean=df_merge.loc[ts]['spread'],
                spread_std=df_merge['spread'].std(),
                z_mean=df_merge.loc[ts]['z'],
                z_max=df_merge['z'].max(),
                corr_mean=corr_series.mean(),
                corr_min=corr_series.min(),
                corr_max=corr_series.max(),
                corr_std=corr_series.std()
            )
            session.merge(summary)  # merge updates if already exists

        session.commit()
        
    finally:
        session.close()
