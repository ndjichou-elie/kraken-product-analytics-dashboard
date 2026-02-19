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
    u.user_id,
    u.created_at,
    d.first_deposit_ts,
    t.first_trade_ts,

    CASE 
        WHEN d.first_deposit_ts IS NOT NULL
         AND DATE(d.first_deposit_ts) <= DATE(u.created_at, '+7 day')
        THEN 1 ELSE 0
    END AS deposited_within_7d,

    CASE 
        WHEN t.first_trade_ts IS NOT NULL
         AND DATE(t.first_trade_ts) <= DATE(u.created_at, '+7 day')
        THEN 1 ELSE 0
    END AS traded_within_7d

FROM dim_users u
LEFT JOIN first_deposit d ON u.user_id = d.user_id
LEFT JOIN first_trade t ON u.user_id = t.user_id
"""

funnel = pd.read_sql_query(query, conn)

print(funnel.head())

funnel.to_csv("outputs/user_funnel_table.csv", index=False)

print("\n✅ Saved outputs/user_funnel_table.csv")
