import streamlit as st

def metric_card(title: str, value: str, status_color_class: str = "color-healthy", description: str = ""):
    """Renders a custom metric card."""
    card_html = f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value {status_color_class}">{value}</div>
        <div style="font-size: 0.8rem; color: #7f8c8d; margin-top: 5px;">{description}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
