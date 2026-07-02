import os
from pathlib import Path


# =====================================================
# 1. Project Root & Core Paths
# =====================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
AI_STACK = PROJECT_ROOT / "ai_stack"
MODELS_DIR = AI_STACK / "models"
FASTEMBED_CACHE_DIR = MODELS_DIR / "embeddings" / "fastembed_cache"
TIKTOKEN_CACHE_DIR = MODELS_DIR / "tiktoken_cache"

# =====================================================
# 2. STRICT AIR-GAPPED ENFORCEMENT FLAGS
# =====================================================
# These MUST be set before any other AI libraries are imported

# 1. Stop HuggingFace from checking the internet for model updates
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

# 2. Force FastEmbed to strictly use your downloaded bm25 local cache
os.environ["FASTEMBED_CACHE_PATH"] = str(FASTEMBED_CACHE_DIR)

# 3. Force Tiktoken (used by mem0) to strictly use the local vocabulary file
os.environ["TIKTOKEN_CACHE_DIR"] = str(TIKTOKEN_CACHE_DIR)

# 4. Disable Mem0 telemetry
os.environ["MEM0_TELEMETRY"] = "false"
try:
    import posthog
    posthog.disabled = True
except ImportError:
    pass

# =====================================================
# 3. Model Paths (Used by Mem0 & RAG)
# =====================================================
EMBEDDING_MODEL = MODELS_DIR / "embeddings" / "all-MiniLM-L6-v2"
LLM_MODEL_DIR = MODELS_DIR / "llm" / "Phi-3-mini-4k-instruct-gguf"

CLAB_DIR = os.path.join(PROJECT_ROOT, "clab-sdwan-mpls-core")
TOPOLOGY_FILE = os.path.join(CLAB_DIR, "topology-data.json")

QDRANT_MEMORY_COLLECTION = "sdwan_memories"
DEFAULT_OPERATOR_ID = "operator_alpha"


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