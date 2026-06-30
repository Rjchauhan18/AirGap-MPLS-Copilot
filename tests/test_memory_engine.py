import pytest
from unittest.mock import patch, MagicMock
from backend.memory_engine import MemoryEngine

@pytest.fixture
@patch("backend.memory_engine.Memory.from_config")
def memory_engine(mock_from_config):
    mock_instance = MagicMock()
    mock_from_config.return_value = mock_instance
    engine = MemoryEngine()
    engine.memory = mock_instance
    return engine

def test_add_interaction_memory(memory_engine):
    memory_engine.add_interaction_memory("op-1", "How do I fix this?", "Restart BGP.")
    
    memory_engine.memory.add.assert_called_once()
    args, kwargs = memory_engine.memory.add.call_args
    messages = args[0]
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert kwargs["user_id"] == "op-1"

def test_get_operator_context_with_results(memory_engine):
    # mem0 search returns a list of dictionary/object representations
    memory_engine.memory.search.return_value = [
        {"memory": "Operator prefers JSON format."},
        {"memory": "Operator handles VPN 2 only."}
    ]
    
    context = memory_engine.get_operator_context("op-1", "status update")
    
    assert "Operator prefers JSON format." in context
    assert "Operator handles VPN 2 only." in context
    assert context.startswith("- ")

def test_get_operator_context_empty(memory_engine):
    memory_engine.memory.search.return_value = []
    
    context = memory_engine.get_operator_context("op-1", "status update")
    
    assert context == ""