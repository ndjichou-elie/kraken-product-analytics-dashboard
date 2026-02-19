import streamlit as st
import pandas as pd
import math

st.sidebar.title("Kraken Analytics")
st.sidebar.caption("Product Growth Dashboard")

st.markdown("## Page Title Here")
st.caption("Short business explanation of what this page answers.")
st.write("---")

st.title("🧪 Experiments")

st.markdown("""
This page summarizes A/B test performance for **7-day deposit conversion**.
""")

ab = pd.read_csv("outputs/gold_ab_deposit.csv")

st.subheader("📋 A/B Summary")
st.dataframe(ab)

# Extract control & treatment
c = ab[ab["variant"] == "control"].iloc[0]
t = ab[ab["variant"] == "treatment"].iloc[0]

c_users, c_conv = int(c["users"]), int(c["converters"])
t_users, t_conv = int(t["users"]), int(t["converters"])

p1 = c_conv / c_users
p2 = t_conv / t_users

uplift_pp = (p2 - p1) * 100
uplift_pct = ((p2 - p1) / p1) * 100 if p1 > 0 else 0

# Z-test for proportions (same method you used)
p_pool = (c_conv + t_conv) / (c_users + t_users)
se = math.sqrt(p_pool * (1 - p_pool) * (1/c_users + 1/t_users))
z = (p2 - p1) / se if se > 0 else 0

st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("Control Conversion", f"{p1*100:.2f}%")
col2.metric("Treatment Conversion", f"{p2*100:.2f}%")
col3.metric("Uplift (pp)", f"{uplift_pp:.2f} pp")

st.write(f"**Relative uplift:** {uplift_pct:.2f}%")
st.write(f"**Z-score:** {z:.3f}")

# Simple significance interpretation
if abs(z) >= 1.96:
    st.success("✅ Statistically significant at ~95% confidence (|z| ≥ 1.96).")
else:
    st.warning("⚠️ Not statistically significant at ~95% confidence (|z| < 1.96).")

st.markdown("""
### Recommended decision
- If not significant: **do not ship as a conversion improvement** (iterate or test another change).
- If significant positive uplift: ship (after checking guardrails).
- If significant negative uplift: rollback.
""")
