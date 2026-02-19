import pandas as pd

# Dataset folder (you will adjust this path)
base_path = "data/"

# Load raw tables
dim_users = pd.read_csv(base_path + "dim_users.csv")
fact_sessions = pd.read_csv(base_path + "fact_sessions.csv")
fact_events = pd.read_csv(base_path + "fact_events.csv")
fact_deposits = pd.read_csv(base_path + "fact_deposits.csv")
fact_trades = pd.read_csv(base_path + "fact_trades.csv")

# Print shapes (rows, columns)
print("dim_users:", dim_users.shape)
print("fact_sessions:", fact_sessions.shape)
print("fact_events:", fact_events.shape)
print("fact_deposits:", fact_deposits.shape)
print("fact_trades:", fact_trades.shape)

# Preview data
print("\n--- dim_users sample ---")
print(dim_users.head(3))

print("\n--- fact_events sample ---")
print(fact_events.head(3))
