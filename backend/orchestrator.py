import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Import all our custom engines
from backend.predictor import Predictor # Assuming you built this in Step 2
from backend.incident_engine import IncidentEngine
from backend.topology_engine import TopologyEngine
from backend.priority_engine import PriorityEngine
from backend.rag_engine import RagEngine
from backend.llm_engine import LLMEngine
from backend.config import TOPOLOGY_FILE
from backend.topology_engine import TopologyEngine


logger = logging.getLogger(__name__)

class CopilotOrchestrator:
    def __init__(self):
        logger.info("Initializing SD-WAN AI Copilot Orchestrator...")
        
        # Ensure output directories exist for reproducibility (Step 12)
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
        self.incidents_dir = os.path.join(self.output_dir, "incidents")
        os.makedirs(self.incidents_dir, exist_ok=True)

        # Initialize engines
        self.predictor = Predictor()
        self.incident_engine = IncidentEngine()
        # self.topology_engine = TopologyEngine()
        self.topology_engine = TopologyEngine(topology_path=TOPOLOGY_FILE)
        self.priority_engine = PriorityEngine()
        self.rag_engine = RagEngine()
        self.llm_engine = LLMEngine()

    def _save_incident_report(self, incident_id: str, full_report: Dict[str, Any]):
        """Persists the final incident to disk as a JSON artifact."""
        filepath = os.path.join(self.incidents_dir, f"{incident_id}.json")
        try:
            with open(filepath, 'w') as f:
                json.dump(full_report, f, indent=4)
            logger.info(f"Saved complete incident report to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save incident report {incident_id}: {str(e)}")

    def run_pipeline(self, telemetry_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Executes the end-to-end Air-Gapped NOC Workflow.
        """
        try:
            logger.info("--- Starting Copilot Analysis Pipeline ---")

            # 1. Prediction Phase
            logger.info("Step 1: Analyzing telemetry for predictive faults...")
            prediction_raw = self.predictor.analyze_telemetry(telemetry_data)
            if not prediction_raw:
                logger.info("No anomalies detected. Network is stable.")
                return None

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

            # 6. LLM Copilot Phase
            logger.info("Step 6: Generating autonomous NOC advisory...")
            incident_json = incident.model_dump_json(indent=2)
            copilot_advice = self.llm_engine.generate_incident_analysis(
                incident_json=incident_json,
                rag_context=context_string
            )

            # 7. Final Assembly and Output
            final_report = {
                "timestamp": datetime.utcnow().isoformat(),
                "incident_details": incident.to_dict(),
                "retrieved_context_used": [doc.get("source") for doc in retrieved_docs],
                "copilot_analysis": copilot_advice
            }

            self._save_incident_report(incident.incident_id, final_report)
            logger.info("--- Copilot Analysis Pipeline Complete ---")
            
            return final_report

        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
            return {"error": str(e)}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    orchestrator = CopilotOrchestrator()
    print("Orchestrator initialized successfully.")