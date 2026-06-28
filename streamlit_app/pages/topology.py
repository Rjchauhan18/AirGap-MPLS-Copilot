import streamlit as st
from components.topology_graph import render_topology
from components.sidebar import render_sidebar
from utils.theme import apply_theme

st.set_page_config(page_title="Topology", layout="wide")
apply_theme()
render_sidebar()

st.title("Network Topology")

st.markdown("""
This graph represents the simulated Containerlab SD-WAN over MPLS network.
Nodes are color-coded based on their current health status.
""")

render_topology()

st.markdown("---")
st.markdown("### Topology Status")
st.warning("⚠️ **Warning:** P-Core router is experiencing high latency drift and packet loss, affecting the link to PE-DC.")
