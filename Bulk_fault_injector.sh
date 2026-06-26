#!/bin/bash
LABEL_FILE="Model/ml_ground_truth_labels.csv"
echo "timestamp,fault_type,severity,target_node" > $LABEL_FILE

echo "================================================================="
echo "🏭 CORE-FABRIC FAULT INJECTION FACTORY (OSPF/BGP FLAPPING ACTIVATED)"
echo "================================================================="

# Pre-flight check: Install traffic control tools inside both the host and the router
sudo docker exec clab-sdwan-mpls-core-host-dc apk add iproute2 --no-cache > /dev/null 2>&1
sudo docker exec clab-sdwan-mpls-core-pe-br apk add iproute2 --no-cache > /dev/null 2>&1

# Clear any lingering rules
sudo docker exec clab-sdwan-mpls-core-host-dc tc qdisc del dev eth1 root 2>/dev/null || true
sudo docker exec clab-sdwan-mpls-core-pe-br tc qdisc del dev eth1 root 2>/dev/null || true

for i in {1..50}
do
    echo -e "\n🔄 [CYCLE $i / 50]"
    
    # 1. CLEAN BASELINE
    echo "   🟢 Phase 1: Core Fabric & Hosts Healthy (10ms Baseline)..."
    sudo docker exec clab-sdwan-mpls-core-host-dc tc qdisc del dev eth1 root 2>/dev/null || true
    sudo docker exec clab-sdwan-mpls-core-pe-br tc qdisc del dev eth1 root 2>/dev/null || true
    
    sudo docker exec clab-sdwan-mpls-core-host-dc tc qdisc add dev eth1 root netem delay 10ms 2ms
    sudo docker exec clab-sdwan-mpls-core-pe-br tc qdisc add dev eth1 root netem delay 10ms 2ms
    sleep 20
    
    # 2. PRECURSOR PHASE (Subtle Link Degradation)
    PRECURSOR_TIME=$(date "+%Y-%m-%d %H:%M:%S")
    echo "   ⚠️ Phase 2: Injecting Backbone Jitter & 15% Core Loss (Precursor Signal)..."
    sudo docker exec clab-sdwan-mpls-core-host-dc tc qdisc change dev eth1 root netem delay 60ms 15ms loss 10%
    sudo docker exec clab-sdwan-mpls-core-pe-br tc qdisc change dev eth1 root netem delay 60ms 15ms loss 15%
    echo "$PRECURSOR_TIME,precursor_degradation,low,core_backbone" >> $LABEL_FILE
    sleep 10
    
    # 3. FULL FAULT PHASE (Core Link Outage -> Forces OSPF/BGP to drop to 0)
    FORWARD_TIME=$(date "+%Y-%m-%d %H:%M:%S")
    echo "   🚨 Phase 3: Total Core Link Outage! Forcing OSPF/BGP Adjacency Drop..."
    sudo docker exec clab-sdwan-mpls-core-host-dc tc qdisc change dev eth1 root netem loss 100%
    # Hard drop 100% on the router interface to instantly kill BGP/OSPF peerings
    sudo docker exec clab-sdwan-mpls-core-pe-br tc qdisc change dev eth1 root netem loss 100%
    echo "$FORWARD_TIME,routing_protocol_failure,critical,pe_br_core_link" >> $LABEL_FILE
    sleep 20
    
    # 4. HEALING PHASE (Protocols re-converge back to 1)
    CLEAN_TIME=$(date "+%Y-%m-%d %H:%M:%S")
    echo "   🩹 Phase 4: Core link repaired. Waiting for OSPF/BGP Re-convergence..."
    sudo docker exec clab-sdwan-mpls-core-host-dc tc qdisc del dev eth1 root 2>/dev/null || true
    sudo docker exec clab-sdwan-mpls-core-pe-br tc qdisc del dev eth1 root 2>/dev/null || true
    echo "$CLEAN_TIME,fault_cleared,none,core_backbone" >> $LABEL_FILE
    sleep 5 # Give routing protocols a moment to re-establish before next cycle
done