import sqlite3
import pandas as pd

# Connect to your simulated Kraken database
conn = sqlite3.connect("analytics.db")

query = """
SELECT 
    u.acquisition_channel,
    COUNT(DISTINCT u.user_id) AS total_users,
    COUNT(DISTINCT f.user_id) AS traders,
    COALESCE(SUM(f.fee_usd), 0) AS total_fees,
    ROUND(COALESCE(SUM(f.fee_usd), 0) / COUNT(DISTINCT u.user_id), 2) AS arpu,
    ROUND(COALESCE(SUM(f.fee_usd), 0) / NULLIF(COUNT(DISTINCT f.user_id), 0), 2) AS arpt
FROM dim_users u
LEFT JOIN fact_trades f 
    ON u.user_id = f.user_id
GROUP BY 1
ORDER BY total_fees DESC;
"""


# Execute and load into Pandas
df_arpu = pd.read_sql_query(query, conn)

# Alternatively, compute ARPU in Pandas (often preferred for complex formatting)
df_arpu["arpu"] = (df_arpu["total_fees"] / df_arpu["total_users"]).round(2)

# Handle potential NaN values (channels with 0 users or 0 trades)
df_arpu = df_arpu.fillna(0)

print("--- Channel Revenue & ARPU Analysis ---")
print(df_arpu)