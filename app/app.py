import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="6G Network Dashboard", layout="wide")

st.title("📡 6G Network Performance Analysis")
st.markdown("Smart Manufacturing | Advanced Dashboard")

# -----------------------------
# LOAD DATA (IMPORTANT FIX)
# -----------------------------
df = pd.read_csv("network_performance.csv")   # <-- keep CSV in same folder

# -----------------------------
# DATE FIX
# -----------------------------
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors='coerce')
df = df.dropna(subset=["Date"])

# -----------------------------
# RISK CATEGORY
# -----------------------------
def risk_category(row):
    if row["Network_Latency_ms"] > 30 or row["Packet_Loss"] > 5:
        return "Critical"
    elif row["Network_Latency_ms"] > 15:
        return "Warning"
    else:
        return "Normal"

df["Risk_Level"] = df.apply(risk_category, axis=1)

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🔍 Filters")

operation_mode = st.sidebar.multiselect(
    "Operation Mode",
    df["Operation_Mode"].unique(),
    default=df["Operation_Mode"].unique()
)

efficiency = st.sidebar.multiselect(
    "Efficiency Status",
    df["Efficiency_Status"].unique(),
    default=df["Efficiency_Status"].unique()
)

df_filtered = df[
    (df["Operation_Mode"].isin(operation_mode)) &
    (df["Efficiency_Status"].isin(efficiency))
]

# -----------------------------
# KPI SECTION
# -----------------------------
st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Avg Latency", round(df_filtered["Network_Latency_ms"].mean(), 2))
col2.metric("Avg Packet Loss", round(df_filtered["Packet_Loss"].mean(), 2))
col3.metric("Avg Production Speed", round(df_filtered["Production_Speed_units_per_hr"].mean(), 2))
col4.metric("Avg Error Rate", round(df_filtered["Error_Rate"].mean(), 2))

# -----------------------------
# RISK CHART
# -----------------------------
st.subheader("🚨 Risk Distribution")

risk_count = df_filtered["Risk_Level"].value_counts().reset_index()
risk_count.columns = ["Risk_Level", "Count"]

fig1 = px.pie(risk_count, names="Risk_Level", values="Count")
st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# SCATTER CHARTS
# -----------------------------
col5, col6 = st.columns(2)

with col5:
    st.subheader("📈 Latency vs Speed")
    fig2 = px.scatter(df_filtered, x="Network_Latency_ms", y="Production_Speed_units_per_hr", color="Efficiency_Status")
    st.plotly_chart(fig2, use_container_width=True)

with col6:
    st.subheader("📉 Packet Loss vs Error Rate")
    fig3 = px.scatter(df_filtered, x="Packet_Loss", y="Error_Rate", color="Risk_Level")
    st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# DISTRIBUTION
# -----------------------------
st.subheader("📊 Efficiency Distribution")

fig4 = px.histogram(df_filtered, x="Efficiency_Status", color="Efficiency_Status")
st.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# TREND
# -----------------------------
st.subheader("📅 Latency Trend")

trend = df.groupby("Date")["Network_Latency_ms"].mean().reset_index()
fig5 = px.line(trend, x="Date", y="Network_Latency_ms")
st.plotly_chart(fig5, use_container_width=True)

# -----------------------------
# END
# -----------------------------
st.success("✅ Dashboard Running Successfully")
