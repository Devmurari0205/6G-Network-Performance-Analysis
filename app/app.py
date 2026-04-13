import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv(
        "data/network_performance.csv",
        encoding='latin1',
        engine='python'
    )
    
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.lower()
    )
    
    return df

df = load_data()

df.columns = (
    df.columns
    .str.strip()
    .str.replace(" ", "_")
    .str.lower()
)

# Fix Date column
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    months = df['date'].dt.month_name().unique()
    st.write(months)
else:
    st.error(f"Date column not found. Available: {df.columns}")
df = load_data()


# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.title("🔍 Filters")

# Check if date column exists
if 'date' in df.columns:
    
    # Convert to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Drop null dates (important)
    df = df.dropna(subset=['date'])
    
    # Extract months
    month_list = df['date'].dt.month_name().unique()
    
    # Sidebar filter
    month = st.sidebar.multiselect(
        "Month",
        options=month_list,
        default=month_list
    )
    
    # Apply filter
    df = df[df['date'].dt.month_name().isin(month)]

else:
    st.error(f"❌ 'date' column not found. Available columns: {df.columns}")

if 'latency_ms' in df.columns:
    
    df['latency_band'] = pd.cut(
        df['latency_ms'],
        bins=[0, 50, 100, 200, 500],
        labels=['Low', 'Medium', 'High', 'Very High']
    )
st.sidebar.title("🔍 Filters")

if 'latency_band' in df.columns:

    latency_band = st.sidebar.multiselect(
        "Latency Band",
        options=df['latency_band'].dropna().unique(),
        default=df['latency_band'].dropna().unique()
    )

    df = df[df['latency_band'].isin(latency_band)]

else:
    st.error(f"❌ latency_band not found. Available columns: {df.columns}")

if 'network_quality' in df.columns:

    quality = st.sidebar.multiselect(
        "Network Quality",
        options=df['network_quality'].dropna().unique(),
        default=df['network_quality'].dropna().unique()
    )

    df = df[df['network_quality'].isin(quality)]

else:
    st.error(f"❌ network_quality not found. Available: {df.columns}")

st.sidebar.title("🔍 Filters")

if 'operation_mode' in df.columns:

    operation = st.sidebar.multiselect(
        "Operation Mode",
        options=df['operation_mode'].dropna().unique(),
        default=df['operation_mode'].dropna().unique()
    )

    df = df[df['operation_mode'].isin(operation)]

else:
    st.error(f"❌ operation_mode not found. Available: {df.columns}")

# FILTER DATA
if all(col in df.columns for col in ['date','latency_band','network_quality','operation_mode']):
    
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    df = df[
        (df['date'].dt.month_name().isin(month)) &
        (df['latency_band'].isin(latency_band)) &
        (df['network_quality'].isin(quality)) &
        (df['operation_mode'].isin(operation))
    ]

else:
    st.error(f"Missing columns. Available: {df.columns}")

# =========================
# DASHBOARD TITLE
# =========================
st.title("📊 NETWORK PERFORMANCE DASHBOARD")

# =========================
# KPI SECTION
# =========================
col1, col2, col3 = st.columns(3)

# Network Stability
if 'network_stability_index' in df.columns:
    col1.metric(
        "Avg Network Stability Index",
        round(df['network_stability_index'].mean(), 2)
    )
else:
    col1.metric("Avg Network Stability Index", "N/A")

# Latency
latency_col = None

if 'latency_ms' in df.columns:
    latency_col = 'latency_ms'
elif 'network_latency_ms' in df.columns:
    latency_col = 'network_latency_ms'

if latency_col:
    col2.metric(
        "Avg Latency (ms)",
        round(df[latency_col].mean(), 2)
    )
else:
    col2.metric("Avg Latency (ms)", "N/A")

# Efficiency
if 'efficiency_status' in df.columns:
    col3.metric(
        "High Efficiency %",
        round((df['efficiency_status'].str.lower() == "high").mean() * 100, 2)
    )
else:
    col3.metric("High Efficiency %", "N/A")

# =========================
# CHART ROW 1
# =========================
col1, col2, col3 = st.columns(3)

# Efficiency by Operation Mode
if 'operation_mode' in df.columns and 'efficiency' in df.columns:

    eff_mode = df.groupby('operation_mode')['efficiency'].mean().reset_index()

    fig1 = px.bar(
        eff_mode,
        x='operation_mode',
        y='efficiency',
        color='operation_mode',
        title="Efficiency by Operation Mode"
    )

    col1.plotly_chart(fig1, use_container_width=True)

else:
    st.error(f"Missing columns. Available: {df.columns}")

# Daily Trend
# Check columns safely
if all(col in df.columns for col in ['date', 'production_speed_units_per_hr']):

    # detect correct latency column
    latency_col = None
    if 'latency_ms' in df.columns:
        latency_col = 'latency_ms'
    elif 'network_latency_ms' in df.columns:
        latency_col = 'network_latency_ms'

    if latency_col:

        trend = df.groupby('date')[[latency_col, 'production_speed_units_per_hr']].mean().reset_index()

        fig2 = px.line(
            trend,
            x='date',
            y=[latency_col, 'production_speed_units_per_hr'],
            title="Daily Network & Production Trend"
        )

        col2.plotly_chart(fig2, use_container_width=True)

    else:
        st.error("❌ Latency column not found")

else:
    st.error(f"❌ Required columns missing. Available: {df.columns}")

# Pie Chart (Network Quality)
if 'network_quality' in df.columns:

    fig3 = px.pie(
        df,
        names='network_quality',
        title="Network Quality Distribution"
    )

    col3.plotly_chart(fig3, use_container_width=True)

else:
    st.error(f"❌ network_quality not found. Available: {df.columns}")

# =========================
# CHART ROW 2
# =========================
col1, col2, col3 = st.columns(3)

# Efficiency Status Distribution
fig4 = px.histogram(
    df,
    x='efficiency_status',
    color='efficiency_status',
    title="Efficiency Status Distribution",
    text_auto=True
)

# Scatter (Latency vs Speed)
# Detect correct latency column
latency_col = None

if 'latency_ms' in df.columns:
    latency_col = 'latency_ms'
elif 'network_latency_ms' in df.columns:
    latency_col = 'network_latency_ms'

if all(col in df.columns for col in ['production_speed_units_per_hr', 'network_quality']) and latency_col:

    fig5 = px.scatter(
        df,
        x=latency_col,
        y='production_speed_units_per_hr',
        color='network_quality',
        title="Latency vs Production Speed"
    )

    col2.plotly_chart(fig5, use_container_width=True)

else:
    st.error(f"❌ Required columns missing. Available: {df.columns}")
# Area Chart
latency_day = df.groupby(df['date'].dt.day).agg({
    'efficiency': 'mean'
}).reset_index()

latency_day.columns = ['day', 'efficiency']

fig6 = px.area(
    latency_day,
    x='day',
    y='efficiency',
    title="Latency Tolerance Benchmark"
)

col3.plotly_chart(fig6, use_container_width=True)

# =========================
# DASHBOARD 2
# =========================
st.markdown("---")
st.title("📊 NETWORK IMPACT ON MANUFACTURING")

# KPI
col1, col2, col3 = st.columns(3)

col1.metric("Avg Packet Loss", round(df['packet_loss'].mean(), 2))
col2.metric("Avg Production Speed", round(df['production_speed_units_per_hr'].mean(), 2))
col3.metric("Avg Error Rate", round(df['error_rate'].mean(), 2))

# =========================
# CHART ROW 3
# =========================
col1, col2, col3 = st.columns(3)

# Speed by Latency Band
if 'latency_band' in df.columns and 'production_speed_units_per_hr' in df.columns:

    speed_band = df.groupby('latency_band')['production_speed_units_per_hr'].mean().reset_index()

    fig7 = px.bar(
        speed_band,
        x='latency_band',
        y='production_speed_units_per_hr',
        color='latency_band',
        title="Speed by Latency Band"
    )

    col1.plotly_chart(fig7, use_container_width=True)

else:
    st.error("Required columns not found")


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
