import sqlite3
import pandas as pd

conn = sqlite3.connect("analytics.db")

print("\n==============================")
print("STEP 10 — RETENTION COHORTS")
print("==============================\n")

# 1) User activity by day
activity = pd.read_sql_query("""
SELECT 
    user_id,
    DATE(event_ts) AS active_date
FROM fact_events
GROUP BY 1, 2
""", conn)

# 2) Signup dates
users = pd.read_sql_query("""
SELECT 
    user_id,
    DATE(created_at) AS signup_date
FROM dim_users
""", conn)

# Merge activity with signup
df = users.merge(activity, on="user_id", how="left")

# Convert to datetime
df["signup_date"] = pd.to_datetime(df["signup_date"])
df["active_date"] = pd.to_datetime(df["active_date"])

# Days since signup
df["days_since_signup"] = (df["active_date"] - df["signup_date"]).dt.days

# Keep only valid days
df = df[df["days_since_signup"] >= 0]

# Focus on D1, D7, D30
ret = df[df["days_since_signup"].isin([1, 7, 30])].copy()

# Cohort week = signup week
users["signup_date"] = pd.to_datetime(users["signup_date"])
users["cohort_week"] = users["signup_date"].dt.to_period("W").apply(lambda r: r.start_time)

ret = ret.merge(users[["user_id", "cohort_week"]], on="user_id", how="left")

# Cohort sizes
cohort_sizes = users.groupby("cohort_week")["user_id"].nunique().reset_index(name="cohort_users")

# Retention counts
ret_counts = ret.groupby(["cohort_week", "days_since_signup"])["user_id"].nunique().reset_index(name="retained_users")

# Pivot into cohort table
cohort_table = ret_counts.pivot(
    index="cohort_week",
    columns="days_since_signup",
    values="retained_users"
).fillna(0).reset_index()

# Merge cohort sizes
cohort_table = cohort_table.merge(cohort_sizes, on="cohort_week", how="left")

# Compute retention percentages
for d in [1, 7, 30]:
    if d not in cohort_table.columns:
        cohort_table[d] = 0
    cohort_table[f"D{d}_retention_pct"] = (
        cohort_table[d] * 100 / cohort_table["cohort_users"]
    ).round(2)

# Save output
cohort_table.to_csv("outputs/gold_retention_cohorts.csv", index=False)

print("✅ Saved outputs/gold_retention_cohorts.csv\n")
print(cohort_table.head(5))
