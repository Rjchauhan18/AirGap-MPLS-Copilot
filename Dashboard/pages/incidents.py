import streamlit as st
from components.sidebar import render_sidebar
from utils.theme import apply_theme
from services.api_client import get_incidents

# 1. Page Configuration
st.set_page_config(page_title="Incident Investigation Timeline", layout="wide")
apply_theme()
render_sidebar()

st.title("🚨 Incident Investigation & Audit Timeline")
st.caption("Review historical autonomous AI detections, playbooks used, and log human engineering overrides.")

# 2. Fetch data from your FastAPI backend
try:
    incidents_list = get_incidents()  # <-- Just take the list directly!
except Exception as e:
    st.error(f"Could not connect to API server: {e}")
    incidents_list = []

if not incidents_list:
    st.info("🟢 No historical network incidents detected yet. Underlay transport links are stable.")
else:
    # Format a clean dropdown list for the operator to select past incidents
    incident_options = {}
    for inc in incidents_list:
        details = inc.get("incident_details", {})
        inc_id = details.get("incident_id", "UNKNOWN_ID")
        fault = details.get("fault_type", "Unknown Fault")
        device = details.get("device", "Unknown Device")
        timestamp = inc.get("timestamp", "").split(".")[0].replace("T", " ")
        
        # Unique display label for dropdown selection
        label = f"[{timestamp}] {inc_id} - {fault} on {device}"
        incident_options[label] = inc

    st.markdown("### 🔍 Select Incident to Investigate")
    selected_label = st.selectbox("Choose a historical log entry:", list(incident_options.keys()))
    
    # Extract the selected incident data payload
    selected_incident = incident_options[selected_label]
    details = selected_incident.get("incident_details", {})

    st.markdown("---")

    # 3. Create a clean two-column layout for Investigation
    col_meta, col_analysis = st.columns([1, 2])

    with col_meta:
        st.markdown("### 📋 Telemetry Footprint")
        st.metric("Incident ID", details.get("incident_id"))
        st.error(f"**Severity:** {details.get('severity', 'P3')} (Score: {details.get('priority_score', 0)})")
        st.markdown(f"**Target Device:** `{details.get('device')}`")
        st.markdown(f"**Impacted Services:** {', '.join(details.get('affected_services', ['None']))}")
        st.markdown(f"**Impacted VPNs:** {', '.join(details.get('affected_vpns', ['None']))}")
        
        # Display sources utilized during RAG retrieval for this specific event
        st.markdown("**📚 Runbooks Referenced:**")
        for source in selected_incident.get("retrieved_context_used", []):
            st.caption(f"• {source}")

    with col_analysis:
        st.markdown("### 🤖 Historical AI Copilot Advisory")
        copilot_text = selected_incident.get("copilot_analysis", "No advisory logged.")
        
        if copilot_text.startswith("PENDING"):
            st.warning("⚠️ The AI engine is still compiling the remediation logs for this event.")
        else:
            st.info(copilot_text)

    st.markdown("---")

    # 4. TRULY PERSISTENT OPERATOR NOTES VIA FASTAPI BACKEND
    st.markdown("### ✍️ Human-in-the-Loop Operator Notes")
    
    # Pull existing notes directly from the JSON if they exist, otherwise default to a prompt
    inc_id = details.get("incident_id")
    existing_note = selected_incident.get("operator_notes", "Investigating underlay interfaces...")

    user_note = st.text_area("Log resolution details or structural observations here:", value=existing_note)
    
    if st.button("💾 Commit Note to Audit Trail"):
        try:
            import requests
            # Fire a post request over to our new backend router endpoint
            api_url = f"http://localhost:8000/incidents/{inc_id}/note"
            response = requests.post(api_url, json={"note": user_note})
            
            if response.status_code == 200:
                st.success(f"🎉 Note permanently bound to `{inc_id}.json` on disk!")
                # Force an instant page rerun so the UI refreshes with the newly saved text
                st.rerun()
            else:
                st.error(f"Backend rejected note save: {response.text}")
        except Exception as err:
            st.error(f"Failed to reach API Server: {err}")