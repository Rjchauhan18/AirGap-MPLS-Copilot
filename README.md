# 🚨 AirGap-MPLS-Copilot: Predictive AI for SD-WAN Fault Detection

An autonomous, air-gapped machine learning pipeline that simulates an SD-WAN over MPLS network, captures high-resolution telemetry, and deploys a local LLM-powered RAG orchestrator to predict, analyze, and explain network failures in real time.

---


## ⚡ Getting Started & Local Installation

👉 **[ SETUP.md](./setup.md)** for detailed, step-by-step operating prerequisites and installation instructions for Linux, macOS, and Windows WSL2.
## 🧭 Architectural Overview

The **AirGap-MPLS-Copilot** is designed to run in highly secure, mission-critical environments where public cloud access is prohibited. It bridges the gap between low-level network telemetry and high-level incident root-cause analysis using a deterministic hybrid architecture:


```

[ Containerlab Network Topology ]
│
▼ (2s Streaming Polling Loop)
[ Telemetry Agent (HTTP Keep-Alive) ]
│
▼ (JSON Payload)
[ FastAPI Backend ] ◄──► [ Deterministic Topology Engine ]
│
┌────────┴────────┐
▼                 ▼
[ Qdrant Vector DB ] [ Ollama: Phi-3-Mini ]
(Local Runbooks)     (Reasoning & Action)
│                 │
└────────┬────────┘
▼
[ Streamlit NOC Dashboard & Incident Audit Trail ]

```

### 🧠 The Core Pillars
* **Local RAG Orchestrator:** Uses a local instance of Qdrant Vector DB paired with `all-MiniLM-L6-v2` embeddings to pull context-aware network runbooks without outbound internet connections.
* **Deterministic Topology Engine:** Computes exact MPLS/VPN impact programmatically. By keeping structural impacts math-based and deterministic, we completely eliminate LLM hallucinations for business-critical SLA routing.
* **Streamlined Telemetry Pipeline:** An optimized, connection-pooled polling agent that tracks network interface counters, OSPF adjacencies, and BGP status blocks, feeding data via persistent HTTP Keep-Alive pipelines.

---

## 📂 Project Structure

| Directory / File | Core Operational Purpose |
| :--- | :--- |
| **`/backend`** | Core logic engines (Orchestrator, LLM, RAG, Predictor, Topology). |
| **`/api`** | REST API endpoints handling prediction, pipeline, incidents, and telemetry. |
| **`/Dashboard`** | Streamlit NOC UI that polls the API and renders real-time telemetry and metrics. |
| **`/ai_stack`** | Local weights filesystem configuration (Phi-3, Qdrant Vector database storage). |
| **`/rag_docs`** | Knowledge base containing physical network runbooks and markdown topology sheets. |
| **`/output`** | Local persistent file storage tracking JSON audit trails for every incident. |
| **`telemetry_agent.py`** | High-frequency sensor polling loop running inside the network nodes. |

---

## 🛑 Honest Framing & Demo Notes
* **Network Sim Simplification:** The lab underlay is intentionally structured as a single-area OSPF-based core for hackathon setup speed. The true focus of this project is the offline AI pipeline and localized remediation execution.
* **Hybrid Verification:** Impacted services and VPN path dependencies are computed mathematically via graph matching inside the code rather than using raw prompt engineering, guaranteeing $100\%$ accuracy for critical fault localization.

---


