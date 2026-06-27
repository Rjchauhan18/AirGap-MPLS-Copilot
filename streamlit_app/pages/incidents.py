import streamlit as st
from components.prediction_table import render_prediction_table
from utils.prediction_reader import load_prediction_history
from components.sidebar import render_sidebar
from utils.theme import apply_theme

st.set_page_config(page_title="Incident Timeline", layout="wide")
apply_theme()
render_sidebar()

st.title("Incident Timeline")

st.markdown("### Detected Predictions")

history = load_prediction_history()
render_prediction_table(history)

st.markdown("---")
st.markdown("### Operator Notes")
st.text_area("Add note for selected incident:", "Investigating P-Core latency drift...")
st.button("Save Note")
