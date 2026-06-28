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

## 📡 Phase 2: Run the Unified NOC Copilot

Instead of running separate agents and scripts, the unified `run.py` orchestrator handles telemetry polling, prediction, impact analysis, and LLM advisory generation.

1. **Start the Network Simulation:**
```bash
sudo ./network_simulation.sh

```


2. **Start the Copilot:**
```bash
python3 run.py

```



*The Copilot will now automatically poll the network every 2 seconds, detect anomalies, and print the Incident Report directly to your terminal.*

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
* `/ai_stack`: Local models (Phi-3, Embeddings) and vector database storage.
* `/rag_docs`: Knowledge base of runbooks and topology context.
* `/output`: JSON artifacts of every generated incident.
* `run.py`: The main entry point for the Unified NOC Copilot.
