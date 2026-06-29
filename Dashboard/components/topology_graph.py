import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

def render_topology(topology: dict, highlighted_devices: list[str] | None = None):
    st.markdown("### Simulated Network Topology (Live from Containerlab JSON)")

    highlighted_devices = highlighted_devices or []
    nodes = []
    edges = []

    raw_nodes = (topology or {}).get("nodes", {}) or {}
    raw_links = (topology or {}).get("links", []) or []

    if not raw_nodes:
        st.warning("Topology JSON not found yet. Deploy Containerlab to generate `topology-data.json`.")
        return

    # Nodes
    for node_id, node_data in raw_nodes.items():
        label = node_id
        kind = (node_data or {}).get("kind") or ""
        if kind:
            label = f"{node_id}\n({kind})"

        color = "#2ecc71"
        size = 26
        if any(h.lower() in node_id.lower() for h in highlighted_devices):
            color = "#f39c12"
            size = 32

        nodes.append(Node(id=node_id, label=label, size=size, color=color))

    # Links
    for link in raw_links:
        endpoints = link.get("endpoints") if isinstance(link, dict) else None
        if not endpoints or len(endpoints) != 2:
            continue
        a, b = endpoints
        src = a.split(":")[0]
        dst = b.split(":")[0]
        edges.append(Edge(source=src, target=dst, type="CURVE_SMOOTH"))

    config = Config(
        width="100%",
        height=600,
        directed=False,
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",
        collapsible=False,
        node={"labelProperty": "label"},
        link={"labelProperty": "label", "renderLabel": False},
        physics={"barnesHut": {"springLength": 150, "springConstant": 0.05}},
    )

    return agraph(nodes=nodes, edges=edges, config=config)
