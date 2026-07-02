import os
import json
import sys
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
from backend.orchestrator import CopilotOrchestrator
from backend.config import QDRANT_URL, OLLAMA_URL, QDRANT_COLLECTION, DEFAULT_OPERATOR_ID
from api.schemas import StatusResponse, ChatRequest, ChatResponse, TopologyResponse



base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)


router = APIRouter()
orchestrator = None

ACTIVE_INCIDENTS: Dict[str, float] = {}  # Tracks { "device_name": timestamp }
INCIDENT_COOLDOWN_SECONDS = 300


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
    operator_id: Optional[str] = DEFAULT_OPERATOR_ID  # Track pipeline tasks per operator profile

class NotePayload(BaseModel):
    note: str

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

def background_pipeline_executor(orch: CopilotOrchestrator, prediction_raw: Dict[str, Any], operator_id: str):
    """Runs components in a background thread to prevent API blocking with memory tracking integration."""
    try:
        print("⚡ [Background Task] Running Incident Engine, Topology, RAG, and LLM with Memory...")
        
        incident = orch.incident_engine.process_prediction(prediction_raw)
        device_name = incident.device.lower() 
        impact = orch.topology_engine.assess_impact(device_name)
        incident.affected_vpns = impact.get("affected_vpns", [])
        incident.affected_services = impact.get("affected_services", [])

        priority_data = orch.priority_engine.calculate_priority(incident.to_dict())
        incident.priority_score = priority_data["priority_score"]
        incident.severity = priority_data["severity"]

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

        # Fast "PENDING" placeholder report save
        pending_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "incident_details": incident.to_dict(),
            "retrieved_context_used": sources,
            "copilot_analysis": "PENDING: Generating copilot advisory...",
        }
        orch._save_incident_report(incident.incident_id, pending_report)

        # Pull memory context for the pipeline task execution
        mem_context = orch.memory_engine.get_operator_context(operator_id=operator_id, query=search_query)

        incident_json = incident.model_dump_json(indent=2)
        copilot_advice = orch.llm_engine.generate_incident_analysis(
            incident_json=incident_json,
            rag_context=context_string,
            memory_context=mem_context
        )

        final_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "incident_details": incident.to_dict(),
            "retrieved_context_used": sources,
            "copilot_analysis": copilot_advice
        }

        orch._save_incident_report(incident.incident_id, final_report)
        
        # Save incident execution pattern outcome back to operator tracking profile
        orch.memory_engine.add_interaction_memory(operator_id=operator_id, query=search_query, response=copilot_advice)
        print(f"🎉 [Background Task] Incident {incident.incident_id} processed successfully with memory tracking!")
        
    except Exception as e:
        print(f"❌ [Background Task Error] Pipeline execution failed: {str(e)}")

@router.post("/ingest_telemetry")
async def ingest_telemetry(payload: TelemetryPayload, background_tasks: BackgroundTasks):
    try:
        import time  # Ensure time is imported for timestamps
        
        telemetry_data = payload.model_dump()
        op_id = telemetry_data.pop("operator_id", DEFAULT_OPERATOR_ID)
        orch = get_orchestrator()
        
        prediction_raw = orch.predictor.analyze_telemetry(telemetry_data)
        if prediction_raw:
            device_name = payload.device
            current_time = time.time()
            
            # Check if this specific device is already in a cooldown period
            if device_name in ACTIVE_INCIDENTS:
                time_since_last_alert = current_time - ACTIVE_INCIDENTS[device_name]
                if time_since_last_alert < INCIDENT_COOLDOWN_SECONDS:
                    # Bypasses heavy LLM execution and alerts quietly
                    return {
                        "status": "alert_suppressed",
                        "message": f"Anomaly detected on {device_name}, but analysis is already underway/throttled."
                    }
            
            # Set/Reset cooldown timestamp for the device and trigger pipeline
            ACTIVE_INCIDENTS[device_name] = current_time
            
            background_tasks.add_task(background_pipeline_executor, orch, prediction_raw, op_id)
            return {
                "status": "alert_generated",
                "message": "🚨 IMPENDING FAULT DETECTED! Processing autonomous analysis in background.",
                "prediction": prediction_raw
            }
            
        return {"status": "normal", "message": "Telemetry processed. Network is healthy."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/predict")
async def predict(payload: TelemetryPayload):
    try:
        orch = get_orchestrator()
        telemetry_data = payload.model_dump()
        telemetry_data.pop("operator_id", None)
        prediction_raw = orch.predictor.analyze_telemetry(telemetry_data)
        if prediction_raw:
            return {"status": "predicted", "prediction": prediction_raw}
        return {"status": "normal"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pipeline")
async def pipeline(payload: TelemetryPayload):
    try:
        orch = get_orchestrator()
        telemetry_data = payload.model_dump()
        op_id = telemetry_data.pop("operator_id", DEFAULT_OPERATOR_ID)
        report = orch.run_pipeline(telemetry_data, operator_id=op_id)
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
async def chat(payload: ChatRequest, background_tasks: BackgroundTasks):
    orch = get_orchestrator()
    question = payload.question.strip()
    operator_id = payload.operator_id or DEFAULT_OPERATOR_ID
    if not question:
        raise HTTPException(status_code=400, detail="question must be non-empty")

    sources: List[str] = []
    rag_context = ""
    try:
        retrieved_docs = orch.rag_engine.retrieve(question)
        rag_context = orch.rag_engine.build_context_string(retrieved_docs)
        sources = [doc.get("source") for doc in retrieved_docs if doc.get("source")]
    except Exception:
        rag_context = "No internal runbooks were retrievable. Use standard MPLS/SD-WAN troubleshooting procedures."
        sources = []

    incident_json = None
    latest = _load_latest_incident()
    if latest and latest.get("incident_details"):
        try:
            incident_json = json.dumps(latest["incident_details"], indent=2)
        except Exception:
            incident_json = None

    # 1. Pull past memory context BEFORE generating the answer (Fast)
    mem_context = orch.memory_engine.get_operator_context(
        operator_id=operator_id, 
        query=question
    )

    # 2. Generate the chat answer directly via the LLM Engine
    # (This bypasses the blocking handle_chat_with_memory wrapper)
    answer = orch.llm_engine.generate_chat_answer(
        question=question,
        rag_context=rag_context,
        memory_context=mem_context,
        incident_json=incident_json
    )

    # 3. Offload the heavy Mem0 fact extraction to a background thread
    background_tasks.add_task(
        orch.memory_engine.add_interaction_memory,
        operator_id=operator_id,
        query=question,
        response=answer
    )

    # 4. Return the answer to Streamlit instantly!
    return ChatResponse(answer=answer, sources=sources)

@router.post("/incidents/{incident_id}/note")
async def save_incident_note(incident_id: str, payload: NotePayload):
    incidents_dir = os.path.join(base_dir, "output", "incidents")
    
    # Locate the correct JSON file on disk
    filepath = os.path.join(incidents_dir, f"{incident_id}.json")
    
    # Fallback lookup in case the files are named with unexpected prefixes/timestamps
    if not os.path.exists(filepath):
        for filename in os.listdir(incidents_dir):
            if incident_id in filename and filename.endswith(".json"):
                filepath = os.path.join(incidents_dir, filename)
                break

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Incident log for {incident_id} not found.")

    try:
        # Read current content
        with open(filepath, "r") as fp:
            data = json.load(fp)
        
        # Append or update the human operator note at the root level
        data["operator_notes"] = payload.note
        
        # Write back to disk permanently
        with open(filepath, "w") as fp:
            json.dump(data, fp, indent=2)
            
        return {"status": "success", "message": "Note committed to file system trail."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))