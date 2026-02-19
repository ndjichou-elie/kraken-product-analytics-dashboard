import sqlite3
import pandas as pd

conn = sqlite3.connect("analytics.db")

query = """
WITH first_deposit AS (
    SELECT user_id, MIN(deposit_ts) AS first_deposit_ts
    FROM fact_deposits
    GROUP BY user_id
)

SELECT 
    u.acquisition_channel,
    COUNT(*) AS total_users,

    SUM(
        CASE 
            WHEN d.first_deposit_ts IS NOT NULL
             AND DATE(d.first_deposit_ts) >= DATE(u.created_at)
             AND DATE(d.first_deposit_ts) <= DATE(u.created_at, '+7 day')
            THEN 1 ELSE 0
        END
    ) AS deposit_within_7d

FROM dim_users u
LEFT JOIN first_deposit d ON u.user_id = d.user_id
GROUP BY u.acquisition_channel
ORDER BY deposit_within_7d DESC
"""

df = pd.read_sql_query(query, conn)

df["deposit_conversion_pct"] = round(
    df["deposit_within_7d"] * 100.0 / df["total_users"], 2
)

print(df)
