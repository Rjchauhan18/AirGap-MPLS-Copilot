# AirGap-MPLS-Copilot: Predictive AI for SD-WAN Fault Detection

An autonomous, air-gapped machine learning pipeline that simulates an SD-WAN over MPLS network, captures high-resolution telemetry, and uses a local LLM-powered RAG orchestrator to predict and explain network failures.

---

## 🚀 Phase 1: Environment Setup

Initialize the AI stack (Qdrant/Ollama), download the required embedding and LLM models, and populate the vector database with RAG documentation.

```bash
chmod +x setup.sh
./setup.sh

```

*The setup script will:*

1. Create the necessary directory structure.
2. Download Phi-3-mini (LLM) and all-MiniLM-L6-v2 (Embeddings).
3. Start the Docker containers (Qdrant/Ollama).
4. Build the custom `local-model` in Ollama.
5. Ingest documentation from `rag_docs/`.

---

## 📡 Phase 2: Run the NOC Copilot (API + Dashboard)

For a product-style demo, **FastAPI is the brain** and **Streamlit is the NOC UI**:

Telemetry → `api/` → `backend/` pipeline → `output/` artifacts → Dashboard

1. **Start the Network Simulation**
```bash
sudo ./network_simulation.sh

```

2. **Start the AI Stack (Qdrant + Ollama)**
```bash
docker compose -f docker-compose.ai.yml up -d

```

3. **Ingest RAG docs (one time)**
```bash
python scripts/ingest_docs.py
```

4. **Start the Backend API**
```bash
python -m api.app
```

5. **Start the Telemetry Agent (sends live telemetry to the API + writes CSV)**
```bash
DEVICE_NAME=pe-br python telemetry_agent.py
```

6. **Start the NOC Dashboard**
```bash
streamlit run Dashboard/app.py
```

Optional (recommended): **generate continuous traffic** for more realistic utilization signals:
```bash
sudo ./scripts/start_traffic.sh
```

*The Dashboard auto-refreshes so when a failure is detected it shows an alert quickly; the copilot advisory is generated using local RAG + local LLM (no internet).*

---

## 🧠 Phase 3: Fault Injection & Testing

With the Copilot running, you can test its autonomous response capabilities using either bulk automation or manual interference.

### Option A: Bulk Fault Injection (Training/Testing)

Automate a cycle of network degradations and hard failures to trigger the incident pipeline multiple times.

```bash
sudo ./Bulk_fault_injector.sh

```

### Option B: Manual Fault Injection

Use these commands in a separate terminal while `run.py` is active to observe the AI's real-time reasoning.

**1. Simulate Precursor Degradation**
*Triggers the Copilot to warn about latency and jitter.*

```bash
sudo docker exec clab-sdwan-mpls-core-pe-br tc qdisc change dev eth1 root netem delay 85ms 25ms loss 15%

```

**2. Simulate Catastrophic Failure**
*Triggers a "Down" status and OSPF/BGP adjacency drops.*

```bash
sudo docker exec clab-sdwan-mpls-core-pe-br tc qdisc change dev eth1 root netem loss 100%

```

**3. Heal the Network (Restore)**

```bash
sudo docker exec clab-sdwan-mpls-core-pe-br tc qdisc del dev eth1 root 2>/dev/null || true

```

---

## 🛑 Phase 4: Teardown

Cleanly destroy the network topology and remove Docker containers.

```bash
sudo containerlab destroy --topo sdwan-mpls.clab.yml

```

---

## 📂 Project Structure

* `/backend`: Core logic engines (Orchestrator, LLM, RAG, Predictor, Topology).
* `/api`: REST API entrypoint (predict, pipeline, incidents, topology, chat, status).
* `/Dashboard`: Streamlit NOC UI (polls the API and renders incidents/telemetry/chat/topology).
* `/ai_stack`: Local models (Phi-3, Embeddings) and vector database storage.
* `/rag_docs`: Knowledge base of runbooks and topology context.
* `/output`: JSON artifacts of every generated incident.
* `run.py`: Legacy single-process runner (useful for quick local debugging).

## Demo note (honest framing)

- MPLS/VPN *impact* is computed deterministically by the `TopologyEngine` (no LLM hallucination).
- The lab underlay is intentionally simplified (OSPF-based) for hackathon speed; the AI pipeline and offline copilot are the focus.
