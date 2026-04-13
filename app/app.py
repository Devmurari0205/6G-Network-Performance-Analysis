import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("network_performance.csv")

    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.lower()
    )

    return df

df = load_data()

# =========================
# DATA PREP
# =========================
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date'])

# Create latency band
df['latency_band'] = pd.cut(
    df['latency_ms'],
    bins=[0, 15, 30, 50],
    labels=['Low', 'Medium', 'High']
)

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.title("🔍 Filters")

month = st.sidebar.multiselect(
    "Month",
    df['date'].dt.month_name().unique(),
    default=df['date'].dt.month_name().unique()
)

latency = st.sidebar.multiselect(
    "Latency Band",
    df['latency_band'].dropna().unique(),
    default=df['latency_band'].dropna().unique()
)

quality = st.sidebar.multiselect(
    "Network Quality",
    df['network_quality'].unique(),
    default=df['network_quality'].unique()
)

operation = st.sidebar.multiselect(
    "Operation Mode",
    df['operation_mode'].unique(),
    default=df['operation_mode'].unique()
)

# Apply filters
df = df[
    (df['date'].dt.month_name().isin(month)) &
    (df['latency_band'].isin(latency)) &
    (df['network_quality'].isin(quality)) &
    (df['operation_mode'].isin(operation))
]

# =========================
# DASHBOARD 1
# =========================
st.title("📊 NETWORK PERFORMANCE OVERVIEW")

col1, col2, col3 = st.columns(3)

col1.metric("Avg Network Stability Index", round(df['network_stability_index'].mean(), 2))
col2.metric("Avg Network Latency (ms)", round(df['latency_ms'].mean(), 2))
col3.metric("High Efficiency %", round((df['efficiency_status'] == "High").mean() * 100, 2))

# Charts Row 1
c1, c2, c3 = st.columns(3)

fig1 = px.bar(
    df.groupby('operation_mode')['efficiency'].mean().reset_index(),
    x='operation_mode', y='efficiency',
    color='operation_mode',
    title="Efficiency by Operation Mode"
)
c1.plotly_chart(fig1, use_container_width=True)

trend = df.groupby('date')[['latency_ms', 'production_speed_units_per_hr']].mean().reset_index()
fig2 = px.line(trend, x='date', y=['latency_ms', 'production_speed_units_per_hr'],
               title="Daily Network & Production Trend")
c2.plotly_chart(fig2, use_container_width=True)

fig3 = px.pie(df, names='network_quality', title="Network Quality Distribution")
c3.plotly_chart(fig3, use_container_width=True)

# Charts Row 2
c4, c5, c6 = st.columns(3)

fig4 = px.histogram(df, x='efficiency_status', color='efficiency_status',
                    title="Efficiency Status Distribution")
c4.plotly_chart(fig4, use_container_width=True)

fig5 = px.scatter(df, x='latency_ms', y='production_speed_units_per_hr',
                  color='network_quality',
                  title="Latency vs Production Speed")
c5.plotly_chart(fig5, use_container_width=True)

lat_day = df.groupby(df['date'].dt.day)['efficiency'].mean().reset_index()
fig6 = px.area(lat_day, x='date', y='efficiency',
               title="Latency Tolerance Benchmark")
c6.plotly_chart(fig6, use_container_width=True)

# =========================
# DASHBOARD 2
# =========================
st.markdown("---")
st.title("📊 NETWORK IMPACT ON MANUFACTURING")

col1, col2, col3 = st.columns(3)

col1.metric("Avg Packet Loss", round(df['packet_loss'].mean(), 2))
col2.metric("Avg Production Speed", round(df['production_speed_units_per_hr'].mean(), 2))
col3.metric("Avg Error Rate", round(df['error_rate'].mean(), 2))

# Charts Row 3
c7, c8, c9 = st.columns(3)

fig7 = px.bar(
    df.groupby('latency_band')['production_speed_units_per_hr'].mean().reset_index(),
    x='latency_band', y='production_speed_units_per_hr',
    color='latency_band',
    title="Speed by Latency Band"
)
c7.plotly_chart(fig7, use_container_width=True)

heat = df.pivot_table(values='network_stability_index',
                      index='operation_mode',
                      columns='machine_id',
                      aggfunc='mean')

fig8 = go.Figure(data=go.Heatmap(
    z=heat.values,
    x=heat.columns,
    y=heat.index
))
fig8.update_layout(title="Machine NSI Heatmap")
c8.plotly_chart(fig8, use_container_width=True)

fig9 = px.box(df, x='packet_loss_band', y='error_rate',
              color='packet_loss_band',
              title="Error by Packet Loss")
c9.plotly_chart(fig9, use_container_width=True)

# Charts Row 4
c10, c11, c12 = st.columns(3)

fig10 = px.bar(df, x='latency_band', y='efficiency',
               color='efficiency_status',
               title="Efficiency by Latency Band")
c10.plotly_chart(fig10, use_container_width=True)

fig11 = px.scatter(df, x='packet_loss', y='quality_control_defect_rate',
                   color='network_quality',
                   title="Defect vs Packet Loss")
c11.plotly_chart(fig11, use_container_width=True)

# Risk Classification
conditions = [
    (df['latency_ms'] > 30) & (df['packet_loss'] > 3.5),
    (df['latency_ms'] > 30) | (df['packet_loss'] > 3.5)
]

choices = ["CRITICAL", "WARNING"]

df['risk_level'] = np.select(conditions, choices, default="NORMAL")

fig12 = px.treemap(df, path=['risk_level'], title="Network Risk Events")
c12.plotly_chart(fig12, use_container_width=True)
