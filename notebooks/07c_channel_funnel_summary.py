import sqlite3
import pandas as pd

conn = sqlite3.connect("analytics.db")

query = """
WITH first_deposit AS (
    SELECT user_id, MIN(deposit_ts) AS first_deposit_ts
    FROM fact_deposits
    GROUP BY user_id
),
first_trade AS (
    SELECT user_id, MIN(trade_ts) AS first_trade_ts
    FROM fact_trades
    GROUP BY user_id
)
SELECT
    u.acquisition_channel,
    COUNT(*) AS total_users,

    SUM(CASE
        WHEN d.first_deposit_ts IS NOT NULL
         AND DATE(d.first_deposit_ts) >= DATE(u.created_at)
         AND DATE(d.first_deposit_ts) <= DATE(u.created_at, '+7 day')
        THEN 1 ELSE 0 END
    ) AS deposit_within_7d,

    SUM(CASE
        WHEN t.first_trade_ts IS NOT NULL
         AND DATE(t.first_trade_ts) >= DATE(u.created_at)
         AND DATE(t.first_trade_ts) <= DATE(u.created_at, '+7 day')
        THEN 1 ELSE 0 END
    ) AS trade_within_7d

FROM dim_users u
LEFT JOIN first_deposit d ON u.user_id = d.user_id
LEFT JOIN first_trade t ON u.user_id = t.user_id
GROUP BY 1
ORDER BY total_users DESC;
"""

df = pd.read_sql_query(query, conn)

df["deposit_conv_pct"] = (df["deposit_within_7d"] * 100 / df["total_users"]).round(2)
df["trade_conv_pct"] = (df["trade_within_7d"] * 100 / df["total_users"]).round(2)

# deposit -> trade activation among depositors
df["deposit_to_trade_pct"] = (df["trade_within_7d"] * 100 / df["deposit_within_7d"]).replace([float("inf")], 0).round(2)

print(df)
