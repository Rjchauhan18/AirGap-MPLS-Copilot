# 🛠️ Local Setup & Operational Deployment Guide

This guide walks you through setting up, configuring, and demonstrating the **AirGap-MPLS-Copilot** platform on your local machine.

---

## 📋 System Prerequisites

Before running the automated installation scripts, ensure your system meets the requirements for your specific Operating System.

### 🐧 Linux (Native Ubuntu / Kali / Debian)
*This is the preferred native environment for running network emulations.*
* **Docker & Docker Compose:** Installed and added to your current user group (`sudo usermod -aG docker $USER`).
* **Python Engine:** Version `3.11` or higher with `pip` and virtual env handling tools installed.
* **Containerlab Engine:** Installed via the official package manager repository to spin up virtual routers.
* **System Utilities:** Native Linux iproute2 tools (`ip`, `tc` traffic controller elements).

### 🪟 Windows (via WSL2)
*Windows architectures must utilize a Linux subsystem container layer to handle containerized network links.*
* **WSL2 (Ubuntu 22.04 LTS recommended):** Configured and updated to system standard.
* **Docker Desktop:** Configured to use the WSL2 Engine backend with integration checked for your specific distro.
* **Containerlab inside WSL2:** Installed directly within your active Ubuntu WSL terminal instance.

### 🍏 macOS (Intel & Apple Silicon)
* **Docker Desktop:** Installed and actively running.
* **Python Engine:** Version `3.11+` managed natively or via Homebrew.
* > ⚠️ **Limitation Note:** Containerlab relies heavily on native Linux kernel routing headers. If running on macOS, you must execute the network topology simulation inside a dedicated Linux VM or connect your local frontend application to a remote Linux development host.

---

## 🚀 Phase 1: Environment Setup & Local Download

The repository includes a comprehensive `setup.sh` file designed to provision your directories, load model binaries, and verify local docker infrastructure.

Run the setup engine from your project root:
```bash
chmod +x setup.sh
./setup.sh

```

**What the setup script manages automatically:**

1. Generates local storage directories (`output/incidents/`, `Model/`, `ai_stack/`).
2. Pulls open-source weights down locally (`Phi-3-mini` LLM & `all-MiniLM-L6-v2` embeddings).
3. Spins up isolated Docker service hooks for Qdrant Vector DB and Ollama.
4. Compiles your custom model definitions directly into the local Ollama server registry.

---

## 📡 Phase 2: Running the NOC Copilot (Step-by-Step)

For an effective live presentation demo, execute these steps in separate terminal windows or run them in background multiplexers like `tmux`.

### 1. Fire up the Network Simulation

Deploy the multi-node container lab topology infrastructure:

```bash
chmod +x network_simulation.sh
./network_simulation.sh

```


### 2. Start the FastAPI Application Server

Boot up the central processing backend orchestrator:

```bash
uvicorn api.app:app --reload --port 8000

```

### 3. Launch the High-Frequency Telemetry Agent

Initialize the data streaming pipeline loop to pass metrics back into the API core:

```bash
DEVICE_NAME=pe-br python telemetry_agent.py

```
`NOTE`: you can use any of this as `DEVICE_NAME` that are withing network simulation `edge-dc`,`p-core`,`pe-br`,`pe-dc`

### 4. Open the Streamlit UI

Launch your NOC interface to monitor live alerts and trace persistent incidents:

```bash
streamlit run Dashboard/Dashboard.py

```

---

## 🧠 Phase 3: Fault Injection & Real-Time Testing

With your ecosystem actively running, you can simulate realistic link issues to observe how the AI agent predicts and mitigates anomalies.

### Option A: Automated Bulk Test Cycles

To trigger automated sequences of intermittent degradation spikes followed by recovery periods, run the bulk runner:

```bash
chmod +x ./Bulk_fault_injector.sh

sudo ./Bulk_fault_injector.sh

```

### Option B: Precise Manual Fault Injection

Run these individual commands manually to observe the exact moment the AI Copilot detects an anomaly.

#### 1. Simulate Network Link Degradation

Inject random packet drops and a $85\text{ms}$ delay spike on your Provider Edge interfaces. This triggers a `DEGRADED` status warning in your dashboard telemetry pipeline:

```bash
sudo docker exec clab-sdwan-mpls-core-pe-br tc qdisc change dev eth1 root netem delay 85ms 25ms loss 15%

```

#### 2. Simulate Catastrophic Core Outage

Force a $100\%$ immediate connection drop on the interface link. This tears down OSPF adjacency states and changes your core status to `DOWN`:

```bash
sudo docker exec clab-sdwan-mpls-core-pe-br tc qdisc change dev eth1 root netem loss 100%

```

#### 3. Heal Interface Links (Network Recovery)

Clear out active traffic controller rules to restore normal operational states across your SD-WAN fabric:

```bash
sudo docker exec clab-sdwan-mpls-core-pe-br tc qdisc del dev eth1 root 2>/dev/null || true

```

---

## 🛑 Phase 4: System Teardown

Once you finish your hackathon presentation or testing block, clean up your container runtime engine and free up system memory:

```bash
# Tear down simulated lab routing topology
sudo containerlab destroy --topo sdwan-mpls.clab.yml


# =======[Optional]=======
# Stop and power down background AI stack services
docker compose -f docker-compose.ai.yml down

```