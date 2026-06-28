#!/bin/bash
set -e

echo "================================================================="
echo "🪐 NATIVE NETWORK SIMULATION GENERATOR"
echo "================================================================="

# 1. Clean up the broken root folders that the previous script accidentally created
if [ -d "/data/config" ]; then
    echo "🧹 Purging bugged Docker root paths..."
    sudo rm -rf /data/config
fi

# 2. Reclaim ownership of your local files
echo "📁 Verifying local configuration assets..."
sudo chown -R $USER:$USER config/ 2>/dev/null || true

# 3. Check if Docker is running
if ! sudo systemctl is-active --quiet docker; then
    echo "🐳 Awakening Docker subsystem..."
    sudo systemctl start docker
    sleep 2
fi

# 4. Deploy NATIVELY (No wrapper container)
echo "🌐 Launching Native Containerlab topology..."
sudo clab deploy -t sdwan-mpls.clab.yml --reconfigure

echo "================================================================="
echo "🎉 INFRASTRUCTURE STACK OPERATIONAL!"
echo "================================================================="