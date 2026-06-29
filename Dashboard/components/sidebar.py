import streamlit as st

def render_sidebar():
    st.sidebar.title("NOC Navigation")
    # Streamlit natively handles sidebar navigation when using the `pages/` directory.
    # We can use this component for additional sidebar information or logo.
    st.sidebar.markdown("---")
    st.sidebar.info("AI Copilot is active.")
    st.sidebar.warning("Air-Gapped Mode: ON")
