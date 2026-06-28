import os
import json
import sys
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from backend.orchestrator import CopilotOrchestrator

router = APIRouter()
orchestrator = None

def get_orchestrator():
    global orchestrator
    if orchestrator is None:
        print("Initializing Orchestrator (Models & Qdrant)...")
        orchestrator = CopilotOrchestrator()
    return orchestrator

class TelemetryPayload(BaseModel):
    device: str
    site: Optional[str] = "Unknown-Site"
    state: Optional[str] = "normal"
    metrics: Dict[str, float]

def background_pipeline_executor(orch: CopilotOrchestrator, prediction_raw: Dict[str, Any]):
    """Runs the heavy RAG and LLM components in a background thread to prevent API blocking."""
    try:
        print("⚡ [Background Task] Running Incident Engine, Topology, RAG, and LLM...")
        
        # Step 2: Incident Creation
        incident = orch.incident_engine.process_prediction(prediction_raw)

        # Step 3: Topology & Impact Phase
        # Force lower-case or fallback to ensure it finds the device in your graph
        device_name = incident.device.lower() 
        impact = orch.topology_engine.assess_impact(device_name)
        incident.affected_vpns = impact.get("affected_vpns", [])
        incident.affected_services = impact.get("affected_services", [])

        # Step 4: Priority Scoring Phase
        priority_data = orch.priority_engine.calculate_priority(incident.to_dict())
        incident.priority_score = priority_data["priority_score"]
        incident.severity = priority_data["severity"]

        # Step 5: RAG Retrieval Phase safely caught
        search_query = f"remediation for {incident.fault_type} on {incident.device}"
        context_string = ""
        try:
            retrieved_docs = orch.rag_engine.retrieve(search_query)
            context_string = orch.rag_engine.build_context_string(retrieved_docs)
            sources = [doc.get("source") for doc in retrieved_docs]
        except Exception as rag_err:
            print(f"⚠️ [RAG Warning] Bypassing RAG due to missing collection: {rag_err}")
            context_string = "Use standard MPLS troubleshooting procedures."
            sources = ["Fallback Protocol Matrix"]

        # Step 6: LLM Copilot Phase
        incident_json = incident.model_dump_json(indent=2)
        copilot_advice = orch.llm_engine.generate_incident_analysis(
            incident_json=incident_json,
            rag_context=context_string
        )

        # Step 7: Final Assembly and Output
        from datetime import datetime
        final_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "incident_details": incident.to_dict(),
            "retrieved_context_used": sources,
            "copilot_analysis": copilot_advice
        }

        orch._save_incident_report(incident.incident_id, final_report)
        print(f"🎉 [Background Task] Incident {incident.incident_id} processed and saved successfully!")
        
    except Exception as e:
        print(f"❌ [Background Task Error] Pipeline execution failed: {str(e)}")

@router.post("/ingest_telemetry")
async def ingest_telemetry(payload: TelemetryPayload, background_tasks: BackgroundTasks):
    try:
        telemetry_data = payload.dict()
        orch = get_orchestrator()
        
        # Step 1: Run prediction synchronously (Instant Random Forest Check)
        prediction_raw = orch.predictor.analyze_telemetry(telemetry_data)
        
        if prediction_raw:
            # Pass the heavy lifting to the background thread pool
            background_tasks.add_task(background_pipeline_executor, orch, prediction_raw)
            return {
                "status": "alert_generated",
                "message": "🚨 IMPENDING FAULT DETECTED! Processing autonomous analysis in background.",
                "prediction": prediction_raw
            }
            
        return {
            "status": "normal",
            "message": "Telemetry processed. Network is healthy."
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/incidents")
async def get_incidents():
    incidents = []
    incidents_dir = os.path.join(base_dir, "output", "incidents")
    if not os.path.exists(incidents_dir):
        return {"incidents": []}
    try:
        for filename in os.listdir(incidents_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(incidents_dir, filename)
                with open(filepath, "r") as f:
                    incidents.append(json.load(f))
        incidents = sorted(incidents, key=lambda x: x.get("incident_details", {}).get("incident_id", ""), reverse=True)
        return {"incidents": incidents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))