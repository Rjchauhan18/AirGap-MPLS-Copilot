import streamlit as st
from components.sidebar import render_sidebar
from utils.theme import apply_theme

st.set_page_config(page_title="Settings", layout="wide")
apply_theme()
render_sidebar()

st.title("Settings")

st.markdown("### Copilot Configuration")
st.text_input("Ollama Endpoint", value="http://localhost:11434")
st.text_input("RAG Knowledge Base Path", value="/data/knowledge")

st.markdown("### Telemetry Settings")
st.text_input("Telemetry CSV Path", value="../Model/sdwan_telemetry_test.csv")
st.slider("Refresh Interval (seconds)", min_value=1, max_value=60, value=5)

st.button("Save Settings")
