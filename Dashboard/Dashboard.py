# import streamlit as st
# from utils.theme import apply_theme
# from components.sidebar import render_sidebar

# st.set_page_config(
#     page_title="NOC AI Copilot",
#     page_icon="🛡️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# apply_theme()

# st.title("Air-Gapped Predictive AI NOC Copilot")

# # Note: Streamlit natively supports multi-page apps through the 'pages/' directory.
# # `app.py` acts as the entrypoint and default landing page (Dashboard).
# # However, to keep it clean, we can redirect or just display the dashboard here.

# import pages.dashboard as dashboard
# dashboard.main()

import streamlit as st
from utils.theme import apply_theme
from components.sidebar import render_sidebar
from components.cards import metric_card
from components.charts import render_line_chart
from utils.telemetry_reader import get_telemetry_data, get_latest_metrics
from services.api_client import get_incidents, get_status

# 1. Global Page Configuration (Must be the very first Streamlit command)
st.set_page_config(
    page_title="NOC AI Copilot",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Apply Custom Layout Styling & Render Global Sidebar
apply_theme()
render_sidebar()

# 3. Dashboard UI Content
st.title("Air-Gapped Predictive AI NOC Copilot")
st.markdown("## Global Dashboard")
st.caption("Auto-refresh: every 2 seconds (alerts appear quickly).")

# Live Data Fragment Optimization
@st.fragment(run_every="2s")
def render_live():
    status = {}
    try:
        status = get_status()
    except Exception:
        status = {"api": "down"}

    # Top Row Metrics Cards
    col1, col2, col3, col4 = st.columns(4)
    latest_metrics = get_latest_metrics()
    incidents = []
    try:
        incidents = get_incidents()
    except Exception:
        incidents = []

    latest_incident = incidents[0] if incidents else {}
    incident_details = latest_incident.get("incident_details", {}) if isinstance(latest_incident, dict) else {}

    with col1:
        status_color = "color-warning" if latest_metrics.get("status", "UP") != "UP" else "color-healthy"
        metric_card("Network Status", latest_metrics.get("status", "UNKNOWN"), status_color)
    with col2:
        conf = float(incident_details.get("confidence", 0.0) or 0.0)
        risk_color = "color-critical" if conf >= 85 else ("color-warning" if conf >= 65 else "color-healthy")
        pred_label = incident_details.get("fault_type", "No active prediction")
        metric_card("Prediction Risk", f"{conf:.0f}%", risk_color, pred_label)
    with col3:
        active_alerts = len(incidents)
        alert_color = "color-critical" if active_alerts > 0 else "color-healthy"
        metric_card("Active Alerts", str(active_alerts), alert_color, "Incidents generated (latest-first)")
    with col4:
        api_state = status.get("api", "unknown")
        api_color = "color-healthy" if api_state == "ok" else "color-warning"
        metric_card("API Status", str(api_state).upper(), api_color, f"Incidents: {status.get('incidents_count', 0)}")

    st.markdown("---")

    # Second Row Live Network Charts
    st.markdown("### Live Telemetry Overview")
    df = get_telemetry_data()
    df_tail = df.tail(30)

    col_chart1, col_chart2, col_chart3 = st.columns(3)
    with col_chart1:
        render_line_chart(df_tail, "timestamp", "avg_latency_ms", "Latency (ms)")
    with col_chart2:
        render_line_chart(df_tail, "timestamp", "packet_loss_pct", "Packet Loss (%)", color="#e74c3c")
    with col_chart3:
        render_line_chart(df_tail, "timestamp", "jitter_ms", "Jitter (ms)", color="#f39c12")

    st.markdown("---")

    # Third Row Prediction Execution Summary
    st.markdown("### AI Prediction Summary")
    col_pred1, col_pred2 = st.columns([2, 1])

    with col_pred1:
        if incident_details:
            st.info(f"**Latest Prediction:** {incident_details.get('fault_type', 'Unknown')}")
            copilot = latest_incident.get("copilot_analysis", "")
            if copilot:
                if str(copilot).startswith("PENDING"):
                    st.warning(copilot)
                else:
                    st.markdown("**Copilot advisory (latest incident):**")
                    st.write(copilot)
            else:
                st.warning("No copilot advisory saved yet for the latest incident.")
        else:
            st.success("No incidents yet. System is monitoring telemetry.")

    with col_pred2:
        eta = incident_details.get("eta")
        if eta is not None:
            st.metric("Estimated Time To Impact (ETA)", f"{eta} min")
        else:
            st.metric("Estimated Time To Impact (ETA)", "N/A")



# Execute live loop
render_live()