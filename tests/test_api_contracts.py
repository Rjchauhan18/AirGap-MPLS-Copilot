import os


def test_dashboard_env_default_api_url():
    # Streamlit dashboard uses this environment variable.
    assert os.getenv("COPILOT_API_URL", "http://localhost:8000").startswith("http")


def test_status_schema_import():
    from api.schemas import StatusResponse  # noqa: F401


def test_chat_schema_import():
    from api.schemas import ChatRequest, ChatResponse  # noqa: F401

