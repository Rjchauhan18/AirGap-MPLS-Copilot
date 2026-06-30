import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import your router
from api.routes import router

# Setup a dummy app for testing
app = FastAPI()
app.include_router(router)
client = TestClient(app)

@pytest.fixture
def mock_orchestrator(mocker):
    """Mocks the global orchestrator to prevent real model initialization."""
    mock_orch = MagicMock()
    # Mock status attributes
    mock_orch.predictor.model = True 
    mocker.patch("api.routes.get_orchestrator", return_value=mock_orch)
    return mock_orch

def test_status_endpoint(mock_orchestrator, mocker):
    # Mock the incident count helper
    mocker.patch("api.routes._count_incidents", return_value=5)
    
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["api"] == "ok"
    assert data["orchestrator_initialized"] is True
    assert data["incidents_count"] == 5

def test_ingest_telemetry_normal(mock_orchestrator):
    mock_orchestrator.predictor.analyze_telemetry.return_value = None
    
    payload = {
        "device": "PE-1",
        "metrics": {"cpu": 20.0, "latency": 5.0}
    }
    response = client.post("/ingest_telemetry", json=payload)
    
    assert response.status_code == 200
    assert response.json()["status"] == "normal"

def test_chat_endpoint_missing_question():
    response = client.post("/chat", json={"question": ""})
    # FastAPI/Pydantic validation should catch the empty string
    assert response.status_code == 422 

def test_chat_endpoint_success(mock_orchestrator, mocker):
    mocker.patch("api.routes._load_latest_incident", return_value=None)
    mock_orchestrator.rag_engine.retrieve.return_value = [{"source": "Runbook A"}]
    mock_orchestrator.rag_engine.build_context_string.return_value = "Mock Context"
    mock_orchestrator.handle_chat_with_memory.return_value = "This is the Copilot answer."

    response = client.post("/chat", json={"question": "Why is the VPN down?", "operator_id": "test_op"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "This is the Copilot answer."
    assert "Runbook A" in data["sources"]