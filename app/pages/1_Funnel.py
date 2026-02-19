import streamlit as st
import pandas as pd

st.sidebar.title("Kraken Analytics")
st.sidebar.caption("Product Growth Dashboard")

st.markdown("## Page Title Here")
st.caption("Short business explanation of what this page answers.")
st.write("---")

st.title("🔻 Activation Funnel")

st.markdown("""
This page summarizes the 7-day activation funnel:

**Signup → Deposit → Trade**
""")

# Load funnel KPIs
funnel = pd.read_csv("outputs/gold_funnel_kpis.csv")
row = funnel.iloc[0]

total = int(row["total_users"])
deposit = int(row["deposit_within_7d"])
trade = int(row["trade_within_7d"])

deposit_pct = row["deposit_conv_7d_pct"]
trade_pct = row["trade_conv_7d_pct"]
dep_to_trade = row["deposit_to_trade_pct"]

# KPI Cards
col1, col2, col3 = st.columns(3)

col1.metric("Total Users", total)
col2.metric("Deposited within 7D", f"{deposit} ({deposit_pct}%)")
col3.metric("Traded within 7D", f"{trade} ({trade_pct}%)")

st.divider()

st.subheader("📉 Funnel Drop-Off")

funnel_df = pd.DataFrame({
    "Stage": ["Signup", "Deposit", "Trade"],
    "Users": [total, deposit, trade]
})

st.bar_chart(funnel_df.set_index("Stage"))

st.markdown(f"""
### Funnel Insight
- **Deposit Conversion:** {deposit_pct}%  
- **Trade Conversion:** {trade_pct}%  
- **Deposit → Trade Activation:** {dep_to_trade}%  

This highlights how many funded users become active traders.
""")
