import streamlit as st
import pandas as pd
import plotly.express as px

st.sidebar.title("Kraken Analytics")
st.sidebar.caption("Product Growth Dashboard")

st.markdown("## Page Title Here")
st.caption("Short business explanation of what this page answers.")
st.write("---")

st.title("📈 Retention")

st.markdown("""
This page shows:
- **Cohort retention** (D1 / D7 / D30) by signup week
- **Retention curve** (D0–D30) for activated users
""")

# ---------- Cohort table ----------
cohort = pd.read_csv("outputs/gold_retention_cohorts.csv")
cohort["cohort_week"] = pd.to_datetime(cohort["cohort_week"]).dt.date

st.subheader("🧩 Cohort Retention Table")
st.dataframe(cohort)

# Heatmap values
heat = cohort[["cohort_week", "D1_retention_pct", "D7_retention_pct", "D30_retention_pct"]].copy()
heat = heat.set_index("cohort_week")

fig = px.imshow(
    heat,
    text_auto=True,
    aspect="auto",
    labels=dict(x="Retention Day", y="Cohort Week", color="Retention %")
)

st.subheader("🔥 Cohort Heatmap (D1 / D7 / D30)")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------- Retention curve ----------
curve = pd.read_csv("outputs/gold_retention_curve_fixed.csv")
st.subheader("📉 Retention Curve (Activated Users)")

fig2 = px.line(
    curve,
    x="days_since_signup",
    y="retention_pct",
    markers=True,
    labels={"days_since_signup": "Days since signup", "retention_pct": "Retention (%)"}
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
### How to read this
- The curve shows retention decay from Day 0 to Day 30.
- The heatmap highlights which signup weeks perform better or worse at D1/D7/D30.
""")
