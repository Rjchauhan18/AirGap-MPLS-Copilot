# AirGap-MPLS-Copilot

## Step1 : Run `network_simulation.sh`
```
sudo ./network_simulation.sh
```

## Step2 : Run telemetry_agent.py
```
sudo python3 telemetry_agent.py
```


## Step3 : 
    
Option1 : To Generate Data Run `Bulk_fault_injector.sh` in New terminal

```
sudo ./Bulk_fault_injector.sh
```

Option2 : To use trained model run `ai_copilot.py` in new terminal

```
python3 ai_copilot.py
```

If you choose Option 2, open a separate terminal to manually inject network anomalies. This allows you to witness the AI Copilot parse telemetry trends, calculate degradation probabilities, and issue early remediation warnings before a hard failure occurs.

### 🛠️ Manual Fault Injection Commands

**To simulate a precursor link degradation (High Latency + Jitter + Drop Rate):**
```bash
sudo docker exec clab-sdwan-mpls-core-host-dc tc qdisc change dev eth1 root netem delay 85ms 25ms loss 15%

sudo docker exec clab-sdwan-mpls-core-pe-br tc qdisc change dev eth1 root netem delay 85ms 25ms loss 15%
```

**To simulate a catastrophic routing & transport failure (100% Outage):**
```bash
sudo docker exec clab-sdwan-mpls-core-host-dc tc qdisc change dev eth1 root netem loss 100%

sudo docker exec clab-sdwan-mpls-core-pe-br tc qdisc change dev eth1 root netem loss 100%
```

**To heal the network back to normal operating baselines:**
```bash
sudo docker exec clab-sdwan-mpls-core-host-dc tc qdisc del dev eth1 root 2>/dev/null || true

sudo docker exec clab-sdwan-mpls-core-pe-br tc qdisc del dev eth1 root 2>/dev/null || true
```