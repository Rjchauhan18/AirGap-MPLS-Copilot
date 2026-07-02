import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

# Import our custom engines
from backend.predictor import Predictor 
from backend.incident_engine import IncidentEngine
from backend.topology_engine import TopologyEngine
from backend.priority_engine import PriorityEngine
from backend.rag_engine import RagEngine
from backend.llm_engine import LLMEngine
from backend.memory_engine import MemoryEngine  
from backend.config import (
    TOPOLOGY_FILE,
    OUTPUT_DIR,
    INCIDENT_DIR,
    REPORT_DIR,
    PREDICTION_DIR,
    VALIDATION_DIR,
    DEFAULT_OPERATOR_ID
)

logger = logging.getLogger(__name__)

class CopilotOrchestrator:
    def __init__(self):
        logger.info("Initializing SD-WAN AI Copilot Orchestrator...")
        
        self.output_dir = str(OUTPUT_DIR)
        self.incidents_dir = str(INCIDENT_DIR)
        self.reports_dir = str(REPORT_DIR)
        self.predictions_dir = str(PREDICTION_DIR)
        self.validation_dir = str(VALIDATION_DIR)

        os.makedirs(self.incidents_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.predictions_dir, exist_ok=True)
        os.makedirs(self.validation_dir, exist_ok=True)

        # Initialize engines
        self.predictor = Predictor()
        self.incident_engine = IncidentEngine()
        self.topology_engine = TopologyEngine(topology_path=TOPOLOGY_FILE)
        self.priority_engine = PriorityEngine()
        self.rag_engine = RagEngine()
        self.llm_engine = LLMEngine()
        self.memory_engine = MemoryEngine()  # New Instantiation

    def _save_prediction(self, prediction: Dict[str, Any]):
        try:
            ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            device = str(prediction.get("device", "unknown")).replace("/", "_")
            filename = f"{ts}_{device}.json"
            filepath = os.path.join(self.predictions_dir, filename)
            with open(filepath, "w") as f:
                json.dump(prediction, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save prediction artifact: {e}")

    def _save_incident_report(self, incident_id: str, full_report: Dict[str, Any]):
        filepath = os.path.join(self.incidents_dir, f"{incident_id}.json")
        try:
            with open(filepath, 'w') as f:
                json.dump(full_report, f, indent=4)
            logger.info(f"Saved complete incident report to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save incident report {incident_id}: {str(e)}")

    def _save_report(self, incident_id: str, full_report: Dict[str, Any]):
        filepath = os.path.join(self.reports_dir, f"{incident_id}.json")
        try:
            with open(filepath, "w") as f:
                json.dump(full_report, f, indent=4)
        except Exception as e:
            logger.warning(f"Failed to save report artifact {incident_id}: {e}")

    def handle_chat_with_memory(self, operator_id: str, question: str, rag_context: str, incident_json: str | None = None) -> str:
        """Handles manual chats, extracts history, updates cognitive profiles dynamically."""
        # 1. Fetch relevant memories for this specific operator
        mem_context = self.memory_engine.get_operator_context(operator_id=operator_id, query=question)
        
        # 2. Run synthesis engine pass matching parameters
        answer = self.llm_engine.generate_chat_answer(
            question=question,
            rag_context=rag_context,
            incident_json=incident_json,
            memory_context=mem_context
        )
        
        # 3. Log facts asynchronously into memory storage
        self.memory_engine.add_interaction_memory(operator_id=operator_id, query=question, response=answer)
        return answer

    def run_pipeline(self, telemetry_data: Dict[str, Any], operator_id: str = DEFAULT_OPERATOR_ID) -> Optional[Dict[str, Any]]:
        """Executes the end-to-end Air-Gapped NOC Workflow with memory capabilities."""
        try:
            logger.info("--- Starting Copilot Analysis Pipeline ---")

            # 1. Prediction Phase
            logger.info("Step 1: Analyzing telemetry for predictive faults...")
            prediction_raw = self.predictor.analyze_telemetry(telemetry_data)
            if not prediction_raw:
                logger.info("No anomalies detected. Network is stable.")
                return None
            self._save_prediction(prediction_raw)

            # 2. Incident Creation Phase
            logger.info("Step 2: Structuring prediction into standard Incident...")
            incident = self.incident_engine.process_prediction(prediction_raw)

            # 3. Topology & Impact Phase
            logger.info("Step 3: Calculating blast radius and topology impact...")
            impact = self.topology_engine.assess_impact(incident.device)
            incident.affected_vpns = impact.get("affected_vpns", [])
            incident.affected_services = impact.get("affected_services", [])

            # 4. Priority Scoring Phase
            logger.info("Step 4: Scoring incident urgency and priority...")
            priority_data = self.priority_engine.calculate_priority(incident.to_dict())
            incident.priority_score = priority_data["priority_score"]
            incident.severity = priority_data["severity"]

            # 5. RAG Retrieval Phase
            logger.info("Step 5: Retrieving air-gapped runbooks...")
            search_query = f"remediation for {incident.fault_type} on {incident.device} affecting {', '.join(incident.affected_services)}"
            retrieved_docs = self.rag_engine.retrieve(search_query)
            context_string = self.rag_engine.build_context_string(retrieved_docs)

            # Fetch background operator contexts before inference
            memory_context = self.memory_engine.get_operator_context(operator_id=operator_id, query=search_query)

            # 6. LLM Copilot Phase
            logger.info("Step 6: Generating autonomous NOC advisory...")
            incident_json = incident.model_dump_json(indent=2)
            copilot_advice = self.llm_engine.generate_incident_analysis(
                incident_json=incident_json,
                rag_context=context_string,
                memory_context=memory_context
            )

            # 7. Final Assembly and Output
            final_report = {
                "timestamp": datetime.utcnow().isoformat(),
                "incident_details": incident.to_dict(),
                "retrieved_context_used": [doc.get("source") for doc in retrieved_docs],
                "copilot_analysis": copilot_advice
            }

            self._save_incident_report(incident.incident_id, final_report)
            self._save_report(incident.incident_id, final_report)
            
            # Commit the analysis transaction pattern into mem0 layer
            self.memory_engine.add_interaction_memory(operator_id=operator_id, query=search_query, response=copilot_advice)
            
            logger.info("--- Copilot Analysis Pipeline Complete ---")
            return final_report

        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
            return {"error": str(e)}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    orchestrator = CopilotOrchestrator()
    print("Orchestrator initialized successfully.")