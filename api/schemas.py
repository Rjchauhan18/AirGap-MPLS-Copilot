from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    api: str = "ok"
    orchestrator_initialized: bool
    model_loaded: bool
    qdrant_url: str
    ollama_url: str
    collection: str
    incidents_count: int = 0


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    device: Optional[str] = None
    incident_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = Field(default_factory=list)


class TopologyResponse(BaseModel):
    topology: Dict[str, Any]
    impact: Optional[Dict[str, Any]] = None

