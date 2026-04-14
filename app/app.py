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

# CLEAN COLUMN NAMES (FINAL STANDARD FORMAT)
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("(", "")
    .str.replace(")", "")
)
     
# Fix Date column
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    months = df['date'].dt.month_name().unique()
    st.write(months)
else:
    st.error(f"Date column not found. Available: {df.columns}")
df = load_data()

# Create latency band safely
if 'latency_band' not in df.columns:
    df['latency_band'] = pd.cut(
        df['latency_ms'],
        bins=[0, 15, 30, 50],
        labels=['Low', 'Medium', 'High']
    )

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
    #month_list = df['date'].dt.month_name().unique()
    
    # Sidebar filter
    month = st.sidebar.multiselect(
        "Month",
        options=month_list,
        default=month_list
    )
    
    # Apply filter
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
import pandas as pd

# Create Latency Band (VERY IMPORTANT)
if 'latency_band' not in df.columns and 'network_latency_ms' in df.columns:
    df['latency_band'] = pd.cut(
        df['network_latency_ms'],
        bins=[0, 20, 50, 100],
        labels=['Low', 'Medium', 'High']
    )

# Create Efficiency Status (optional but useful)
if 'efficiency_status' not in df.columns and 'efficiency' in df.columns:
    df['efficiency_status'] = pd.cut(
        df['efficiency'],
        bins=[0, 60, 80, 100],
        labels=['Low', 'Average', 'High']
    )

# =========================
# Efficiency by Latency Band
# =========================
import streamlit as st
import plotly.express as px
import pandas as pd

# =========================
# STEP 1: CLEAN COLUMNS
# =========================
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# =========================
# STEP 2: CREATE df_filtered (FIX)
# =========================
df_filtered = df.copy()

# =========================
# STEP 3: CREATE LATENCY BAND
# =========================
if 'latency_band' not in df_filtered.columns and 'network_latency_ms' in df_filtered.columns:
    df_filtered['latency_band'] = pd.cut(
        df_filtered['network_latency_ms'],
        bins=[0, 20, 50, 100],
        labels=['Low', 'Medium', 'High']
    )

# =========================
# STEP 4: PLOT
# =========================
if all(col in df_filtered.columns for col in ['latency_band', 'efficiency']):

    fig = px.bar(
        df_filtered,
        x='latency_band',
        y='efficiency',
        color='latency_band',
        title="⚡ Efficiency by Latency Band"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.error(f"Missing columns: {list(df_filtered.columns)}")
 # -------------------------------------   
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
st.markdown(
    "<h2 style='text-align: center; color: #2E86C1;'>📊 Network Impact on Manufacturing Efficiency</h2>",
    unsafe_allow_html=True
)
# Rename columns properly
df.rename(columns={
    'Latency Band': 'latency_band',
    'Production Speed (units per hr)': 'production_speed_units_per_hr',
    'Packet Loss': 'packet_loss',
    'Error Rate': 'error_rate'
}, inplace=True)

import pandas as pd

# Packet Loss Band
if 'packet_loss_band' not in df.columns and 'packet_loss' in df.columns:
    df['packet_loss_band'] = pd.cut(
        df['packet_loss'],
        bins=[0, 1, 3, 5],
        labels=['Low', 'Medium', 'High']
    )

# Packet Loss Category (same but you can customize)
if 'packet_loss_category' not in df.columns and 'packet_loss' in df.columns:
    df['packet_loss_category'] = pd.cut(
        df['packet_loss'],
        bins=[0, 1, 3, 5],
        labels=['Good', 'Average', 'Poor']
    )
# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("🔍 Filters")

df_filtered = df.copy()

# 1. Operation Mode
if 'operation_mode' in df.columns:
    op_mode = st.sidebar.multiselect(
        "Operation Mode",
        options=sorted(df['operation_mode'].dropna().unique()),
        default=sorted(df['operation_mode'].dropna().unique())
    )
    df_filtered = df_filtered[df_filtered['operation_mode'].isin(op_mode)]

# 2. Packet Loss Category
if 'packet_loss_category' in df.columns:
    plc = st.sidebar.multiselect(
        "Packet Loss Category",
        options=df['packet_loss_category'].dropna().unique(),
        default=df['packet_loss_category'].dropna().unique()
    )
    df_filtered = df_filtered[df_filtered['packet_loss_category'].isin(plc)]

# 3. Packet Loss Band
if 'packet_loss_band' in df.columns:
    plb = st.sidebar.multiselect(
        "Packet Loss Band",
        options=df['packet_loss_band'].dropna().unique(),
        default=df['packet_loss_band'].dropna().unique()
    )
    df_filtered = df_filtered[df_filtered['packet_loss_band'].isin(plb)]

# 4. Machine ID
if 'machine_id' in df.columns:
    machine = st.sidebar.multiselect(
        "Machine ID",
        options=df['machine_id'].dropna().unique(),
        default=df['machine_id'].dropna().unique()
    )
    df_filtered = df_filtered[df_filtered['machine_id'].isin(machine)]

# KPI
# =========================
# CREATE LATENCY BAND (IF NOT EXISTS)
# =========================
if 'latency_band' not in df.columns:
    if 'network_latency_ms' in df.columns:
        df['latency_band'] = pd.cut(
            df['latency_ms'],
            bins=[0, 15, 30, 50],
            labels=['Low', 'Medium', 'High']
        )
# KPI
# =========================
col1, col2, col3 = st.columns(3)

col1.metric(
    "Avg Packet Loss",
    round(df['packet_loss'].mean(), 2) if 'packet_loss' in df.columns else "N/A"
)

col2.metric(
    "Avg Production Speed",
    round(df['production_speed_units_per_hr'].mean(), 2) if 'production_speed_units_per_hr' in df.columns else "N/A"
)

col3.metric(
    "Avg Error Rate",
    round(df['error_rate'].mean(), 2) if 'error_rate' in df.columns else "N/A"
)

# =========================
# CHART
# =========================
col1, col2, col3 = st.columns(3)

if 'latency_band' in df.columns and 'production_speed_units_per_hr' in df.columns:

    speed_band = (
        df.groupby('latency_band')['production_speed_units_per_hr']
        .mean()
        .reset_index()
    )

    fig1 = px.bar(
        speed_band,
        x='latency_band',
        y='production_speed_units_per_hr',
        color='latency_band',
        title="Speed by Latency Band"
    )

    col1.plotly_chart(fig1, use_container_width=True)

else:
    col1.error(f"Missing columns. Available: {list(df.columns)}")

# HEATMAP (FIXED)
# =========================
# =========================
# IMPROVED HEATMAP (CLEAR)
# =========================

if all(col in df.columns for col in ['network_stability_index', 'operation_mode', 'machine_id']):

    # Pivot table
    heat = df.pivot_table(
        values='network_stability_index',
        index='operation_mode',
        columns='machine_id',
        aggfunc='mean'
    )

    # Round values for clarity
    heat = heat.round(2)

    # Create heatmap
    fig8 = go.Figure(data=go.Heatmap(
        z=heat.values,
        x=heat.columns,
        y=heat.index,
        colorscale='RdYlGn',   # ✅ better colors (red→yellow→green)
        colorbar=dict(title="NSI"),
        text=heat.values,      # ✅ show values
        texttemplate="%{text}", # ✅ print numbers inside boxes
        hovertemplate="Mode: %{y}<br>Machine: %{x}<br>NSI: %{z}<extra></extra>"
    ))

    # Layout improvements
    fig8.update_layout(
        title="📊 Machine Network Stability Heatmap",
        xaxis_title="Machine ID",
        yaxis_title="Operation Mode",
        xaxis_tickangle=-45,
        height=500
    )

    col2.plotly_chart(fig8, use_container_width=True)

else:
    col2.error(f"Missing columns. Available: {list(df.columns)}")

# Error vs Packet Loss
# =========================
# BOX PLOT (FIXED)
# =========================
# Create packet_loss_band if not exists
if 'packet_loss_band' not in df.columns and 'packet_loss' in df.columns:
    df['packet_loss_band'] = pd.cut(
        df['packet_loss'],
        bins=[0, 1, 3, 5],
        labels=['Low', 'Medium', 'High']
    )

# Plot
if 'packet_loss_band' in df.columns and 'error_rate' in df.columns:

    fig9 = px.box(
        df,
        x='packet_loss_band',
        y='error_rate',
        color='packet_loss_band',
        title="Error by Packet Loss"
    )

    col3.plotly_chart(fig9, use_container_width=True)

else:
    col3.error(f"Missing columns. Available: {list(df.columns)}")
# =========================
# CHART ROW 4
# =========================
col1, col2, col3 = st.columns(3)

# Efficiency vs Latency
# =========================
# BAR CHART (FIXED)
# =========================

# Create latency_band if not exists
if 'latency_band' not in df.columns and 'latency_ms' in df.columns:
    df['latency_band'] = pd.cut(
        df['latency_ms'],
        bins=[0, 15, 30, 50],
        labels=['Low', 'Medium', 'High']
    )

# Create efficiency_status if not exists
if 'efficiency_status' not in df.columns and 'efficiency' in df.columns:
    df['efficiency_status'] = pd.cut(
        df['efficiency'],
        bins=[0, 50, 80, 100],
        labels=['Low', 'Medium', 'High']
    )

# Plot
if all(col in df.columns for col in ['latency_band', 'efficiency', 'efficiency_status']):

    fig10 = px.bar(
        df,
        x='latency_band',
        y='efficiency',
        color='efficiency_status',
        title="Efficiency by Latency Band"
    )

    col1.plotly_chart(fig10, use_container_width=True)

else:
    col1.error(f"Missing columns. Available: {list(df.columns)}")

# Scatter (Defect vs Packet Loss)
# =========================
# SCATTER PLOT (FIXED)
# =========================

if all(col in df.columns for col in [
    'packet_loss',
    'quality_control_defect_rate',
    'network_quality'
]):

    fig11 = px.scatter(
        df,
        x='packet_loss',
        y='quality_control_defect_rate',
        color='network_quality',
        title="Defect vs Packet Loss"
    )

    col2.plotly_chart(fig11, use_container_width=True)

else:
    col2.error(f"Missing columns. Available: {list(df.columns)}")
# Treemap (Risk Events)

import numpy as np

import numpy as np

# =========================
# RISK LEVEL (FIXED)
# =========================

# 🔍 ensure correct column names exist
if 'network_latency_ms' in df.columns:
    latency_col = 'network_latency_ms'
elif 'latency_ms' in df.columns:
    latency_col = 'latency_ms'
else:
    latency_col = None

if latency_col and 'packet_loss' in df.columns:

    conditions = [
        (df[latency_col] > 30) & (df['packet_loss'] > 3.5),
        (df[latency_col] > 30) | (df['packet_loss'] > 3.5)
    ]

    choices = ["CRITICAL", "WARNING"]

    df['risk_level'] = np.select(conditions, choices, default="NORMAL")

    fig12 = px.treemap(
        df,
        path=['risk_level'],
        title="Network Risk Events"
    )

    col3.plotly_chart(fig12, use_container_width=True)

else:
    col3.error(f"Missing columns. Available: {list(df.columns)}")
