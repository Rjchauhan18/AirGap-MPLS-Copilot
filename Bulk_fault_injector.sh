#!/bin/bash
DOCKER="docker -H unix:///var/run/docker-native.sock"
export DOCKER_HOST=unix:///var/run/docker-native.sock
LABEL_FILE="Model/ml_ground_truth_labels_TEST.csv"
echo "timestamp,fault_type,severity,target_node" > $LABEL_FILE

echo "================================================================="
echo "🏭 CORE-FABRIC FAULT INJECTION FACTORY (OSPF/BGP FLAPPING ACTIVATED)"
echo "================================================================="

# Clear any lingering rules (no sudo needed, no apk needed - tc is baked in)
$DOCKER exec clab-sdwan-mpls-core-host-dc tc qdisc del dev eth1 root 2>/dev/null || true
$DOCKER exec clab-sdwan-mpls-core-host-br tc qdisc del dev eth1 root 2>/dev/null || true

for i in {1..50}
do
    echo -e "\n🔄 [CYCLE $i / 50]"

    # 1. CLEAN BASELINE
    echo "   🟢 Phase 1: Core Fabric & Hosts Healthy (10ms Baseline)..."
    $DOCKER exec clab-sdwan-mpls-core-host-dc tc qdisc del dev eth1 root 2>/dev/null || true
    $DOCKER exec clab-sdwan-mpls-core-host-br tc qdisc del dev eth1 root 2>/dev/null || true
    $DOCKER exec clab-sdwan-mpls-core-host-dc tc qdisc add dev eth1 root netem delay 10ms 2ms
    $DOCKER exec clab-sdwan-mpls-core-host-br tc qdisc add dev eth1 root netem delay 10ms 2ms
    sleep 20

    # 2. PRECURSOR PHASE
    PRECURSOR_TIME=$(date "+%Y-%m-%d %H:%M:%S")
    echo "   ⚠️ Phase 2: Injecting Backbone Jitter & 15% Core Loss (Precursor Signal)..."
    $DOCKER exec clab-sdwan-mpls-core-host-dc tc qdisc change dev eth1 root netem delay 60ms 15ms loss 10%
    $DOCKER exec clab-sdwan-mpls-core-host-br tc qdisc change dev eth1 root netem delay 60ms 15ms loss 15%
    echo "$PRECURSOR_TIME,precursor_degradation,low,core_backbone" >> $LABEL_FILE
    sleep 10

    # 3. FULL FAULT PHASE
    FORWARD_TIME=$(date "+%Y-%m-%d %H:%M:%S")
    echo "   🚨 Phase 3: Total Core Link Outage! Forcing OSPF/BGP Adjacency Drop..."
    $DOCKER exec clab-sdwan-mpls-core-host-dc tc qdisc change dev eth1 root netem loss 100%
    $DOCKER exec clab-sdwan-mpls-core-host-br tc qdisc change dev eth1 root netem loss 100%
    echo "$FORWARD_TIME,routing_protocol_failure,critical,pe_br_core_link" >> $LABEL_FILE
    sleep 20

    # 4. HEALING PHASE
    CLEAN_TIME=$(date "+%Y-%m-%d %H:%M:%S")
    echo "   🩹 Phase 4: Core link repaired. Waiting for OSPF/BGP Re-convergence..."
    $DOCKER exec clab-sdwan-mpls-core-host-dc tc qdisc del dev eth1 root 2>/dev/null || true
    $DOCKER exec clab-sdwan-mpls-core-host-br tc qdisc del dev eth1 root 2>/dev/null || true
    echo "$CLEAN_TIME,fault_cleared,none,core_backbone" >> $LABEL_FILE
    sleep 5
done