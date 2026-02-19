import sqlite3
import pandas as pd
import numpy as np
import math

conn = sqlite3.connect("analytics.db")

# Load user funnel table
funnel = pd.read_csv("outputs/user_funnel_table_fixed.csv")

# Random experiment assignment
np.random.seed(42)
funnel["variant"] = np.where(np.random.rand(len(funnel)) < 0.5,
                             "control", "treatment")

# Conversion by variant
summary = funnel.groupby("variant")["deposited_within_7d"].agg(
    users="count",
    converters="sum"
).reset_index()

summary["conversion_rate"] = round(
    summary["converters"] / summary["users"] * 100, 2
)


# Extract numbers
c_users = summary.loc[summary["variant"]=="control", "users"].values[0]
c_conv  = summary.loc[summary["variant"]=="control", "converters"].values[0]

t_users = summary.loc[summary["variant"]=="treatment", "users"].values[0]
t_conv  = summary.loc[summary["variant"]=="treatment", "converters"].values[0]

# Conversion rates
p1 = c_conv / c_users
p2 = t_conv / t_users

# Pooled probability
p_pool = (c_conv + t_conv) / (c_users + t_users)

# Standard error
se = math.sqrt(p_pool * (1 - p_pool) * (1/c_users + 1/t_users))

# Z-score
z = (p2 - p1) / se

print("\n--- Statistical Test ---")
print("Control rate:", round(p1*100, 4), "%")
print("Treatment rate:", round(p2*100, 4), "%")
print("Difference:", round((p2-p1)*100, 4), "%")
print("Z-score:", round(z, 4))
print(summary)
