import os
import json
import logging
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class TopologyEngine:
    def __init__(self, topology_path: str = None):
        """
        Initializes the topology engine using the actual Containerlab output.
        """
        # Dynamically resolve the absolute path to the clab JSON file
        if not topology_path:
            # Gets the root directory (one level up from backend/)
            base_dir = Path(__file__).resolve().parent.parent
            topology_path = os.path.join(base_dir, "clab-sdwan-mpls-core", "topology-data.json")
            
        self.topology_path = topology_path
        self.network_data = self._load_topology()

    def _load_topology(self) -> Dict[str, Any]:
        """Loads the Containerlab topology JSON from disk."""
        if os.path.exists(self.topology_path):
            try:
                with open(self.topology_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to parse topology from {self.topology_path}: {str(e)}")
                return {"nodes": {}, "links": []}
        else:
            logger.error(f"Topology file not found at {self.topology_path}. Is Containerlab running?")
            return {"nodes": {}, "links": []}

    def assess_impact(self, device_name: str) -> Dict[str, Any]:
        """
        Determines the affected neighbors, services, and VPNs if a specific device fails.
        Includes an automated fallback simulation layer if Containerlab metadata labels are missing.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        nodes = self.network_data.get("nodes", {})
        links = self.network_data.get("links", [])
        
        # 1. Aggressive Fuzzy Matching
        matched_node = None
        normalized_target = device_name.lower().replace("_", "-")
        
        for node_key in nodes.keys():
            normalized_key = node_key.lower().replace("_", "-")
            if normalized_target == normalized_key or normalized_target in normalized_key:
                matched_node = node_key
                break
        
        if not matched_node:
            logger.warning(f"Device {device_name} not found in topology graph.")
            return {"target_device": device_name, "affected_vpns": [], "affected_services": [], "connected_devices": []}
            
        node_info = nodes[matched_node]
        
        # 2. Extract Labels with Simulated Enterprise Metadata Fallback
        labels = node_info.get("labels", {})
        vpns_str = labels.get("vpns", "")
        services_str = labels.get("services", "")
        
        # If Containerlab JSON doesn't contain explicit app metadata, simulate it
        if not vpns_str or not services_str:
            SIMULATION_PROFILE = {
                "pe-br": {"vpns": "VPN-10-Retail,VPN-20-Corporate", "services": "POS-Transactions,Branch-VoIP-Gateway"},
                "edge-br": {"vpns": "VPN-20-Corporate", "services": "Local-Internet-Breakout"},
                "pe-dc": {"vpns": "VPN-10-Retail,VPN-20-Corporate,VPN-90-Storage", "services": "DataCenter-Interconnect,Database-Replication"},
                "edge-dc": {"vpns": "VPN-20-Corporate", "services": "Central-Firewall-Appliance,DMZ-Public-Proxy"},
                "p-core": {"vpns": "MPLS-Backbone-Carrier", "services": "Core-MPLS-LDP-Transit"}
            }
            
            # Match the shortname pattern to populate the data structure
            for profile_key, mock_data in SIMULATION_PROFILE.items():
                if profile_key in matched_node.lower():
                    vpns_str = vpns_str or mock_data["vpns"]
                    services_str = services_str or mock_data["services"]
                    break

        vpns = [v.strip() for v in vpns_str.split(",") if v.strip()] if vpns_str else []
        services = [s.strip() for s in services_str.split(",") if s.strip()] if services_str else []

        # 3. Calculate Physical Blast Radius
        connected_devices = []
        for link in links:
            endpoint_a = None
            endpoint_z = None

            if "a" in link and isinstance(link["a"], dict):
                endpoint_a = link["a"].get("node")
            if "z" in link and isinstance(link["z"], dict):
                endpoint_z = link["z"].get("node")
            elif "endpoints" in link and isinstance(link["endpoints"], list) and len(link["endpoints"]) >= 2:
                endpoint_a = link["endpoints"][0].split(":")[0]
                endpoint_z = link["endpoints"][1].split(":")[0]

            if endpoint_a == matched_node and endpoint_z:
                connected_devices.append(endpoint_z)
            elif endpoint_z == matched_node and endpoint_a:
                connected_devices.append(endpoint_a)

        return {
            "target_device": matched_node,
            "connected_devices": list(set(connected_devices)), 
            "affected_vpns": vpns,
            "affected_services": services
            
        }
    
if __name__ == "__main__":
    # Standalone Test
    logging.basicConfig(level=logging.INFO)
    engine = TopologyEngine()
    
    # # Testing with 'pe-dc' which exists in your config folder
    # test_device = "pe-dc" 
    # impact = engine.assess_impact(test_device)
    
    # print(f"\nTopology Impact for {test_device}:")
    # print(json.dumps(impact, indent=2))