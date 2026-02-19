import pandas as pd

print("\n==============================")
print("STEP 13B — EXPERIMENT DURATION")
print("==============================\n")

# Load sample size requirement
ss = pd.read_csv("outputs/gold_ab_sample_size.csv")
total_required = int(ss["total_n"].iloc[0])

# Estimate signup rate from dataset
users = pd.read_csv("data/dim_users.csv")
users["created_at"] = pd.to_datetime(users["created_at"])
users["signup_day"] = users["created_at"].dt.date

daily_signups = users.groupby("signup_day")["user_id"].count()

avg_signups_per_day = daily_signups.mean()

print(f"Average signups per day: {avg_signups_per_day:.2f}")
print(f"Total users required:    {total_required:,}")

# Days needed
days_needed = total_required / avg_signups_per_day

print(f"\nEstimated experiment duration: {days_needed:.1f} days")

print("\nBusiness takeaway:")
print("Small lifts require long experiments unless traffic is very high.")
