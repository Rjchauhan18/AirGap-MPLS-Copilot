import subprocess
import time
import csv
import os
from datetime import datetime
import requests
import socket

# ML Dataset File
OUTPUT_FILE = "Model/sdwan_telemetry_test.csv"

# API Endpoint for the AI Copilot
COPILOT_API_URL = "http://127.0.0.1:8000/ingest_telemetry"


def get_dynamic_device_identity():
    """
    Dynamically discovers the real name of the device.
    If running in Containerlab, this grabs the exact container hostname 
    (e.g., 'clab-sdwan-pe-br'), which perfectly matches the topology graph!
    """
    # 1. Allow environment variable override for ultimate flexibility
    if "DEVICE_NAME" in os.environ:
        return os.environ["DEVICE_NAME"]
    
    # 2. Dynamically pull the actual hostname of the machine/container
    return socket.gethostname()

# Get the real, actual name of this device dynamically
ACTUAL_DEVICE_NAME = get_dynamic_device_identity()

def run_cmd(container, cmd_list):
    """Helper function to execute commands safely inside Docker containers."""
    base_cmd = ["sudo", "docker", "exec", container] + cmd_list
    try:
        return subprocess.check_output(base_cmd, universal_newlines=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return ""

def fix_file_permissions():
    """Automatically gives file ownership back to your standard login user account."""
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user:
        subprocess.run(["chown", "-R", f"{sudo_user}:{sudo_user}", "Model/"], stderr=subprocess.DEVNULL)

def get_ping_stats():
    """Captures Latency, Jitter, and Packet Loss from the End-Host."""
    output = run_cmd("clab-sdwan-mpls-core-host-dc", ["ping", "-c", "2", "-W", "1", "192.168.1.1"])
    avg_lat, jitter, packet_loss = 999.0, 999.0, 100.0
    
    if not output:
        return avg_lat, jitter, packet_loss
        
    for line in output.split('\n'):
        if "packet loss" in line:
            try:
                packet_loss = float(line.split('%')[0].split(',')[-1].strip())
            except:
                pass
        if "rtt min/avg/max/mdev" in line or "round-trip min/avg/max" in line:
            try:
                stats = line.split('=')[1].strip().split('/')
                avg_lat = float(stats[1])
                jitter = float(stats[3].split(' ')[0]) if len(stats) > 3 else 0.0
            except:
                pass
    return avg_lat, jitter, packet_loss

def get_routing_status():
    """Captures OSPF and BGP Adjacency States from the Provider Edge Router."""
    ospf_output = run_cmd("clab-sdwan-mpls-core-pe-br", ["vtysh", "-c", "show ip ospf neighbor"])
    ospf_healthy = 1 if "Full" in ospf_output else 0
    
    bgp_output = run_cmd("clab-sdwan-mpls-core-pe-br", ["vtysh", "-c", "show bgp summary"])
    bgp_healthy = 0 if ("Idle" in bgp_output or "Active" in bgp_output) else 1
    
    return ospf_healthy, bgp_healthy

def get_interface_stats():
    """Captures raw SNMP-style Interface Utilization and Error Counters from the Core."""
    rx_bytes_str = run_cmd("clab-sdwan-mpls-core-p-core", ["cat", "/sys/class/net/eth1/statistics/rx_bytes"]).strip()
    tx_bytes_str = run_cmd("clab-sdwan-mpls-core-p-core", ["cat", "/sys/class/net/eth1/statistics/tx_bytes"]).strip()
    rx_dropped_str = run_cmd("clab-sdwan-mpls-core-p-core", ["cat", "/sys/class/net/eth1/statistics/rx_dropped"]).strip()
    
    try:
        rx_bytes = int(rx_bytes_str) if rx_bytes_str else 0
        tx_bytes = int(tx_bytes_str) if tx_bytes_str else 0
        rx_dropped = int(rx_dropped_str) if rx_dropped_str else 0
        return rx_bytes, tx_bytes, rx_dropped
    except ValueError:
        return 0, 0, 0

print("=================================================================")
print("📡 STARTING SELF-FLUSHING SD-WAN TELEMETRY AGENT")
print("=================================================================")

# Ensure directory exists
os.makedirs("Model", exist_ok=True)

# Initialize file with comprehensive headers
if not os.path.exists(OUTPUT_FILE) or os.path.getsize(OUTPUT_FILE) == 0:
    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "timestamp", "avg_latency_ms", "jitter_ms", "packet_loss_pct", 
            "rx_bytes_per_sec", "tx_bytes_per_sec", "rx_dropped", 
            "ospf_state", "bgp_state", "status"
        ])
    fix_file_permissions()

# Variables to calculate real-time interface utilization (throughput)
prev_rx = 0
prev_tx = 0
prev_time = time.time()

while True:
    current_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Poll metrics
    latency, jitter, loss = get_ping_stats()
    ospf_state, bgp_state = get_routing_status()
    rx_bytes, tx_bytes, rx_dropped = get_interface_stats()
    
    # 2. Calculate rates
    time_diff = current_time - prev_time
    rx_rate = int((rx_bytes - prev_rx) / time_diff) if prev_rx > 0 else 0
    tx_rate = int((tx_bytes - prev_tx) / time_diff) if prev_tx > 0 else 0
    
    prev_rx = rx_bytes
    prev_tx = tx_bytes
    prev_time = current_time
    
    if loss == 100.0 or latency >= 999.0 or ospf_state == 0:
        status = "DOWN"
    elif loss > 0.0 or rx_dropped > 0:
        status = "DEGRADED"
    else:
        status = "UP"
    
    # 3. Open, Append, and Close immediately (Forces OS to show file changes)
    with open(OUTPUT_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            timestamp, latency, jitter, loss, 
            rx_rate, tx_rate, rx_dropped, 
            ospf_state, bgp_state, status
        ])
    
    fix_file_permissions()
    
    print(f"[{timestamp}] Lat: {latency:5.1f}ms | Loss: {loss:5.1f}% | OSPF: {ospf_state} | BGP: {bgp_state} | Util: {rx_rate}/{tx_rate} Bps | [{status}]")
    
    # -------------------------------------------------------------
    # 4. SEND LIVE DATA TO AI COPILOT API
    # -------------------------------------------------------------
    def get_site_context(device_name):
        dev_lower = device_name.lower()
        if "-br" in dev_lower or "_br" in dev_lower:
            return "Branch-Office-Site"
        elif "-dc" in dev_lower or "_dc" in dev_lower:
            return "Data-Center-Site"
        elif "core" in dev_lower:
            return "Core-Transit-Backbone"
        return "Enterprise-WAN-Edge"

    dynamic_site = get_site_context(ACTUAL_DEVICE_NAME)

    payload = {
        "device": ACTUAL_DEVICE_NAME, 
        "site": dynamic_site, 
        "state": status.lower(),
        "metrics": {
            "avg_latency_ms": latency,
            "jitter_ms": jitter,
            "packet_loss_pct": loss,
            "rx_bytes_per_sec": float(rx_rate)
        }
    }
    
    try:
        # Use a short timeout so a slow API doesn't bottleneck our data polling
        response = requests.post(COPILOT_API_URL, json=payload, timeout=2.0)
        
        # If the ML model flagged an anomaly, print the alert
        if response.status_code == 200:
            api_data = response.json()
            if api_data.get("status") == "alert_generated":
                print(f"  🚨 [COPILOT PREDICTION] {api_data.get('message')}")
    except requests.exceptions.Timeout:
        print("  ⚠️ [API] Connection timed out. Is the backend under heavy load?")
    except requests.exceptions.ConnectionError:
        print("  ⚠️ [API] Could not connect. Is 'python -m api.app' running?")
    except Exception as e:
        print(f"  ⚠️ [API] Unexpected error: {e}")

    # Sleep before next poll
    time.sleep(2)