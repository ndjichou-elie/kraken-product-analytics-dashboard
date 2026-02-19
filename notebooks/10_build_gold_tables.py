import sqlite3
import pandas as pd

conn = sqlite3.connect("analytics.db")

# ---------- GOLD 1: Daily KPIs ----------
daily = pd.read_sql_query("""
WITH daily_events AS (
  SELECT DATE(event_ts) AS dt,
         COUNT(DISTINCT user_id) AS dau
  FROM fact_events
  GROUP BY 1
),
daily_deposits AS (
  SELECT DATE(deposit_ts) AS dt,
         COUNT(DISTINCT user_id) AS deposit_users,
         COUNT(*) AS deposits,
         SUM(amount) AS deposit_amount
  FROM fact_deposits
  GROUP BY 1
),
daily_trades AS (
  SELECT DATE(trade_ts) AS dt,
         COUNT(DISTINCT user_id) AS trade_users,
         COUNT(*) AS trades,
         SUM(notional_usd) AS trade_notional_usd,
         SUM(fee_usd) AS fees_usd
  FROM fact_trades
  GROUP BY 1
)
SELECT e.dt,
       e.dau,
       COALESCE(d.deposit_users, 0) AS deposit_users,
       COALESCE(d.deposits, 0) AS deposits,
       COALESCE(d.deposit_amount, 0) AS deposit_amount,
       COALESCE(t.trade_users, 0) AS trade_users,
       COALESCE(t.trades, 0) AS trades,
       COALESCE(t.trade_notional_usd, 0) AS trade_notional_usd,
       COALESCE(t.fees_usd, 0) AS fees_usd
FROM daily_events e
LEFT JOIN daily_deposits d USING(dt)
LEFT JOIN daily_trades t USING(dt)
ORDER BY e.dt;
""", conn)

daily["trades_per_dau"] = (daily["trades"] / daily["dau"]).replace([float("inf")], 0).fillna(0).round(4)
daily["deposit_users_per_dau"] = (daily["deposit_users"] / daily["dau"]).replace([float("inf")], 0).fillna(0).round(4)

daily.to_csv("outputs/gold_daily_kpis.csv", index=False)
print("✅ Saved outputs/gold_daily_kpis.csv")

# ---------- GOLD 2: Funnel KPIs ----------
funnel = pd.read_sql_query("""
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
  COUNT(*) AS total_users,
  SUM(CASE WHEN d.first_deposit_ts IS NOT NULL
            AND DATE(d.first_deposit_ts) >= DATE(u.created_at)
            AND DATE(d.first_deposit_ts) <= DATE(u.created_at, '+7 day')
      THEN 1 ELSE 0 END) AS deposit_within_7d,
  SUM(CASE WHEN t.first_trade_ts IS NOT NULL
            AND DATE(t.first_trade_ts) >= DATE(u.created_at)
            AND DATE(t.first_trade_ts) <= DATE(u.created_at, '+7 day')
      THEN 1 ELSE 0 END) AS trade_within_7d
FROM dim_users u
LEFT JOIN first_deposit d ON u.user_id = d.user_id
LEFT JOIN first_trade t ON u.user_id = t.user_id;
""", conn)

funnel["deposit_conv_7d_pct"] = (funnel["deposit_within_7d"] * 100 / funnel["total_users"]).round(2)
funnel["trade_conv_7d_pct"] = (funnel["trade_within_7d"] * 100 / funnel["total_users"]).round(2)
funnel["deposit_to_trade_pct"] = (funnel["trade_within_7d"] * 100 / funnel["deposit_within_7d"]).replace([float("inf")], 0).round(2)

funnel.to_csv("outputs/gold_funnel_kpis.csv", index=False)
print("✅ Saved outputs/gold_funnel_kpis.csv")

# ---------- GOLD 3: Channel KPIs ----------
channel = pd.read_sql_query("""
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
  COUNT(DISTINCT u.user_id) AS total_users,
  SUM(CASE WHEN d.first_deposit_ts IS NOT NULL
            AND DATE(d.first_deposit_ts) >= DATE(u.created_at)
            AND DATE(d.first_deposit_ts) <= DATE(u.created_at, '+7 day')
      THEN 1 ELSE 0 END) AS deposit_within_7d,
  SUM(CASE WHEN t.first_trade_ts IS NOT NULL
            AND DATE(t.first_trade_ts) >= DATE(u.created_at)
            AND DATE(t.first_trade_ts) <= DATE(u.created_at, '+7 day')
      THEN 1 ELSE 0 END) AS trade_within_7d
FROM dim_users u
LEFT JOIN first_deposit d ON u.user_id = d.user_id
LEFT JOIN first_trade t ON u.user_id = t.user_id
GROUP BY 1;
""", conn)

channel["deposit_conv_7d_pct"] = (channel["deposit_within_7d"] * 100 / channel["total_users"]).round(2)
channel["trade_conv_7d_pct"] = (channel["trade_within_7d"] * 100 / channel["total_users"]).round(2)
channel["deposit_to_trade_pct"] = (channel["trade_within_7d"] * 100 / channel["deposit_within_7d"]).replace([float("inf")], 0).round(2)

# join revenue
rev = pd.read_sql_query("""
SELECT u.acquisition_channel,
       COALESCE(SUM(t.fee_usd),0) AS total_fees,
       COUNT(DISTINCT t.user_id) AS traders
FROM dim_users u
LEFT JOIN fact_trades t ON u.user_id = t.user_id
GROUP BY 1;
""", conn)

channel = channel.merge(rev, on="acquisition_channel", how="left").fillna(0)
channel["arpu"] = (channel["total_fees"] / channel["total_users"]).replace([float("inf")], 0).fillna(0).round(4)
channel["arpt"] = (channel["total_fees"] / channel["traders"]).replace([float("inf")], 0).fillna(0).round(4)

channel = channel.sort_values("total_fees", ascending=False)
channel.to_csv("outputs/gold_channel_kpis.csv", index=False)
print("✅ Saved outputs/gold_channel_kpis.csv")

# ---------- GOLD 4: A/B deposit summary (reuse existing funnel table if present) ----------
# We'll rebuild quickly from scratch for reproducibility (random assignment).
import numpy as np
np.random.seed(42)

users = pd.read_sql_query("SELECT user_id, created_at FROM dim_users;", conn)

first_deposit = pd.read_sql_query("""
SELECT user_id, MIN(deposit_ts) AS first_deposit_ts
FROM fact_deposits
GROUP BY 1;
""", conn)

ab = users.merge(first_deposit, on="user_id", how="left")
ab["variant"] = np.where(np.random.rand(len(ab)) < 0.5, "control", "treatment")

ab["deposited_within_7d"] = (
    ab["first_deposit_ts"].notna() &
    (pd.to_datetime(ab["first_deposit_ts"]) >= pd.to_datetime(ab["created_at"])) &
    (pd.to_datetime(ab["first_deposit_ts"]) <= pd.to_datetime(ab["created_at"]) + pd.Timedelta(days=7))
).astype(int)

ab_summary = ab.groupby("variant")["deposited_within_7d"].agg(users="count", converters="sum").reset_index()
ab_summary["conversion_rate_pct"] = (ab_summary["converters"] * 100 / ab_summary["users"]).round(4)

ab_summary.to_csv("outputs/gold_ab_deposit.csv", index=False)
print("✅ Saved outputs/gold_ab_deposit.csv")

print("\nPreview:")
print(daily.head(3))
print(channel.head(3))
print(funnel)
print(ab_summary)
