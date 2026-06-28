import streamlit as st
from utils.theme import apply_theme
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="NOC AI Copilot",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()

st.title("Air-Gapped Predictive AI NOC Copilot")

# Note: Streamlit natively supports multi-page apps through the 'pages/' directory.
# `app.py` acts as the entrypoint and default landing page (Dashboard).
# However, to keep it clean, we can redirect or just display the dashboard here.

import pages.dashboard as dashboard
dashboard.main()
