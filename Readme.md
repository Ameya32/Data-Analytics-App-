Sure! Here’s the revised version with example routes included:

---

This project collects real-time Binance tick data for cryptocurrency pairs like BTC/USDT and ETH/USDT, stores it in a SQLite database, and provides analytics through a Flask API. The APIs allow users to fetch recent prices, compute and retrieve spread and z-score between symbol pairs, calculate rolling correlations, generate summary statistics, trigger z-score based alerts, and export price, spread, correlation. An admin endpoint allows computation of hourly summaries that aggregate price, spread, and correlation statistics for easier analysis.

**APIs provided:**

* **GET /api/prices** – Fetch recent prices for a symbol 
* **GET /api/spread** – Get spread and z-score between two symbols 
* **GET /api/correlation** – Calculate rolling correlation between two symbols 
* **GET /api/stats** – Retrieve statistical summaries for a symbol 
* **GET /api/prices_v2** – Get high-resolution price series 
* **GET /api/alerts_v2** – Generate z-score based alerts 
* **GET /api/export/price** – Export recent prices as CSV.
* **GET /api/export/spread** – Export spread and z-score as CSV.(Partial Done)
* **GET /api/export/correlation** – Export correlation as CSV.(Partial Done)
* **POST /api/admin/schedule** – Admin endpoint to compute hourly summaries.


