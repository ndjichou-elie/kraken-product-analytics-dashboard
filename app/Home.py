import streamlit as st
import pandas as pd

# ---------- Page Config ----------
st.set_page_config(
    page_title="Kraken Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---------- Load CSS ----------
with open("app/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown(
    """
    # 📊 Kraken Product Analytics Dashboard  
    **Executive view of Growth, Activation, Retention & Experiments**
    """,
)

st.write("---")

# Load daily KPIs
daily = pd.read_csv("outputs/gold_daily_kpis.csv")
latest = daily.iloc[-1]

# ---------- KPI Cards ----------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Daily Active Users", f"{int(latest['dau']):,}")
col2.metric("Depositors", f"{int(latest['deposit_users']):,}")
col3.metric("Traders", f"{int(latest['trade_users']):,}")
col4.metric("Fees (USD)", f"${latest['fees_usd']:.2f}")

st.write("")

# ---------- Trends ----------
st.subheader("📈 User Activity Trend")
st.line_chart(daily.set_index("dt")["dau"])

st.subheader("💰 Monetization Trend")
st.line_chart(daily.set_index("dt")["fees_usd"])

st.success("Use the sidebar to explore Funnel, Channels, Retention, and Experiments.")
