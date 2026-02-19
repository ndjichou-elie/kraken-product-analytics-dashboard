import streamlit as st
import pandas as pd

st.sidebar.title("Kraken Analytics")
st.sidebar.caption("Product Growth Dashboard")

st.markdown("## Page Title Here")
st.caption("Short business explanation of what this page answers.")
st.write("---")

st.title("📣 Acquisition Channel Performance")

st.markdown("""
This page compares acquisition channels across:

- Activation (Deposit + Trade conversion)
- Monetization (Total fees, ARPU, ARPT)
""")

# Load channel KPIs
channel = pd.read_csv("outputs/gold_channel_kpis.csv")

st.subheader("📊 Channel KPI Table")
st.dataframe(channel)

st.divider()

# Trade conversion chart
st.subheader("⚡ Trade Conversion (7D) by Channel")

trade_chart = channel[["acquisition_channel", "trade_conv_7d_pct"]].set_index("acquisition_channel")
st.bar_chart(trade_chart)

st.divider()

# Revenue chart
st.subheader("💰 Total Trading Fees by Channel")

fees_chart = channel[["acquisition_channel", "total_fees"]].set_index("acquisition_channel")
st.bar_chart(fees_chart)

st.divider()

# ARPU + ARPT comparison
st.subheader("📈 ARPU vs ARPT")

arpu_chart = channel[["acquisition_channel", "arpu", "arpt"]].set_index("acquisition_channel")
st.line_chart(arpu_chart)

st.markdown("""
### Business Insight

- **Organic** drives the largest total revenue due to scale.
- **Paid Social** shows strong activation + monetization efficiency.
- **Influencer** has fewer traders but higher ARPT, suggesting high-value users.
""")
