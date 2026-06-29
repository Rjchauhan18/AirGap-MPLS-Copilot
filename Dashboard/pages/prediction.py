import streamlit as st
from components.cards import metric_card
from components.charts import render_feature_importance
from components.prediction_table import render_prediction_table
from components.sidebar import render_sidebar
from utils.theme import apply_theme
from services.api_client import get_incidents

st.set_page_config(page_title="Prediction Engine", layout="wide")
apply_theme()
render_sidebar()

st.title("Machine Learning Prediction Engine")

incidents = []
try:
    incidents = get_incidents()
except Exception:
    incidents = []

latest = incidents[0] if incidents else {}
details = latest.get("incident_details", {}) if isinstance(latest, dict) else {}
signals = details.get("raw_signals", []) or details.get("signals", [])

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Current Prediction", details.get("fault_type", "None"), "color-prediction")
with col2:
    conf = float(details.get("confidence", 0.0) or 0.0)
    metric_card("Confidence Score", f"{conf:.0f}%", "color-critical" if conf >= 85 else "color-warning")
with col3:
    eta = details.get("eta")
    metric_card("Lead Time (ETA)", f"{eta} min" if eta is not None else "N/A", "color-warning")
with col4:
    metric_card("Severity", details.get("severity", "N/A"), "color-critical")

st.markdown("---")

col_feat, col_hist = st.columns([1, 1])

with col_feat:
    st.markdown("### Feature Importance")
    if signals:
        # Lightweight heuristic: treat signal strings as "top features"
        features = [s.split("(")[0].strip()[:32] for s in signals[:6]]
        scores = list(reversed([max(0.05, 1.0 / (i + 2)) for i in range(len(features))]))
        render_feature_importance(features, scores)
    else:
        st.info("No signal breakdown available yet (no incidents).")
    
with col_hist:
    st.markdown("### Prediction History")
    render_prediction_table(incidents)

st.markdown("---")
st.markdown("### Timeline")
if details:
    ts = latest.get("timestamp", "N/A")
    st.info(
        f"**{ts}**: Model predicted **{details.get('fault_type', 'Unknown')}** "
        f"with {details.get('confidence', 'N/A')}% confidence. "
        f"Signals: {', '.join(signals) if signals else 'N/A'}"
    )
else:
    st.success("No incidents yet. Waiting for predictive engine to trigger.")
