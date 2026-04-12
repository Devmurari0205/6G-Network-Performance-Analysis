import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# =========================
# LOAD DATA
# =========================
@st.cache_data
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\united_inteship\Un_project\network_performance.csv", encoding='latin1')

    # FIX COLUMN NAMES
    df.columns = df.columns.str.strip().str.replace(" ", "_")

    # FIX DATE
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')

    return df
df = load_data()


# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.title("🔍 Filters")

month = st.sidebar.multiselect(
    "Month",
    df['Date'].dt.month_name().unique(),
    default=df['Date'].dt.month_name().unique()
)

latency_band = st.sidebar.multiselect(
    "Latency Band",
    df['Latency_Band'].unique(),
    default=df['Latency_Band'].unique()
)

quality = st.sidebar.multiselect(
    "Network_Quality",
     df['Network_Quality'].unique(),
     default=df['Network_Quality'].unique()
)

operation = st.sidebar.multiselect(
    "Operation_Mode",
    df['Operation_Mode'].unique(),
    default=df['Operation_Mode'].unique()
)

# FILTER DATA
df = df[
    (df['Date'].dt.month_name().isin(month)) &
    (df['Latency_Band'].isin(latency_band)) &
    (df['Network_Quality'].isin(quality)) &
    (df['Operation_Mode'].isin(operation))
]

# =========================
# DASHBOARD TITLE
# =========================
st.title("📊 NETWORK PERFORMANCE DASHBOARD")

# =========================
# KPI SECTION
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("Avg Network Stability Index", round(df['Network_Stability_Index'].mean(), 2))
col2.metric("Avg Latency (ms)", round(df['Network_Latency_ms'].mean(), 2))
col3.metric("High Efficiency %",
            round((df['Efficiency_Status'] == "High").mean()*100, 2))

# =========================
# CHART ROW 1
# =========================
col1, col2, col3 = st.columns(3)

# Efficiency by Operation Mode
eff_mode = df.groupby('Operation_Mode')['Efficiency'].mean().reset_index()
fig1 = px.bar(eff_mode, x='Operation_Mode', y='Efficiency',
              color='Operation_Mode', title="Efficiency by Operation Mode")
col1.plotly_chart(fig1, use_container_width=True)

# Daily Trend
trend = df.groupby('Date')[['Network_Latency_ms', 'Production_Speed_units_per_hr']].mean().reset_index()
fig2 = px.line(trend, x='Date', y=['Network_Latency_ms', 'Production_Speed_units_per_hr'],
               title="Daily Network & Production Trend")
col2.plotly_chart(fig2, use_container_width=True)

# Pie Chart (Network Quality)
fig3 = px.pie(df, names='Network_Quality',
              title="Network Quality Distribution")
col3.plotly_chart(fig3, use_container_width=True)

# =========================
# CHART ROW 2
# =========================
col1, col2, col3 = st.columns(3)

# Efficiency Status Distribution
fig4 = px.histogram(df, x='Efficiency_Status',
                    color='Efficiency_Status',
                    title="Efficiency Status Distribution")
col1.plotly_chart(fig4, use_container_width=True)

# Scatter (Latency vs Speed)
fig5 = px.scatter(df, x='Network_Latency_ms', y='Production_Speed_units_per_hr',
                  color='Network_Quality',
                  title="Latency vs Production Speed")
col2.plotly_chart(fig5, use_container_width=True)

# Area Chart
latency_day = df.groupby(df['Date'].dt.day)['Efficiency'].mean().reset_index()
fig6 = px.area(latency_day, x='Date', y='Efficiency',
               title="Latency Tolerance Benchmark")
col3.plotly_chart(fig6, use_container_width=True)

# =========================
# DASHBOARD 2
# =========================
st.markdown("---")
st.title("📊 NETWORK IMPACT ON MANUFACTURING")

# KPI
col1, col2, col3 = st.columns(3)

col1.metric("Avg Packet Loss", round(df['Packet_Loss'].mean(), 2))
col2.metric("Avg Production Speed", round(df['Production_Speed_units_per_hr'].mean(), 2))
col3.metric("Avg Error Rate", round(df['Error_Rate'].mean(), 2))

# =========================
# CHART ROW 3
# =========================
col1, col2, col3 = st.columns(3)

# Speed by Latency Band
speed_band = df.groupby('Latency_Band')['Production_Speed_units_per_hr'].mean().reset_index()
fig7 = px.bar(speed_band, x='Latency_Band', y='Production_Speed_units_per_hr',
              color='Latency_Band',
              title="Speed by Latency Band")
col1.plotly_chart(fig7, use_container_width=True)

# Heatmap
heat = df.pivot_table(values='Network_Stability_Index',
                      index='Operation_Mode',
                      columns='Machine_ID',
                      aggfunc='mean')

fig8 = go.Figure(data=go.Heatmap(
    z=heat.values,
    x=heat.columns,
    y=heat.index
))
fig8.update_layout(title="Machine NSI Heatmap")
col2.plotly_chart(fig8, use_container_width=True)

# Error vs Packet Loss
fig9 = px.box(df, x='Packet_Loss_Band', y='Error_Rate',
              color='Packet_Loss_Band',
              title="Error by Packet Loss")
col3.plotly_chart(fig9, use_container_width=True)

# =========================
# CHART ROW 4
# =========================
col1, col2, col3 = st.columns(3)

# Efficiency vs Latency
fig10 = px.bar(df, x='Latency_Band', y='Efficiency',
               color='Efficiency_Status',
               title="Efficiency by Latency Band")
col1.plotly_chart(fig10, use_container_width=True)

# Scatter (Defect vs Packet Loss)
fig11 = px.scatter(df, x='Packet_Loss', y='Quality_Control_Defect_Rate',
                   color='Network_Quality',
                   title="Defect vs Packet Loss")
col2.plotly_chart(fig11, use_container_width=True)

# Treemap (Risk Events)

import numpy as np

conditions = [
    (df['Network_Latency_ms'] > 30) & (df['Packet_Loss'] > 3.5),
    (df['Network_Latency_ms'] > 30) | (df['Packet_Loss'] > 3.5)
]

choices = ["CRITICAL", "WARNING"]

df['Risk_Level'] = np.select(conditions, choices, default="NORMAL")

fig12 = px.treemap(df,
                   path=['Risk_Level'],
                   title="Network Risk Events")
col3.plotly_chart(fig12, use_container_width=True)