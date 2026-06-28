import streamlit as st
from utils.telemetry_reader import get_telemetry_data
from components.charts import render_line_chart, render_area_chart
from components.sidebar import render_sidebar
from utils.theme import apply_theme

st.set_page_config(page_title="Live Telemetry", layout="wide")
apply_theme()
render_sidebar()

st.title("Live Telemetry")


# Filters
col1, col2 = st.columns(2)
with col1:
    device = st.selectbox("Select Device/Link", ["Core Link (P-Core -> PE-DC)", "EDGE-BR", "EDGE-DC"])
with col2:
    time_range = st.selectbox("Time Range", ["Last 5 Minutes", "Last 15 Minutes", "Last 1 Hour", "All Time"])

st.markdown("---")

@st.fragment(run_every="3s")
def render_live_charts(selected_time_range):
    import pandas as pd
    from datetime import timedelta
    
    df = get_telemetry_data()
    
    # Filter by time range
    if selected_time_range != "All Time" and not df.empty:
        latest_time = df['timestamp'].max()
        if selected_time_range == "Last 5 Minutes":
            cutoff = latest_time - timedelta(minutes=5)
        elif selected_time_range == "Last 15 Minutes":
            cutoff = latest_time - timedelta(minutes=15)
        elif selected_time_range == "Last 1 Hour":
            cutoff = latest_time - timedelta(hours=1)
        df = df[df['timestamp'] >= cutoff]
        
    col_left, col_right = st.columns(2)
    
    with col_left:
        render_line_chart(df, 'timestamp', 'avg_latency_ms', "Latency Over Time (ms)")
        render_line_chart(df, 'timestamp', 'jitter_ms', "Jitter Over Time (ms)", color="#f39c12")
        render_area_chart(df, 'timestamp', 'rx_bytes_per_sec', "Interface Utilization (RX Bytes/s)", color="#9b59b6")
    
    with col_right:
        render_line_chart(df, 'timestamp', 'packet_loss_pct', "Packet Loss Over Time (%)", color="#e74c3c")
        render_area_chart(df, 'timestamp', 'tx_bytes_per_sec', "Interface Utilization (TX Bytes/s)", color="#34495e")
    
    st.markdown("### Advanced Metrics")
    st.dataframe(df.tail(10), width="stretch")

render_live_charts(time_range)
