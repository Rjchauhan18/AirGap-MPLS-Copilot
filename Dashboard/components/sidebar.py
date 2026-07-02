import streamlit as st

def render_sidebar():
    if st.session_state.get("nav_running", False):
        return

    with st.sidebar:
        st.caption("🔒 Air-Gapped Mode Enabled")
        st.markdown("---")
        
    # Core Global and Infrastructure Views
    dashboard_page = st.Page("pages/dashboard.py", title="Global View", icon="📊", default=True)
    topology_page = st.Page("pages/topology.py", title="Network Topology", icon="🌐")
    
    # 🟢 NEW: Dedicated Deep-Dive Telemetry View
    telemetry_page = st.Page("pages/telemetry.py", title="Detailed Telemetry", icon="📈")
    
    # 🟢 NEW: Advanced ML Modeling/Prediction Analytics View
    prediction_page = st.Page("pages/prediction.py", title="AI Prediction Engine", icon="🧠")
    
    # Logs and Communication
    incidents_page = st.Page("pages/incidents.py", title="Incident Logs", icon="🚨")
    chat_page = st.Page("pages/copilot.py", title="Copilot Chat", icon="💬")
    
    # Compiled structure arranged by logical operation flow
    pg = st.navigation({
        "NOC NAVIGATION": [
            dashboard_page, 
            topology_page, 
            telemetry_page, 
            prediction_page, 
            incidents_page, 
            chat_page
        ]
    })
    
    st.session_state["nav_running"] = True
    try:
        pg.run()
    finally:
        st.session_state["nav_running"] = False