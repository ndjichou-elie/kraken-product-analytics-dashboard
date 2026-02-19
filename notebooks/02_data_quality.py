import pandas as pd

# Load data again (each script must load what it needs)
base_path = "data/"

dim_users = pd.read_csv(base_path + "dim_users.csv")
fact_sessions = pd.read_csv(base_path + "fact_sessions.csv")
fact_events = pd.read_csv(base_path + "fact_events.csv")
fact_deposits = pd.read_csv(base_path + "fact_deposits.csv")
fact_trades = pd.read_csv(base_path + "fact_trades.csv")

tables = {
    "dim_users": dim_users,
    "fact_sessions": fact_sessions,
    "fact_events": fact_events,
    "fact_deposits": fact_deposits,
    "fact_trades": fact_trades,
}

print("\n====================")
print("STEP 2: DATA QUALITY")
print("====================\n")

# 1) Missing values
print("1) Missing values")
for name, df in tables.items():
    nulls = df.isna().sum()
    nulls = nulls[nulls > 0]
    print(f"\n{name}:")
    if len(nulls) == 0:
        print("  ✅ No missing values")
    else:
        print(nulls)

# 2) Primary key uniqueness
print("\n2) Primary key uniqueness checks")
pk_checks = {
    "dim_users.user_id": ("dim_users", "user_id"),
    "fact_sessions.session_id": ("fact_sessions", "session_id"),
    "fact_events.event_id": ("fact_events", "event_id"),
    "fact_deposits.deposit_id": ("fact_deposits", "deposit_id"),
    "fact_trades.trade_id": ("fact_trades", "trade_id"),
}

for label, (tname, col) in pk_checks.items():
    df = tables[tname]
    dupes = df[col].duplicated().sum()
    print(f"{label}: duplicated keys = {dupes}")

# 3) Foreign key checks
print("\n3) Foreign key orphan checks")

user_set = set(dim_users["user_id"].unique())

def orphan_count(df):
    return (~df["user_id"].isin(user_set)).sum()

print("fact_sessions orphan user_id:", orphan_count(fact_sessions))
print("fact_events orphan user_id:", orphan_count(fact_events))
print("fact_deposits orphan user_id:", orphan_count(fact_deposits))
print("fact_trades orphan user_id:", orphan_count(fact_trades))

# 4) Timestamp ranges
print("\n4) Timestamp ranges")

dim_users["created_at"] = pd.to_datetime(dim_users["created_at"], errors="coerce")
fact_sessions["session_start_ts"] = pd.to_datetime(fact_sessions["session_start_ts"], errors="coerce")
fact_events["event_ts"] = pd.to_datetime(fact_events["event_ts"], errors="coerce")
fact_deposits["deposit_ts"] = pd.to_datetime(fact_deposits["deposit_ts"], errors="coerce")
fact_trades["trade_ts"] = pd.to_datetime(fact_trades["trade_ts"], errors="coerce")

print("created_at:", dim_users["created_at"].min(), "->", dim_users["created_at"].max())
print("session_start_ts:", fact_sessions["session_start_ts"].min(), "->", fact_sessions["session_start_ts"].max())
print("event_ts:", fact_events["event_ts"].min(), "->", fact_events["event_ts"].max())
print("deposit_ts:", fact_deposits["deposit_ts"].min(), "->", fact_deposits["deposit_ts"].max())
print("trade_ts:", fact_trades["trade_ts"].min(), "->", fact_trades["trade_ts"].max())
