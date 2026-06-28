import logging
import time
import subprocess
import os
import socket
from datetime import datetime
from backend.orchestrator import CopilotOrchestrator

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

# ---------------------------------------------------------
# TELEMETRY POLLING FUNCTIONS (Directly from Containerlab)
# ---------------------------------------------------------
def run_cmd(container, cmd_list):
    base_cmd = ["sudo", "docker", "exec", container] + cmd_list
    try:
        return subprocess.check_output(base_cmd, universal_newlines=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return ""

def get_ping_stats():
    output = run_cmd("clab-sdwan-mpls-core-host-dc", ["ping", "-c", "2", "-W", "1", "192.168.1.1"])
    avg_lat, jitter, packet_loss = 999.0, 999.0, 100.0
    if not output: return avg_lat, jitter, packet_loss
        
    for line in output.split('\n'):
        if "packet loss" in line:
            try: packet_loss = float(line.split('%')[0].split(',')[-1].strip())
            except: pass
        if "rtt min/avg/max/mdev" in line or "round-trip min/avg/max" in line:
            try:
                stats = line.split('=')[1].strip().split('/')
                avg_lat = float(stats[1])
                jitter = float(stats[3].split(' ')[0]) if len(stats) > 3 else 0.0
            except: pass
    return avg_lat, jitter, packet_loss

def get_routing_status():
    ospf_output = run_cmd("clab-sdwan-mpls-core-pe-br", ["vtysh", "-c", "show ip ospf neighbor"])
    ospf_healthy = 1 if "Full" in ospf_output else 0
    bgp_output = run_cmd("clab-sdwan-mpls-core-pe-br", ["vtysh", "-c", "show bgp summary"])
    bgp_healthy = 0 if ("Idle" in bgp_output or "Active" in bgp_output) else 1
    return ospf_healthy, bgp_healthy

def get_interface_stats():
    rx_bytes_str = run_cmd("clab-sdwan-mpls-core-p-core", ["cat", "/sys/class/net/eth1/statistics/rx_bytes"]).strip()
    tx_bytes_str = run_cmd("clab-sdwan-mpls-core-p-core", ["cat", "/sys/class/net/eth1/statistics/tx_bytes"]).strip()
    rx_dropped_str = run_cmd("clab-sdwan-mpls-core-p-core", ["cat", "/sys/class/net/eth1/statistics/rx_dropped"]).strip()
    try:
        return int(rx_bytes_str or 0), int(tx_bytes_str or 0), int(rx_dropped_str or 0)
    except ValueError:
        return 0, 0, 0

# ---------------------------------------------------------
# COPILOT DASHBOARD RENDERER
# ---------------------------------------------------------
def print_dashboard(result):
    print("\n" + "="*70)
    print("🚨 AIR-GAPPED NOC COPILOT ALERT 🚨".center(70))
    print("="*70)
    print(f"Incident ID : {result.get('incident_details', {}).get('incident_id', 'N/A')}")
    print(f"Severity    : {result.get('incident_details', {}).get('severity', 'UNKNOWN')}")
    print(f"Device      : {result.get('incident_details', {}).get('device', 'Unknown')} ")
    
    vpns = result.get('incident_details', {}).get('affected_vpns', [])
    print(f"Impact      : {', '.join(vpns) if vpns else 'None detected'}")
    
    print("-" * 70)
    print("COPILOT AUTONOMOUS ANALYSIS:\n")
    print(result.get('copilot_analysis', 'No analysis provided.'))
    print("="*70 + "\n")

# ---------------------------------------------------------
# MAIN EXECUTION LOOP
# ---------------------------------------------------------
def main():
    setup_logging()
    logger = logging.getLogger("CopilotRunner")
    logger.info("Starting Unified Air-Gapped SD-WAN NOC Copilot")

    try:
        orchestrator = CopilotOrchestrator()
    except Exception as e:
        logger.error(f"Failed to initialize backend systems: {str(e)}")
        return

    logger.info("Entering live telemetry monitoring loop. Press Ctrl+C to exit.")
    
    prev_rx = 0
    prev_tx = 0
    prev_time = time.time()
    
    try:
        while True:
            current_time = time.time()
            
            # 1. Scrape Live Network Data
            latency, jitter, loss = get_ping_stats()
            ospf_state, bgp_state = get_routing_status()
            rx_bytes, tx_bytes, rx_dropped = get_interface_stats()
            
            # Calculate Rates
            time_diff = current_time - prev_time
            rx_rate = int((rx_bytes - prev_rx) / time_diff) if prev_rx > 0 else 0
            
            prev_rx = rx_bytes
            prev_tx = tx_bytes
            prev_time = current_time
            
            # Determine state
            if loss == 100.0 or latency >= 999.0 or ospf_state == 0:
                status = "down"
            elif loss > 0.0 or rx_dropped > 0:
                status = "degraded"
            else:
                status = "stable"
                
            logger.info(f"Polled PE-BR: Lat={latency:5.1f}ms, Loss={loss:5.1f}%, OSPF={ospf_state}, State={status.upper()}")

            # 2. Build Payload for AI Pipeline
            live_payload = {
                "device": "pe-br",  # Matches the topology engine perfectly
                "site": "Branch-Office-Site",
                "interface": "eth1",
                "state": status,
                "metrics": {
                    "avg_latency_ms": latency,
                    "latency_ms": latency,          # Included for backward compatibility with your Predictor
                    "jitter_ms": jitter,
                    "packet_loss_pct": loss,
                    "utilization_percent": rx_rate, # Included for backward compatibility
                    "rx_bytes_per_sec": float(rx_rate)
                }
            }

            # 3. Feed to AI Orchestrator
            result = orchestrator.run_pipeline(live_payload)

            # 4. Display result only if it's an anomaly
            if result:
                if "error" not in result:
                    print_dashboard(result)
                else:
                    logger.error(f"Pipeline error: {result.get('error')}")

            # Polling Interval (Matches telemetry_agent.py)
            time.sleep(2)
            
    except KeyboardInterrupt:
        logger.info("\nShutting down NOC Copilot...")

if __name__ == "__main__":
    main()