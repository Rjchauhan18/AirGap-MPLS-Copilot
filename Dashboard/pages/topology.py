import streamlit as st
from components.topology_graph import render_topology
from utils.theme import apply_theme
from services.api_client import get_topology, get_incidents

# 1. Page Configuration (Must stay at the very top)
st.set_page_config(page_title="Topology", layout="wide")
apply_theme()

st.title("Network Topology")

st.markdown("""
This graph represents the simulated Containerlab SD-WAN over MPLS network.
Nodes are color-coded based on their current health status.
""")

# Fetch Topology Data
topo_payload = {}
try:
    topo_payload = get_topology()
except Exception:
    topo_payload = {"topology": {"nodes": {}, "links": []}}

# Fetch Incident Data to identify the faulty device
incidents = []
try:
    incidents = get_incidents()
except Exception:
    incidents = []

latest_device = None
if incidents and isinstance(incidents[0], dict):
    latest_device = (incidents[0].get("incident_details") or {}).get("device")

# 2. CAPTURE THE CLICK: Assign the graph component to a variable
clicked_node = render_topology(
    topo_payload.get("topology", {}), 
    highlighted_devices=[latest_device] if latest_device else []
)

# 3. ROUTE NATIVELY: Handle the node click without crashing
if clicked_node:
    # If the user clicked the orange faulty device, safely switch to the incidents page
    if latest_device and clicked_node.lower() in latest_device.lower():
        st.warning(f"🚨 Fault detected on **{clicked_node}**. Redirecting to Incident Logs...")
        st.switch_page("pages/incidents.py")
    else:
        # Optional: Display info if they click a healthy green node
        st.info(f"Selected Node: **{clicked_node}** (Status: Healthy)")

st.markdown("---")
st.markdown("### Topology Status")
if latest_device:
    st.warning(f"⚠️ **Warning:** Latest incident involves device **{latest_device}**. See Incidents page for blast radius.")
else:
    st.info("No active incidents yet. Topology is being monitored.")