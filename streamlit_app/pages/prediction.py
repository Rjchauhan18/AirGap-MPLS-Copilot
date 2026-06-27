import streamlit as st
from utils.prediction_reader import load_prediction_summary, load_prediction_history
from components.cards import metric_card
from components.charts import render_feature_importance
from components.prediction_table import render_prediction_table
from components.sidebar import render_sidebar
from utils.theme import apply_theme

st.set_page_config(page_title="Prediction Engine", layout="wide")
apply_theme()
render_sidebar()

st.title("Machine Learning Prediction Engine")

prediction = load_prediction_summary()

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Current Prediction", prediction["prediction"], "color-prediction")
with col2:
    metric_card("Confidence Score", f"{prediction['confidence']}%", "color-critical")
with col3:
    metric_card("Lead Time", prediction["lead_time"], "color-warning")
with col4:
    metric_card("Severity", "CRITICAL", "color-critical")

st.markdown("---")

col_feat, col_hist = st.columns([1, 1])

with col_feat:
    st.markdown("### Feature Importance")
    # Mocking feature importance based on signals
    features = ["Latency", "Packet Loss", "Jitter", "Utilization"]
    scores = [0.45, 0.35, 0.15, 0.05]
    render_feature_importance(features, scores)
    
with col_hist:
    st.markdown("### Prediction History")
    history = load_prediction_history()
    render_prediction_table(history)

st.markdown("---")
st.markdown("### Timeline")
st.info(f"**{prediction['timestamp']}**: Model detected **{prediction['prediction']}** with {prediction['confidence']}% confidence. Triggering signals: {', '.join(prediction['signals'])}")
