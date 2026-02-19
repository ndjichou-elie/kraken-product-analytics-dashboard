import pandas as pd
import math

print("\n==============================")
print("STEP 13 — SAMPLE SIZE / POWER")
print("==============================\n")

ab = pd.read_csv("outputs/gold_ab_deposit.csv")

control = ab[ab["variant"] == "control"].iloc[0]
p1 = control["converters"] / control["users"]   # baseline rate

# Target: +1 percentage point lift
p2 = p1 + 0.01

# Z values for 95% confidence and 80% power
z_alpha = 1.96
z_beta = 0.84

# Pooled variance approximation
p_bar = (p1 + p2) / 2

# Sample size per group formula for 2-proportion test (approx)
numerator = (z_alpha * math.sqrt(2 * p_bar * (1 - p_bar)) + z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
denominator = (p2 - p1) ** 2

n_per_group = math.ceil(numerator / denominator)

print(f"Baseline conversion (p1): {p1:.4f} ({p1*100:.2f}%)")
print(f"Target conversion (p2):   {p2:.4f} ({p2*100:.2f}%)")
print(f"Absolute lift:            {(p2-p1)*100:.2f} pp")
print(f"\nRequired sample size per group (≈): {n_per_group:,}")
print(f"Total sample size (2 groups):       {2*n_per_group:,}")

# Save a small report
out = pd.DataFrame([{
    "baseline_p1": round(p1, 6),
    "target_p2": round(p2, 6),
    "absolute_lift_pp": round((p2 - p1) * 100, 3),
    "n_per_group": n_per_group,
    "total_n": 2 * n_per_group,
    "confidence_level": "95%",
    "power": "80%"
}])

out.to_csv("outputs/gold_ab_sample_size.csv", index=False)
print("\n✅ Saved outputs/gold_ab_sample_size.csv")
