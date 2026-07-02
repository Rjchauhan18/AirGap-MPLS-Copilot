#!/bin/bash
set -e

echo "=================================================="
echo "Starting Setup: AirGap-MPLS-Copilot"
echo "=================================================="

echo "[1/7] Creating local directory structure..."
mkdir -p ai_stack/models/embeddings/all-MiniLM-L6-v2
mkdir -p ai_stack/models/llm/Phi-3-mini-4k-instruct-gguf
mkdir -p ai_stack/qdrant_storage ai_stack/ollama_storage ai_stack/logs
mkdir -p output/incidents

echo "[2/7] Downloading AI Models..."

# 1. Download LLM Model via wget
if [ ! -f "ai_stack/models/llm/Phi-3-mini-4k-instruct-gguf/model.gguf" ]; then
    echo "Downloading LLM (Phi-3-mini-4k-instruct-q4.gguf)..."
    wget -q --show-progress -O ./ai_stack/models/llm/Phi-3-mini-4k-instruct-gguf/model.gguf https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf
else
    echo "LLM model already exists. Skipping download."
fi

# 2. Download Embedding Model via Python (Ensures all required config/tokenizer files are correctly structured)
echo "Downloading Embedding Model (all-MiniLM-L6-v2)..."
cat << 'EOF' > scripts/download_embeddings_tmp.py
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer   
from fastembed import SparseTextEmbedding
import tiktoken

# Define base paths
BASE = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE / "ai_stack" / "models"
EMBED_DIR = MODELS_DIR / "embeddings" / "all-MiniLM-L6-v2"
FASTEMBED_CACHE_DIR = MODELS_DIR / "embeddings" / "fastembed_cache"
TIKTOKEN_DIR = MODELS_DIR / "tiktoken_cache"

# Create directories
EMBED_DIR.mkdir(parents=True, exist_ok=True)
FASTEMBED_CACHE_DIR.mkdir(parents=True, exist_ok=True)
TIKTOKEN_DIR.mkdir(parents=True, exist_ok=True)

# 1. Download SentenceTransformer (Dense)
print(f"Downloading all-MiniLM-L6-v2 to {EMBED_DIR}...")
model = SentenceTransformer("all-MiniLM-L6-v2")
model.save(str(EMBED_DIR))
print("✅ Dense model saved.")

# 2. Download FastEmbed (Sparse)
print(f"Downloading Qdrant/bm25 to {FASTEMBED_CACHE_DIR}...")
# Setting cache_dir here forces it to download to your local folder
bm25 = SparseTextEmbedding(model_name="Qdrant/bm25", cache_dir=str(FASTEMBED_CACHE_DIR))
print("✅ Sparse model saved.")

# 3. Download Tiktoken
print(f"Downloading Tiktoken to {TIKTOKEN_DIR}...")
os.environ["TIKTOKEN_CACHE_DIR"] = str(TIKTOKEN_DIR)
_ = tiktoken.get_encoding("cl100k_base")
print("✅ Tiktoken saved.")
EOF

# Execution blocks here and waits until the Python process finishes fully
python scripts/download_embeddings_tmp.py

# Cleanup happens only after python successfully finishes downloading
rm -f scripts/download_embeddings_tmp.py
echo "Temporary setup download script cleaned up safely."

echo "[3/7] Starting Docker Services (Ollama & Qdrant)..."
if ! docker info >/dev/null 2>&1; then
  echo "Docker is not running. Please start Docker first."
  exit 1
fi

if ! command -v docker compose >/dev/null 2>&1; then
  echo "docker compose is not available."
  exit 1
fi

docker compose -f docker-compose.ai.yml up -d
echo "Waiting 10 seconds for services to initialize..."
sleep 10

echo "[4/7] Configuring and Building 'local-model' in Ollama..."
OLLAMA_ID=$(docker ps -qf "ancestor=ollama/ollama")

if [ -n "$OLLAMA_ID" ]; then
    echo "Found Ollama container (ID: $OLLAMA_ID). Copying model and Modelfile..."
    docker cp ai_stack/models/llm/Phi-3-mini-4k-instruct-gguf/model.gguf $OLLAMA_ID:/tmp/model.gguf
    
    echo "FROM /tmp/model.gguf" > ai_stack/Modelfile.tmp
    docker cp ai_stack/Modelfile.tmp $OLLAMA_ID:/tmp/Modelfile
    
    echo "Building local-model..."
    docker exec $OLLAMA_ID ollama create local-model -f /tmp/Modelfile
    
    # Cleanup tmp files
    docker exec $OLLAMA_ID rm /tmp/model.gguf /tmp/Modelfile
    rm ai_stack/Modelfile.tmp
else
    echo "Could not find Ollama container by ancestor. Attempting build via docker compose..."
    echo "FROM /ai_stack/models/llm/Phi-3-mini-4k-instruct-gguf/model.gguf" > ai_stack/Modelfile
    docker compose -f docker-compose.ai.yml exec ollama ollama create local-model -f /ai_stack/Modelfile
fi

echo "[5/7] Populating Vector Database (RAG Ingestion)..."
if [ -f "scripts/ingest_docs.py" ]; then
    python scripts/ingest_docs.py
    echo "Ingestion completed successfully."
else
    echo "Warning: scripts/ingest_docs.py not found. Skipping vector DB creation."
fi

echo "[6/7] Starting Network Simulation..."
if [ -f "network_simulation.sh" ]; then
    chmod +x network_simulation.sh
    ./network_simulation.sh
    echo "Network Simulation started."
else
    echo "Warning: network_simulation.sh not found."
fi

echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "Dashboards:"
echo " - Qdrant Web UI: http://localhost:6333/dashboard"
echo " - Ollama API:    http://localhost:11434"
echo ""
echo "[7/7] Project Execution Guide:"
echo ""
echo "To run the project, open separate terminal tabs and execute the following:"
echo ""
echo "1. Start the Backend API / Copilot Server:"
echo "   python api/app.py"
echo ""
echo "2. Start the Telemetry Agent (Continuous Monitoring):"
echo "   python telemetry_agent.py"
echo ""
echo "3. Trigger Autonomous Copilot Analysis (Inject Faults):"
echo "   chmod +x Bulk_fault_injector.sh"
echo "   ./Bulk_fault_injector.sh"
echo "=================================================="