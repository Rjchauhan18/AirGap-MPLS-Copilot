#!/bin/bash

LABEL_FILE="ml_ground_truth_labels.csv"

# Create header if it doesn't exist
if [ ! -f $LABEL_FILE ]; then
    echo "timestamp,fault_type,severity,target_node" > $LABEL_FILE
fi

START_TIME=$(date "+%Y-%m-%d %H:%M:%S")
echo "🚨 INJECTING FAULT: 50% Packet Loss on P-Core Router"

# Use iptables inside the core router to randomly drop 50% of traffic
sudo docker exec -it clab-sdwan-mpls-core-p-core iptables -A FORWARD -m statistic --mode random --probability 0.5 -j DROP

# Log the ground truth label for the ML model
echo "$START_TIME,packet_loss,50_percent,p-core" >> $LABEL_FILE

echo "⏳ Fault is active. Gathering telemetry data for 30 seconds..."
sleep 30

echo "✅ HEALING NETWORK: Removing Packet Loss"
sudo docker exec -it clab-sdwan-mpls-core-p-core iptables -D FORWARD -m statistic --mode random --probability 0.5 -j DROP
END_TIME=$(date "+%Y-%m-%d %H:%M:%S")
echo "$END_TIME,fault_cleared,0,p-core" >> $LABEL_FILE

echo "Done. ML Labels updated."
