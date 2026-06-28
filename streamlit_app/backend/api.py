import random
import time

def get_latest_prediction():
    """Mock the ML prediction."""
    return {
        "status": "warning",
        "prediction": "Core Link Failure",
        "confidence": 79,
        "lead_time": "15-30 seconds",
        "signals": [
            "Latency Drift",
            "Packet Loss"
        ],
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

def get_prediction_history():
    """Mock the prediction history."""
    return [
        {"timestamp": "2026-06-27 04:20:00", "prediction": "Network Stable", "confidence": 99, "outcome": "Stable"},
        {"timestamp": "2026-06-27 04:25:00", "prediction": "Latency Spike", "confidence": 65, "outcome": "Resolved"},
        {"timestamp": "2026-06-27 04:30:00", "prediction": "Core Link Failure", "confidence": 79, "outcome": "Pending"},
    ]

def ask_copilot(question: str):
    """Mock RAG + Ollama Copilot response."""
    time.sleep(1) # simulate latency
    if "outage risk increasing" in question.lower():
        return {"answer": "The outage risk is increasing primarily due to significant latency drift and increasing packet loss observed on the Core Link over the last 5 minutes. This pattern historically correlates with a 79% chance of link failure."}
    if "routers are affected" in question.lower():
        return {"answer": "Currently, P-Core and PE-DC are showing the most severe symptoms, specifically on the interface connecting them."}
    if "what should i do" in question.lower():
        return {"answer": "Recommended action: Shift traffic to the secondary MPLS LSP to avoid the potential core link failure."}
    
    return {"answer": f"I received your question: '{question}'. However, my RAG brain is not fully connected yet to provide a specific network operations answer."}
