import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PriorityEngine:
    def __init__(self):
        # Weighting factors for our priority algorithm
        self.weights = {
            "confidence": 0.3,
            "eta_urgency": 0.4, # Time is the most critical factor for a pre-emptive NOC
            "impact": 0.3
        }

    def _calculate_eta_urgency(self, eta_minutes: int) -> float:
        """Inverse relationship: lower ETA = higher urgency score (0-100)"""
        if eta_minutes <= 0:
            return 100.0
        elif eta_minutes >= 60:
            return 10.0
        else:
            # Linear scale from 1 to 60 minutes
            return 100.0 - ((eta_minutes / 60.0) * 90.0)

    def _calculate_impact_score(self, affected_vpns: list, affected_services: list) -> float:
        """Scores impact based on the sheer number of affected network components."""
        score = 0.0
        score += len(affected_vpns) * 15
        score += len(affected_services) * 10
        
        # Cap at 100
        return min(score, 100.0)

    def calculate_priority(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes raw incident metrics and topology impact, returning a final 
        priority score and NOC classification (P1-P4).
        """
        confidence = incident_data.get("confidence", 0.0) # Assume 0-100 scale
        eta = incident_data.get("eta", 60)
        vpns = incident_data.get("affected_vpns", [])
        services = incident_data.get("affected_services", [])

        # 1. Component calculations
        eta_score = self._calculate_eta_urgency(eta)
        impact_score = self._calculate_impact_score(vpns, services)

        # 2. Weighted total score (0 to 100)
        final_score = (
            (confidence * self.weights["confidence"]) +
            (eta_score * self.weights["eta_urgency"]) +
            (impact_score * self.weights["impact"])
        )
        
        # 3. Categorization mapping
        if final_score >= 85:
            severity_tag = "P1 - Critical"
        elif final_score >= 65:
            severity_tag = "P2 - High"
        elif final_score >= 40:
            severity_tag = "P3 - Medium"
        else:
            severity_tag = "P4 - Low"

        logger.info(f"Calculated Priority: {severity_tag} (Score: {final_score:.1f})")

        return {
            "priority_score": round(final_score, 1),
            "severity": severity_tag
        }

if __name__ == "__main__":
    # Standalone Test
    logging.basicConfig(level=logging.INFO)
    engine = PriorityEngine()
    
    mock_incident = {
        "confidence": 94.0,
        "eta": 12, # Just 12 minutes until failure!
        "affected_vpns": ["VPN10-Corp", "VPN30-Secure"],
        "affected_services": ["BGP", "MPLS-TE"]
    }
    
    result = engine.calculate_priority(mock_incident)
    print("\nCalculated Priority Details:")
    print(result)