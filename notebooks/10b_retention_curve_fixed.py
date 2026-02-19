import sqlite3
import pandas as pd

conn = sqlite3.connect("analytics.db")

print("\n==============================")
print("STEP 10B — TRUE RETENTION CURVE (FIXED)")
print("==============================\n")

# Activity log
activity = pd.read_sql_query("""
SELECT user_id, DATE(event_ts) AS active_date
FROM fact_events
GROUP BY 1,2
""", conn)

users = pd.read_sql_query("""
SELECT user_id, DATE(created_at) AS signup_date
FROM dim_users
""", conn)

df = users.merge(activity, on="user_id", how="left")

df["signup_date"] = pd.to_datetime(df["signup_date"])
df["active_date"] = pd.to_datetime(df["active_date"])

df["days_since_signup"] = (df["active_date"] - df["signup_date"]).dt.days
df = df[df["days_since_signup"] >= 0]

# ✅ Baseline = users active on Day 0
day0_users = df[df["days_since_signup"] == 0]["user_id"].unique()
baseline = len(day0_users)

print("Activated users (Day 0):", baseline)

# Keep only activated users
df = df[df["user_id"].isin(day0_users)]

# Retention by day (0–30)
retention = (
    df[df["days_since_signup"] <= 30]
    .groupby("days_since_signup")["user_id"]
    .nunique()
    .reset_index()
)

retention["retention_pct"] = (
    retention["user_id"] * 100 / baseline
).round(2)

retention.to_csv("outputs/gold_retention_curve_fixed.csv", index=False)

print("\n✅ Saved outputs/gold_retention_curve_fixed.csv\n")
print(retention.head(10))
