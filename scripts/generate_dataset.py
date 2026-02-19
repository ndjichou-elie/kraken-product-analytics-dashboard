import os
import numpy as np
import pandas as pd

np.random.seed(42)

# ---------- CONFIG ----------
N_USERS = 20000
N_DAYS = 120
START_DATE = pd.Timestamp("2025-10-01")
END_DATE = START_DATE + pd.Timedelta(days=N_DAYS - 1)

OUT_DIR = "data"
os.makedirs(OUT_DIR, exist_ok=True)

countries = ["US","GB","DE","FR","ES","IT","NL","PL","TR","AE","IN","NG","BR","CA","AU","JP","SG","HK","ZA","MX"]
devices = ["web","ios","android","desktop"]
channels = ["organic","paid_search","paid_social","referral","affiliate","partner","email","influencer"]
plans = ["standard","pro"]

# ---------- 1) dim_users ----------
user_id = np.arange(1, N_USERS + 1)

created_day_offset = np.random.randint(0, N_DAYS, size=N_USERS)
created_at = START_DATE + pd.to_timedelta(created_day_offset, unit="D") \
             + pd.to_timedelta(np.random.randint(0, 86400, size=N_USERS), unit="s")

dim_users = pd.DataFrame({
    "user_id": user_id,
    "created_at": created_at,
    "country": np.random.choice(countries, size=N_USERS),
    "device_primary": np.random.choice(devices, size=N_USERS, p=[0.45,0.22,0.25,0.08]),
    "acquisition_channel": np.random.choice(channels, size=N_USERS, p=[0.32,0.17,0.12,0.10,0.08,0.06,0.07,0.08]),
    "plan": np.random.choice(plans, size=N_USERS, p=[0.78,0.22]),
})

# ---------- 2) fact_sessions (sessions ONLY after signup) ----------
# realistic-ish sessions per user
sess_counts = np.clip(np.random.poisson(lam=6, size=N_USERS), 1, 40)
total_sessions = sess_counts.sum()

session_id = np.arange(1, total_sessions + 1)
session_user_id = np.repeat(dim_users["user_id"].values, sess_counts)

created_lookup = dim_users.set_index("user_id")["created_at"]
created_for_session = created_lookup.loc[session_user_id].values.astype("datetime64[ns]")

# session start between created_at and END_DATE (inclusive)
end_np = np.datetime64(END_DATE + pd.Timedelta(days=1))  # exclusive upper
u = np.random.rand(total_sessions)
session_start = created_for_session + (end_np - created_for_session) * u
session_start = pd.to_datetime(session_start)

session_duration_sec = np.clip(np.random.lognormal(mean=6.0, sigma=0.6, size=total_sessions).astype(int), 60, 7200)

fact_sessions = pd.DataFrame({
    "session_id": session_id,
    "user_id": session_user_id,
    "session_start_ts": session_start,
    "session_duration_sec": session_duration_sec
})

# ---------- 3) fact_events (events within sessions) ----------
# We'll create a simple but valid funnel:
# app_open always
# deposit_completed sometimes
# order_filled sometimes (only if deposit_completed happened)

sess_traits = fact_sessions.merge(
    dim_users[["user_id","country","device_primary","acquisition_channel","plan"]],
    on="user_id",
    how="left"
)

n_sess = len(sess_traits)
is_pro = (sess_traits["plan"].values == "pro").astype(int)

# probabilities
p_deposit = np.clip(0.30 + 0.10*is_pro, 0.10, 0.70)
p_trade_after_deposit = np.clip(0.60 + 0.10*is_pro, 0.20, 0.90)

deposit_flag = np.random.rand(n_sess) < p_deposit
trade_flag = deposit_flag & (np.random.rand(n_sess) < p_trade_after_deposit)

def make_events(mask, name, min_offset=5, max_offset=1800):
    idx = np.where(mask)[0]
    base = sess_traits.iloc[idx]
    # offset inside session, ensure >0 and within duration
    offs = np.minimum(
        (min_offset + (np.random.rand(len(idx)) * (max_offset - min_offset))).astype(int),
        base["session_duration_sec"].values - 1
    )
    ts = pd.to_datetime(base["session_start_ts"].values) + pd.to_timedelta(offs, unit="s")
    return pd.DataFrame({
        "user_id": base["user_id"].values,
        "session_id": base["session_id"].values,
        "event_ts": ts,
        "event_name": name,
        "device": base["device_primary"].values,
        "country": base["country"].values,
        "acquisition_channel": base["acquisition_channel"].values
    })

# app_open for all sessions at offset 0-10s
app_open = make_events(np.ones(n_sess, dtype=bool), "app_open", min_offset=0, max_offset=10)
deposit_completed = make_events(deposit_flag, "deposit_completed", min_offset=20, max_offset=900)
order_filled = make_events(trade_flag, "order_filled", min_offset=60, max_offset=1800)

fact_events = pd.concat([app_open, deposit_completed, order_filled], ignore_index=True)
fact_events = fact_events.sort_values(["session_id","event_ts"]).reset_index(drop=True)
fact_events.insert(0, "event_id", np.arange(1, len(fact_events) + 1))

# ---------- 4) fact_deposits (derived from deposit_completed events) ----------
de = fact_events[fact_events["event_name"]=="deposit_completed"].copy()
fact_deposits = pd.DataFrame({
    "deposit_id": np.arange(1, len(de)+1),
    "deposit_ts": de["event_ts"].values,
    "user_id": de["user_id"].values,
    "session_id": de["session_id"].values,
    "amount": np.round(np.random.lognormal(mean=5.2, sigma=1.0, size=len(de)), 2)
})

# ---------- 5) fact_trades (derived from order_filled events) ----------
te = fact_events[fact_events["event_name"]=="order_filled"].copy()
notional = np.round(np.random.lognormal(mean=4.9, sigma=1.1, size=len(te)), 2)
fee = np.round(notional * np.where(is_pro.mean() > 0.2, 0.0018, 0.0022), 4)

fact_trades = pd.DataFrame({
    "trade_id": np.arange(1, len(te)+1),
    "trade_ts": te["event_ts"].values,
    "user_id": te["user_id"].values,
    "session_id": te["session_id"].values,
    "notional_usd": notional,
    "fee_usd": fee
})

# ---------- SAVE ----------
dim_users.to_csv(os.path.join(OUT_DIR, "dim_users.csv"), index=False)
fact_sessions.to_csv(os.path.join(OUT_DIR, "fact_sessions.csv"), index=False)
fact_events.to_csv(os.path.join(OUT_DIR, "fact_events.csv"), index=False)
fact_deposits.to_csv(os.path.join(OUT_DIR, "fact_deposits.csv"), index=False)
fact_trades.to_csv(os.path.join(OUT_DIR, "fact_trades.csv"), index=False)

print("✅ Regenerated dataset saved to /data")
print("Rows:")
print("dim_users:", dim_users.shape)
print("fact_sessions:", fact_sessions.shape)
print("fact_events:", fact_events.shape)
print("fact_deposits:", fact_deposits.shape)
print("fact_trades:", fact_trades.shape)

# Quick sanity check: deposits/trades after signup
merged = dim_users[["user_id","created_at"]].merge(
    fact_deposits.groupby("user_id")["deposit_ts"].min().reset_index(),
    on="user_id",
    how="left"
)
bad = (pd.to_datetime(merged["deposit_ts"]) < pd.to_datetime(merged["created_at"])).sum()
print("Sanity check - deposits before signup:", bad)
