import streamlit as st
from components.topology_graph import render_topology
from components.sidebar import render_sidebar
from utils.theme import apply_theme
from services.api_client import get_topology, get_incidents

st.set_page_config(page_title="Topology", layout="wide")
apply_theme()
render_sidebar()

st.title("Network Topology")

st.markdown("""
This graph represents the simulated Containerlab SD-WAN over MPLS network.
Nodes are color-coded based on their current health status.
""")

topo_payload = {}
try:
    topo_payload = get_topology()
except Exception:
    topo_payload = {"topology": {"nodes": {}, "links": []}}

# Highlight the latest incident device if any
incidents = []
try:
    incidents = get_incidents()
except Exception:
    incidents = []

latest_device = None
if incidents and isinstance(incidents[0], dict):
    latest_device = (incidents[0].get("incident_details") or {}).get("device")

render_topology(topo_payload.get("topology", {}), highlighted_devices=[latest_device] if latest_device else [])

st.markdown("---")
st.markdown("### Topology Status")
if latest_device:
    st.warning(f"⚠️ **Warning:** Latest incident involves device **{latest_device}**. See Incidents page for blast radius.")
else:
    st.info("No active incidents yet. Topology is being monitored.")
