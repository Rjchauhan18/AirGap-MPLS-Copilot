#!/usr/bin/env python3
"""
Diagnostic script to verify Topology and RAG engine compliance.
Run this from the project root or the test/ directory.
"""
import sys
import os
import json
import logging
from pathlib import Path

# Fix python paths cleanly: resolve the project root directory
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

try:
    from backend.topology_engine import TopologyEngine
    from backend.rag_engine import RagEngine
except ImportError as e:
    print(f"❌ Critical Import Error: {e}")
    print("Please ensure you are running this from the correct folder or environment.")
    sys.exit(1)

def run_debug():
    print("==================================================")
    print("               DIAGNOSTIC START                   ")
    print("==================================================")
    
    # 1. Test Topology Engine
    print("\n[1] Testing Topology Engine...")
    try:
        topo = TopologyEngine()
        print(f"🔹 Target file path: {topo.topology_path}")
        
        # Verify underlying data shape
        raw_data = topo.network_data
        print(f"🔹 Network data type parsed: {type(raw_data)}")
        
        nodes = raw_data.get("nodes", {})
        links = raw_data.get("links", [])
        print(f"🔹 Found {len(nodes)} total nodes and {len(links)} total links in JSON.")
        print(f"🔹 Available node keys in JSON: {list(nodes.keys())}")

        # Test Impact Assessments with different string variants to verify fuzzy matching
        test_cases = ["pe-br", "PE-BR", "pe_br"]
        
        print("\n--- Running Impact Tests (Fuzzy Match Validation) ---")
        for device in test_cases:
            print(f"\nEvaluating: '{device}'")
            impact = topo.assess_impact(device)
            
            # If target_device matches something inside the nodes or contains it
            if impact.get("target_device") != device or impact.get("connected_devices"):
                print(f"   ✅ SUCCESS: Matched node to internal ID: '{impact.get('target_device')}'")
                print(f"   Blast Radius Neighbors: {impact.get('connected_devices')}")
                print(f"   Affected VPNs: {impact.get('affected_vpns')}")
                print(f"   Affected Services: {impact.get('affected_services')}")
            else:
                print(f"   ❌ FAILURE: '{device}' could not be resolved against the JSON node keys.")
                
    except Exception as e:
        print(f"❌ Error testing Topology Engine: {str(e)}")

    # 2. Test RAG Engine
    print("\n[2] Testing RAG Engine...")
    try:
        rag = RagEngine()
        query = "How to remediate BGP flapping on pe-br"
        print(f"🔹 Issuing query: '{query}'")
        results = rag.retrieve(query, top_k=2)
        
        if results:
            print(f"✅ SUCCESS: RAG retrieved {len(results)} context documents.")
            for i, res in enumerate(results):
                source = res.get('source', 'Unknown source')
                score = res.get('score', 0.0)
                print(f"   📄 Doc {i+1}: {source} (Score: {score:.2f})")
        else:
            print("❌ FAILURE: No matching documents found for query in the vector store.")
    except Exception as e:
        print(f"❌ Error testing RAG Engine: {str(e)}")

    print("\n==================================================")
    print("                DIAGNOSTIC END                    ")
    print("==================================================")

if __name__ == "__main__":
    # Suppress verbose debugs during diagnostic run unless needed
    logging.basicConfig(level=logging.WARNING)
    run_debug()