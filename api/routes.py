import os
import json
import sys
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from backend.orchestrator import CopilotOrchestrator
from backend.config import QDRANT_URL, OLLAMA_URL, QDRANT_COLLECTION
from api.schemas import StatusResponse, ChatRequest, ChatResponse, TopologyResponse

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

def _count_incidents() -> int:
    incidents_dir = os.path.join(base_dir, "output", "incidents")
    if not os.path.exists(incidents_dir):
        return 0
    try:
        return len([f for f in os.listdir(incidents_dir) if f.endswith(".json")])
    except Exception:
        return 0

def _load_latest_incident() -> Optional[Dict[str, Any]]:
    incidents_dir = os.path.join(base_dir, "output", "incidents")
    if not os.path.exists(incidents_dir):
        return None
    try:
        files = [f for f in os.listdir(incidents_dir) if f.endswith(".json")]
        if not files:
            return None
        files = sorted(files, reverse=True)
        latest_path = os.path.join(incidents_dir, files[0])
        with open(latest_path, "r") as fp:
            return json.load(fp)
    except Exception:
        return None

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

        # Save a fast "PENDING" incident immediately so the dashboard updates quickly.
        from datetime import datetime
        pending_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "incident_details": incident.to_dict(),
            "retrieved_context_used": sources,
            "copilot_analysis": "PENDING: Generating copilot advisory...",
        }
        orch._save_incident_report(incident.incident_id, pending_report)

        # Step 6: LLM Copilot Phase
        incident_json = incident.model_dump_json(indent=2)
        copilot_advice = orch.llm_engine.generate_incident_analysis(
            incident_json=incident_json,
            rag_context=context_string
        )

        # Step 7: Final Assembly and Output
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


@router.post("/predict")
async def predict(payload: TelemetryPayload):
    """
    Synchronous prediction-only endpoint.
    Returns the raw predictor output (or normal status).
    """
    try:
        orch = get_orchestrator()
        telemetry_data = payload.dict()
        prediction_raw = orch.predictor.analyze_telemetry(telemetry_data)
        if prediction_raw:
            return {"status": "predicted", "prediction": prediction_raw}
        return {"status": "normal"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pipeline")
async def pipeline(payload: TelemetryPayload):
    """
    Synchronous full pipeline endpoint (predict → incident → topology → rag → llm).
    Useful for demos / one-shot runs.
    """
    try:
        orch = get_orchestrator()
        telemetry_data = payload.dict()
        report = orch.run_pipeline(telemetry_data)
        if report:
            return {"status": "incident_generated", "report": report}
        return {"status": "normal"}
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


@router.get("/status", response_model=StatusResponse)
async def status():
    try:
        orch = get_orchestrator()
        model_loaded = bool(getattr(getattr(orch, "predictor", None), "model", None))
        return StatusResponse(
            orchestrator_initialized=True,
            model_loaded=model_loaded,
            qdrant_url=QDRANT_URL,
            ollama_url=OLLAMA_URL,
            collection=QDRANT_COLLECTION,
            incidents_count=_count_incidents(),
        )
    except Exception:
        # Don't hard-fail status for demo UX; report minimal info.
        return StatusResponse(
            orchestrator_initialized=False,
            model_loaded=False,
            qdrant_url=QDRANT_URL,
            ollama_url=OLLAMA_URL,
            collection=QDRANT_COLLECTION,
            incidents_count=_count_incidents(),
        )


@router.get("/topology", response_model=TopologyResponse)
async def topology(device: Optional[str] = None):
    """
    Returns Containerlab topology (if available) and optional impact assessment.
    """
    orch = get_orchestrator()
    topo = getattr(getattr(orch, "topology_engine", None), "network_data", None) or {"nodes": {}, "links": []}
    impact = None
    if device:
        try:
            impact = orch.topology_engine.assess_impact(device)
        except Exception:
            impact = {"target_device": device, "affected_vpns": [], "affected_services": [], "connected_devices": []}
    return TopologyResponse(topology=topo, impact=impact)


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    """
    Operator chat endpoint grounded in air-gapped RAG.
    """
    orch = get_orchestrator()
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question must be non-empty")

    # Retrieve RAG context
    sources: List[str] = []
    rag_context = ""
    try:
        retrieved_docs = orch.rag_engine.retrieve(question)
        rag_context = orch.rag_engine.build_context_string(retrieved_docs)
        sources = [doc.get("source") for doc in retrieved_docs if doc.get("source")]
    except Exception:
        rag_context = "No internal runbooks were retrievable. Use standard MPLS/SD-WAN troubleshooting procedures."
        sources = []

    # Optional: include latest incident context to keep answers aligned to live state
    incident_json = None
    latest = _load_latest_incident()
    if latest and latest.get("incident_details"):
        try:
            incident_json = json.dumps(latest["incident_details"], indent=2)
        except Exception:
            incident_json = None

    answer = orch.llm_engine.generate_chat_answer(
        question=question,
        rag_context=rag_context,
        incident_json=incident_json,
    )
    return ChatResponse(answer=answer, sources=sources)