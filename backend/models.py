from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Prediction(BaseModel):
    """Data contract for the output coming from predictor.py"""
    site: str
    device: str
    confidence: float
    fault_type: str
    eta: int
    signals: List[str] = Field(default_factory=list)

class Incident(BaseModel):
    """Data contract for the official Incident object"""
    incident_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    device: str
    site: str
    fault_type: str
    severity: str
    priority_score: Optional[float] = None
    eta: int
    confidence: float
    affected_services: List[str] = Field(default_factory=list)
    affected_vpns: List[str] = Field(default_factory=list)
    raw_signals: List[str] = Field(default_factory=list)

    def to_dict(self):
        """Helper to safely serialize for the LLM or frontend"""
        return self.model_dump(mode='json')