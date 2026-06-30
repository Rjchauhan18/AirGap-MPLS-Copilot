import pytest
from unittest.mock import patch, Mock
from backend.llm_engine import LLMEngine

@pytest.fixture
def llm_engine():
    return LLMEngine(ollama_url="http://fake-url", model_name="test-model")

def test_build_system_prompt_without_memory(llm_engine):
    prompt = llm_engine._build_system_prompt()
    assert "Enterprise NOC Copilot" in prompt
    assert "[CRITICAL" not in prompt

def test_build_system_prompt_with_memory(llm_engine):
    memory = "Operator prefers CLI commands only."
    prompt = llm_engine._build_system_prompt(memory_context=memory)
    assert "[CRITICAL - PAST OPERATOR PREFERENCES" in prompt
    assert memory in prompt

@patch("backend.llm_engine.requests.post")
def test_generate_incident_analysis_success(mock_post, llm_engine):
    # Setup mock HTTP response
    mock_response = Mock()
    mock_response.json.return_value = {"response": "Mocked LLM Analysis"}
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response

    result = llm_engine.generate_incident_analysis(
        incident_json='{"device": "R1"}',
        rag_context="No issues found."
    )
    
    assert result == "Mocked LLM Analysis"
    mock_post.assert_called_once()
    
    # Verify the payload structure
    args, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["model"] == "test-model"
    assert "R1" in payload["prompt"]

@patch("backend.llm_engine.requests.post")
def test_generate_chat_answer_api_failure(mock_post, llm_engine):
    import requests
    # Simulate Ollama being offline
    mock_post.side_effect = requests.exceptions.ConnectionError("Offline")
    
    result = llm_engine.generate_chat_answer(question="Test?", rag_context="")
    
    assert "Critical Error" in result