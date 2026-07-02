import streamlit as st
from utils.theme import apply_theme
from components.sidebar import render_sidebar

# 1. Global Page Configuration (Must run exactly once on app boot)
st.set_page_config(
    page_title="NOC AI Copilot",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Apply styling structures
apply_theme()

# 3. Handoff directly to our sidebar routing setup
if __name__ == "__main__":
    render_sidebar()