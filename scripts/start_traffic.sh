#!/bin/bash
set -e

# Continuous traffic generator (hackathon realism).
# Runs iperf3 server on host-dc and a repeating client on host-br.
#
# Prereq: Containerlab topology deployed.
#
# Usage:
#   sudo ./scripts/start_traffic.sh

echo "Starting iperf3 server on host-dc..."
sudo docker exec -d clab-sdwan-mpls-core-host-dc sh -lc "pkill -f 'iperf3 -s' 2>/dev/null || true; iperf3 -s -p 5201"

echo "Starting repeating iperf3 client on host-br..."
sudo docker exec -d clab-sdwan-mpls-core-host-br sh -lc "apk add --no-cache iperf3 >/dev/null 2>&1 || true; while true; do iperf3 -c 192.168.1.10 -p 5201 -t 5 -i 1 || true; sleep 1; done"

echo "Traffic generation started."

