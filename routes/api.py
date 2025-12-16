from flask import Blueprint, jsonify, request
import csv
from io import StringIO
from flask import Response
from analytics.price import get_recent_prices
from analytics.spread import spread_and_zscore
from analytics.correlation import rolling_correlation
from analytics.stats import summary_stats
from analytics.alerts_v2 import alerts_v2
from analytics.price_v2 import price_series_v2
from storage.utils import compute_hourly_summary


api = Blueprint("api", __name__)

@api.route("/api/prices")
def prices():
    symbol = request.args.get("symbol", "btcusdt")
    return jsonify(get_recent_prices(symbol))


@api.route("/api/spread")
def spread():
    try:
        s1 = request.args.get("s1")
        s2 = request.args.get("s2")
        return jsonify(spread_and_zscore(s1, s2))
    except Exception as e:
        print("ERROR in spread:", e)
        return jsonify([])

@api.route("/api/correlation")
def correlation():
    try:
        s1 = request.args.get("s1")
        s2 = request.args.get("s2")
        return jsonify(rolling_correlation(s1, s2))
    except Exception as e:
        print("ERROR in correlation:", e)
        return jsonify([])


@api.route("/api/stats")
def stats():
    symbol = request.args.get("symbol", "btcusdt")
    return jsonify(summary_stats(symbol))


@api.route("/api/prices_v2")
def prices_v2():
    symbol = request.args.get("symbol", "btcusdt")
    tf = request.args.get("tf", "1S")

    try:
        return jsonify(price_series_v2(symbol, timeframe=tf))
    except Exception as e:
        print("ERROR in prices_v2:", e)
        return jsonify([])


@api.route("/api/alerts_v2")
def alerts_v2_route():
    s1 = request.args.get("s1")
    s2 = request.args.get("s2")
    tf = request.args.get("tf", "1S")
    z = float(request.args.get("z", 2.0))

    try:
        return jsonify(alerts_v2(s1, s2, z_threshold=z, timeframe=tf))
    except Exception as e:
        print("ERROR in alerts_v2:", e)
        return jsonify([])


@api.route("/api/export/price")
def export_price():
    symbol = request.args.get("symbol", "btcusdt")
    data = get_recent_prices(symbol)

    if not data:
        return Response("No data", status=400)

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "price"])

    for row in data:
        writer.writerow([row["ts"], row["price"]])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={symbol}_price.csv"
        }
    )


@api.route("/api/export/spread")
def export_spread():
    s1 = request.args.get("s1")
    s2 = request.args.get("s2")

    data = spread_and_zscore(s1, s2)

    if not data:
        return Response("No data", status=400)

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "spread", "zscore"])

    for row in data:
        writer.writerow([row["ts"], row["spread"], row["zscore"]])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={s1}_{s2}_spread.csv"
        }
    )


@api.route("/api/export/correlation")
def export_correlation():
    s1 = request.args.get("s1")
    s2 = request.args.get("s2")

    data = rolling_correlation(s1, s2)

    if not data:
        return Response("No data", status=400)

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "correlation"])

    for row in data:
        writer.writerow([row["ts"], row["corr"]])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={s1}_{s2}_correlation.csv"
        }
    )


# @api.route("/api/export/hourly_summary")
# def export_hourly_summary():
#     s1 = request.args.get("s1", "btcusdt")
#     s2 = request.args.get("s2", "ethusdt")

#     # Fetch analytics
#     price1 = get_recent_prices(s1)
#     price2 = get_recent_prices(s2)
#     spread = spread_and_zscore(s1, s2)
#     corr = rolling_correlation(s1, s2)

#     if not price1 or not price2:
#         return Response("No data", status=400)

#     import pandas as pd
#     import csv
#     from io import StringIO

#     # ---------------- PRICE ----------------
#     df_p1 = pd.DataFrame(price1)
#     df_p1["ts"] = pd.to_datetime(df_p1["ts"])
#     df_p1.set_index("ts", inplace=True)
#     print("DATA RANGE:", df_p1.index.min(), "→", df_p1.index.max())

#     price_hourly = df_p1["price"].resample("1H").agg(
#         ["first", "max", "min", "last", "mean", "std"]
#     ).dropna()

#     # ---------------- SPREAD ----------------
#     df_s = pd.DataFrame(spread)
#     if not df_s.empty:
#         df_s["ts"] = pd.to_datetime(df_s["ts"])
#         df_s.set_index("ts", inplace=True)

#         spread_hourly = df_s.resample("1H").agg(
#             spread_mean=("spread", "mean"),
#             spread_std=("spread", "std"),
#             z_mean=("zscore", "mean"),
#             z_max=("zscore", "max")
#         )
#     else:
#         spread_hourly = pd.DataFrame()

#     # ---------------- CORRELATION ----------------
#     df_c = pd.DataFrame(corr)
#     if not df_c.empty:
#         df_c["ts"] = pd.to_datetime(df_c["ts"])
#         df_c.set_index("ts", inplace=True)

#         corr_hourly = df_c["corr"].resample("1H").agg(
#             ["mean", "min", "max", "std"]
#         )
#     else:
#         corr_hourly = pd.DataFrame()

#     # ---------------- EXPORT ----------------
#     output = StringIO()
#     writer = csv.writer(output)

#     writer.writerow(["Hourly Summary"])
#     writer.writerow(["Symbol 1:", s1, "Symbol 2:", s2])
#     writer.writerow([])

#     writer.writerow(["--- PRICE (Hourly) ---"])
#     writer.writerow(price_hourly.reset_index().columns)
#     for row in price_hourly.reset_index().itertuples(index=False):
#         writer.writerow(row)

#     writer.writerow([])
#     writer.writerow(["--- SPREAD (Hourly) ---"])
#     if not spread_hourly.empty:
#         writer.writerow(spread_hourly.reset_index().columns)
#         for row in spread_hourly.reset_index().itertuples(index=False):
#             writer.writerow(row)

#     writer.writerow([])
#     writer.writerow(["--- CORRELATION (Hourly) ---"])
#     if not corr_hourly.empty:
#         writer.writerow(corr_hourly.reset_index().columns)
#         for row in corr_hourly.reset_index().itertuples(index=False):
#             writer.writerow(row)

#     return Response(
#         output.getvalue(),
#         mimetype="text/csv",
#         headers={
#             "Content-Disposition":
#                 f"attachment; filename={s1}_{s2}_hourly_summary.csv"
#         }
#     )


@api.route("/api/admin/schedule", methods=["POST"])
def run_hourly_summary():
    try:
        compute_hourly_summary("btcusdt", "ethusdt")
        return jsonify({"status": "success", "message": "Hourly summary computed"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
