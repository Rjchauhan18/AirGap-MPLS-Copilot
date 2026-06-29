import streamlit as st
from components.copilot_chat import render_chat
from components.sidebar import render_sidebar
from utils.theme import apply_theme

st.set_page_config(page_title="AI Copilot", layout="wide")
apply_theme()
render_sidebar()

st.title("AI Copilot (RAG + Ollama)")
st.caption("Interact with the predictive brain to diagnose failures and receive actionable insights.")

st.markdown("""
**Suggested Queries:**
- *Why is outage risk increasing?*
- *Which routers are affected?*
- *What should I do?*
""")

st.markdown("---")

render_chat()
