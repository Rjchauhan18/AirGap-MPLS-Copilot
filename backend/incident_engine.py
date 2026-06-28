import logging
from datetime import datetime
from typing import Dict, Any
from backend.models import Prediction, Incident

logger = logging.getLogger(__name__)

class IncidentEngine:
    def __init__(self):
        # In a production system, this would be a database sequence.
        # For the hackathon, a simple in-memory counter works perfectly.
        self._incident_counter = 1000

    def _generate_incident_id(self) -> str:
        """Generates a unique, NOC-style incident ID."""
        self._incident_counter += 1
        return f"INC-{self._incident_counter}"

    def _determine_baseline_severity(self, confidence: float, eta: int) -> str:
        """
        Calculates a baseline severity. 
        Note: The Priority Engine will refine this later based on impact.
        """
        if confidence >= 0.90 and eta <= 15:
            return "Critical"
        elif confidence >= 0.80 and eta <= 30:
            return "High"
        elif confidence >= 0.70:
            return "Medium"
        else:
            return "Low"

    def process_prediction(self, prediction_data: Dict[str, Any]) -> Incident:
        """
        Converts a raw prediction dictionary into a validated Incident object.
        """
        try:
            # 1. Validate incoming data using Pydantic
            prediction = Prediction(**prediction_data)
            logger.info(f"Processing prediction for device: {prediction.device}")

            # 2. Generate NOC identifiers and baseline metrics
            incident_id = self._generate_incident_id()
            baseline_severity = self._determine_baseline_severity(
                confidence=prediction.confidence, 
                eta=prediction.eta
            )

            # 3. Construct the official Incident object
            # Affected services/VPNs are left empty here; the Topology Engine will fill them.
            incident = Incident(
                incident_id=incident_id,
                device=prediction.device,
                site=prediction.site,
                fault_type=prediction.fault_type,
                severity=baseline_severity,
                eta=prediction.eta,
                confidence=prediction.confidence * 100, # Convert to readable percentage
                raw_signals=prediction.signals
            )

            logger.info(f"Successfully created {incident_id} ({incident.severity})")
            return incident

        except Exception as e:
            logger.error(f"Failed to process prediction into incident: {str(e)}")
            raise

if __name__ == "__main__":
    # Quick internal test to ensure the module works standalone
    logging.basicConfig(level=logging.INFO)
    engine = IncidentEngine()
    
    mock_prediction = {
        "site": "Delhi-Hub",
        "device": "PE2",
        "confidence": 0.94,
        "fault_type": "Congestion buildup",
        "eta": 12,
        "signals": ["Interface utilization > 85%", "Jitter increasing"]
    }
    
    new_incident = engine.process_prediction(mock_prediction)
    print(new_incident.model_dump_json(indent=2))