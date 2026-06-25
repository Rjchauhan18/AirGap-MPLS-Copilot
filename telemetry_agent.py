import subprocess
import time
import csv
from datetime import datetime

# ML Dataset File
OUTPUT_FILE = "sdwan_telemetry.csv"

def get_ping_stats():
    try:
        # Ping the remote branch over the overlay tunnel
        output = subprocess.check_output(
            ["sudo", "docker", "exec", "clab-sdwan-mpls-core-host-dc", "ping", "-c", "4", "192.168.2.10"],
            universal_newlines=True
        )
        # Parse standard Linux ping output for latency and jitter approximation
        for line in output.split('\n'):
            if "rtt min/avg/max/mdev" in line or "round-trip min/avg/max" in line:
                stats = line.split('=')[1].strip().split('/')
                avg_lat = float(stats[1])
                jitter = float(stats[3].split(' ')[0]) if len(stats) > 3 else 0.0
                return avg_lat, jitter
    except subprocess.CalledProcessError:
        return 999.0, 999.0 # Network Down Indicator
    return 0.0, 0.0

print("📡 Starting SD-WAN Telemetry Agent. Press Ctrl+C to stop.")
with open(OUTPUT_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["timestamp", "avg_latency_ms", "jitter_ms", "status"])
    
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        latency, jitter = get_ping_stats()
        status = "UP" if latency < 999.0 else "DOWN"
        
        writer.writerow([timestamp, latency, jitter, status])
        file.flush()
        print(f"[{timestamp}] Latency: {latency}ms | Jitter: {jitter}ms | Status: {status}")
        time.sleep(2) # Poll every 2 seconds
