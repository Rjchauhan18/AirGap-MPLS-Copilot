import os
from pathlib import Path

# =====================================================
# Project Root
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


CLAB_DIR = os.path.join(PROJECT_ROOT, "clab-sdwan-mpls-core")
TOPOLOGY_FILE = os.path.join(CLAB_DIR, "topology-data.json")

# =====================================================
# AI Stack
# =====================================================

AI_STACK = PROJECT_ROOT / "ai_stack"

MODELS_DIR = AI_STACK / "models"

EMBEDDING_MODEL = (
    MODELS_DIR
    / "embeddings"
    / "all-MiniLM-L6-v2"
)

LLM_MODEL_DIR = (
    MODELS_DIR
    / "llm"
    / "Phi-3-mini-4k-instruct-gguf"
)

# =====================================================
# Model Files
# =====================================================

ML_MODEL = (
    PROJECT_ROOT
    / "Model"
    / "predictive_brain.joblib"
)

TELEMETRY_FILE = (
    PROJECT_ROOT
    / "Model"
    / "sdwan_telemetry_test.csv"
)

# =====================================================
# RAG
# =====================================================

RAG_DOCS = PROJECT_ROOT / "rag_docs"

QDRANT_COLLECTION = "sdwan_copilot"

# =====================================================
# Docker Services
# =====================================================

QDRANT_URL = "http://localhost:6333"

OLLAMA_URL = "http://localhost:11434/v1/chat/completions"

OLLAMA_MODEL = "local-model"

# =====================================================
# Output
# =====================================================

OUTPUT_DIR = PROJECT_ROOT / "output"

INCIDENT_DIR = OUTPUT_DIR / "incidents"

REPORT_DIR = OUTPUT_DIR / "reports"

PREDICTION_DIR = OUTPUT_DIR / "predictions"

VALIDATION_DIR = OUTPUT_DIR / "validation"

# =====================================================
# Logging
# =====================================================

LOG_DIR = AI_STACK / "logs"

# =====================================================
# Predictor
# =====================================================

WINDOW_SIZE = 3

CONFIDENCE_THRESHOLD = 0.65