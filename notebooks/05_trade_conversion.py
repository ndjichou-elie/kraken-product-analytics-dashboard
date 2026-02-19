import sqlite3
import pandas as pd

conn = sqlite3.connect("analytics.db")

query = """
WITH first_trade AS (
    SELECT 
        user_id,
        MIN(trade_ts) AS first_trade_ts
    FROM fact_trades
    GROUP BY user_id
)

SELECT 
    COUNT(*) AS total_users,

    SUM(
        CASE 
            WHEN first_trade_ts IS NOT NULL
             AND DATE(first_trade_ts) <= DATE(created_at, '+7 day')
            THEN 1 ELSE 0
        END
    ) AS trade_within_7d

FROM dim_users u
LEFT JOIN first_trade t
ON u.user_id = t.user_id;
"""

df = pd.read_sql_query(query, conn)

df["trade_conversion_7d_pct"] = round(
    df["trade_within_7d"] * 100.0 / df["total_users"], 2
)

print(df)
