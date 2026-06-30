import pytest
from unittest.mock import patch, MagicMock
from backend.orchestrator import CopilotOrchestrator

@pytest.fixture
def patched_orchestrator(mocker):
    """Mocks all inner engines so orchestrator logic can be tested in a vacuum."""
    mocker.patch("backend.orchestrator.Predictor")
    mocker.patch("backend.orchestrator.IncidentEngine")
    mocker.patch("backend.orchestrator.TopologyEngine")
    mocker.patch("backend.orchestrator.PriorityEngine")
    mocker.patch("backend.orchestrator.RagEngine")
    mocker.patch("backend.orchestrator.LLMEngine")
    mocker.patch("backend.orchestrator.MemoryEngine")
    
    # We also mock OS file writes to avoid creating garbage files during tests
    mocker.patch("backend.orchestrator.os.makedirs")
    mocker.patch("builtins.open", mocker.mock_open())
    
    orch = CopilotOrchestrator()
    return orch

def test_run_pipeline_no_prediction(patched_orchestrator):
    patched_orchestrator.predictor.analyze_telemetry.return_value = None
    
    result = patched_orchestrator.run_pipeline({"cpu": 10})
    assert result is None

def test_run_pipeline_full_flow(patched_orchestrator, mocker):
    # Setup mock data flow
    patched_orchestrator.predictor.analyze_telemetry.return_value = {"anomaly": True}
    
    mock_incident = MagicMock()
    mock_incident.device = "PE-1"
    mock_incident.fault_type = "BGP Drop"
    mock_incident.incident_id = "INC-TEST"
    mock_incident.to_dict.return_value = {"id": "INC-TEST"}
    patched_orchestrator.incident_engine.process_prediction.return_value = mock_incident
    
    patched_orchestrator.topology_engine.assess_impact.return_value = {
        "affected_vpns": ["VPN1"], "affected_services": ["Web"]
    }
    patched_orchestrator.priority_engine.calculate_priority.return_value = {
        "priority_score": 95, "severity": "CRITICAL"
    }
    
    patched_orchestrator.rag_engine.retrieve.return_value = [{"source": "Doc1"}]
    patched_orchestrator.memory_engine.get_operator_context.return_value = "Memory Data"
    patched_orchestrator.llm_engine.generate_incident_analysis.return_value = "Root Cause Analysis"

    # Execute
    result = patched_orchestrator.run_pipeline({"cpu": 99}, operator_id="test_op")

    # Assertions
    assert result is not None
    assert result["incident_details"]["id"] == "INC-TEST"
    assert result["copilot_analysis"] == "Root Cause Analysis"
    
    # Verify memory was committed
    patched_orchestrator.memory_engine.add_interaction_memory.assert_called_once()