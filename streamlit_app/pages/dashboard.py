import streamlit as st
from components.cards import metric_card
from components.charts import render_line_chart
from utils.telemetry_reader import get_telemetry_data, get_latest_metrics
from utils.prediction_reader import load_prediction_summary
from components.sidebar import render_sidebar

def main():
    st.markdown("## Global Dashboard")
    render_sidebar()
    
    # Top Row Cards
    col1, col2, col3, col4 = st.columns(4)
    latest_metrics = get_latest_metrics()
    prediction = load_prediction_summary()
    
    with col1:
        status_color = "color-warning" if latest_metrics.get("status", "UP") != "UP" else "color-healthy"
        metric_card("Network Status", latest_metrics.get("status", "UNKNOWN"), status_color)
    with col2:
        risk_color = "color-critical" if prediction["confidence"] > 75 else "color-warning"
        metric_card("Prediction Risk", f"{prediction['confidence']}%", risk_color, prediction["prediction"])
    with col3:
        metric_card("Active Alerts", "1", "color-critical", "Core Link Failure Predicted")
    with col4:
        metric_card("Devices Online", "5/5", "color-healthy")

    st.markdown("---")
    
    # Second Row Live Charts
    st.markdown("### Live Telemetry Overview")
    df = get_telemetry_data()
    # tail 30 for live view
    df_tail = df.tail(30)
    
    col_chart1, col_chart2, col_chart3 = st.columns(3)
    with col_chart1:
        render_line_chart(df_tail, 'timestamp', 'avg_latency_ms', "Latency (ms)")
    with col_chart2:
        render_line_chart(df_tail, 'timestamp', 'packet_loss_pct', "Packet Loss (%)", color="#e74c3c")
    with col_chart3:
        render_line_chart(df_tail, 'timestamp', 'jitter_ms', "Jitter (ms)", color="#f39c12")

    st.markdown("---")
    
    # Third Row Prediction Summary
    st.markdown("### AI Prediction Summary")
    col_pred1, col_pred2 = st.columns([2, 1])
    
    with col_pred1:
        st.info(f"**Latest Prediction:** {prediction['prediction']}")
        st.warning(f"**Recommended Action:** Shift traffic to secondary MPLS LSP immediately.")
        
    with col_pred2:
        st.metric("Estimated Time To Failure", prediction['lead_time'])

if __name__ == "__main__":
    from utils.theme import apply_theme
    st.set_page_config(layout="wide")
    apply_theme()
    main()
