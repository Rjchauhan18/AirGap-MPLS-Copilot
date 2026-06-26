# AirGap-MPLS-Copilot: Predictive AI for SD-WAN Fault Detection

An autonomous, air-gapped machine learning pipeline that simulates an SD-WAN over MPLS network, captures high-resolution telemetry, and uses a Random Forest classifier to predict network failures before operational impact.

---

## 🚀 Phase 1: Deploy Network Infrastructure
Spin up the Containerlab environment, which orchestrates the branches, hubs, datacenter nodes, and FRR routing configurations (OSPF/BGP).

```bash
sudo ./network_simulation.sh

```

*Wait for the containers to deploy and the routing protocols to converge (approx. 30-45 seconds).*

---

## 📡 Phase 2: Start the Telemetry Pipeline

Start the custom telemetry agent to monitor interface utilization, latency, jitter, packet loss, and dynamic routing states across the MPLS fabric.

Leave this running in its own terminal.

```bash
sudo python3 telemetry_agent.py

```

---

## 🧠 Phase 3: AI Copilot Inference & Fault Injection

With the network running and telemetry flowing, you have two options for testing the environment: Automated Data Generation or Live AI Inference.

### Option A: Bulk Data Generation (For ML Training)

Run the automated fault factory to cycle through 50 rounds of network degradation and hard failures. This generates the `sdwan_telemetry.csv` and `ml_ground_truth_labels.csv` used for training the model.

```bash
# Open a new terminal
sudo ./Bulk_fault_injector.sh

```

### Option B: Live AI Copilot Inference (Demo Mode)

If your model (`Model/predictive_brain.joblib`) is already trained, start the AI Copilot to tail the live telemetry and monitor for precursor anomalies.

```bash
# Open a new terminal
python3 ai_copilot.py

```

While the Copilot is running, open a **third terminal** and manually inject anomalies to watch the AI predict the failure before it happens:

#### 🛠️ Manual Fault Injection Commands

**1. Simulate Precursor Degradation (High Latency + Jitter + Drop Rate)**
*Watch the AI Copilot trigger an early warning based on these precursor signals.*

```bash
sudo docker exec clab-sdwan-mpls-core-host-dc tc qdisc change dev eth1 root netem delay 85ms 25ms loss 15%

sudo docker exec clab-sdwan-mpls-core-pe-br tc qdisc change dev eth1 root netem delay 85ms 25ms loss 15%

```

**2. Simulate Catastrophic Failure (100% Outage)**
*Forces OSPF/BGP adjacency drops.*

```bash
sudo docker exec clab-sdwan-mpls-core-host-dc tc qdisc change dev eth1 root netem loss 100%

sudo docker exec clab-sdwan-mpls-core-pe-br tc qdisc change dev eth1 root netem loss 100%

```

**3. Heal the Network (Restore to Baseline)**
*Clears the traffic control rules and allows the network to reconverge.*

```bash
sudo docker exec clab-sdwan-mpls-core-host-dc tc qdisc del dev eth1 root 2>/dev/null || true

sudo docker exec clab-sdwan-mpls-core-pe-br tc qdisc del dev eth1 root 2>/dev/null || true

```

---

## 🛑 Phase 4: Teardown and Cleanup

When you are finished testing, use the following command to cleanly destroy the network topology, remove the Docker containers, and clear the virtual veth-pairs.

```bash
sudo containerlab destroy --topo sdwan-mpls.clab.yml

```
## For Local Ollmna

### Setup Ollama

- Install Ollama (<https://ollama.com/download>)
- Pull the Qwen3:8b model -`ollama pull qwen-3.8b` - Please check the system requirements for the model before pulling it.
- Test using `python test_llm.py` to ensure the model is working correctly.
