import sqlite3
import pandas as pd

base_path = "data/"
db_path = "analytics.db"

# Load CSVs
dim_users = pd.read_csv(base_path + "dim_users.csv")
fact_sessions = pd.read_csv(base_path + "fact_sessions.csv")
fact_events = pd.read_csv(base_path + "fact_events.csv")
fact_deposits = pd.read_csv(base_path + "fact_deposits.csv")
fact_trades = pd.read_csv(base_path + "fact_trades.csv")

# Connect to SQLite (this creates analytics.db in your project folder)
conn = sqlite3.connect(db_path)

# Load tables into SQL
dim_users.to_sql("dim_users", conn, if_exists="replace", index=False)
fact_sessions.to_sql("fact_sessions", conn, if_exists="replace", index=False)
fact_events.to_sql("fact_events", conn, if_exists="replace", index=False)
fact_deposits.to_sql("fact_deposits", conn, if_exists="replace", index=False)
fact_trades.to_sql("fact_trades", conn, if_exists="replace", index=False)

print("✅ Loaded tables into analytics.db")

# DAU query
dau = pd.read_sql_query("""
SELECT 
    DATE(event_ts) AS event_date,
    COUNT(DISTINCT user_id) AS dau
FROM fact_events
GROUP BY DATE(event_ts)
ORDER BY event_date
""", conn)

print("\nDAU sample:")
print(dau.head(10))

# Save output for dashboard usage
dau.to_csv("outputs/dau.csv", index=False)
print("\n✅ Saved outputs/dau.csv")
