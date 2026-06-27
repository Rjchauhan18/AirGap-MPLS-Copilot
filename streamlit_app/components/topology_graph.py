import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

def render_topology():
    st.markdown("### Simulated Network Topology")
    
    nodes = []
    edges = []
    
    # Define Nodes
    nodes.append(Node(id="EDGE-BR", label="EDGE-BR\n(Branch)", size=25, color="#2ecc71"))
    nodes.append(Node(id="PE-BR", label="PE-BR", size=25, color="#2ecc71"))
    nodes.append(Node(id="P-Core", label="P-Core\n(WARNING)", size=30, color="#f39c12")) # Highlighting potential failure
    nodes.append(Node(id="PE-DC", label="PE-DC", size=25, color="#2ecc71"))
    nodes.append(Node(id="EDGE-DC", label="EDGE-DC\n(Datacenter)", size=25, color="#2ecc71"))
    
    # Define Edges
    edges.append(Edge(source="EDGE-BR", target="PE-BR", type="CURVE_SMOOTH"))
    edges.append(Edge(source="PE-BR", target="P-Core", type="CURVE_SMOOTH"))
    edges.append(Edge(source="P-Core", target="PE-DC", type="CURVE_SMOOTH", color="#e74c3c", width=3)) # Highlight bad link
    edges.append(Edge(source="PE-DC", target="EDGE-DC", type="CURVE_SMOOTH"))
    
    config = Config(
        width="100%", 
        height=600, 
        directed=False,
        nodeHighlightBehavior=True, 
        highlightColor="#F7A7A6", 
        collapsible=False,
        node={'labelProperty': 'label'},
        link={'labelProperty': 'label', 'renderLabel': True},
        physics={"barnesHut": {"springLength": 150, "springConstant": 0.05}}
    )
    
    return agraph(nodes=nodes, edges=edges, config=config)
