import streamlit as st
import pandas as pd

st.sidebar.title("Kraken Analytics")
st.sidebar.caption("Product Growth Dashboard")

st.title("📐 Experiment Planning")

st.markdown("""
This page summarizes power analysis for experiment design.
""")

ss = pd.read_csv("outputs/gold_ab_sample_size.csv")

st.subheader("Sample Size Requirement")
st.dataframe(ss)

st.markdown("""
### Key Takeaway
Small conversion lifts require large sample sizes.
Teams must balance expected impact vs experiment cost.
""")

# Duration estimate
users = pd.read_csv("data/dim_users.csv")
users["created_at"] = pd.to_datetime(users["created_at"])
users["signup_day"] = users["created_at"].dt.date

avg_signups = users.groupby("signup_day")["user_id"].count().mean()
total_required = int(ss["total_n"].iloc[0])

days_needed = total_required / avg_signups

st.metric("Estimated Duration (days)", f"{days_needed:.0f}")

st.markdown("""
### Business Insight
At Kraken scale, higher traffic reduces duration dramatically,
but the principle remains: **bigger lifts are easier to measure**.
""")
