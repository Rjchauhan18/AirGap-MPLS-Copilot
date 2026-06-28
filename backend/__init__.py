"""
Air-Gapped Predictive Copilot Backend

This package contains all core business logic for the offline AI NOC Copilot.

Modules
-------
config.py
    Global configuration

predictor.py
    ML inference engine

incident_engine.py
    Builds incident objects

priority_engine.py
    Calculates alert priority

topology_engine.py
    Computes affected network scope

rag_engine.py
    Qdrant retrieval

llm_engine.py
    Local Ollama/Phi interface

orchestrator.py
    Main execution pipeline
"""

__version__ = "1.0.0"