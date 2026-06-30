import os
import logging
from urllib.parse import urlparse
from mem0 import Memory
from backend.config import (
    QDRANT_URL,
    OLLAMA_URL,
    OLLAMA_MODEL,
    EMBEDDING_MODEL,
    QDRANT_MEMORY_COLLECTION
)

logger = logging.getLogger(__name__)

# Parse your existing config values dynamically
parsed_qdrant = urlparse(QDRANT_URL)
QDRANT_HOST = parsed_qdrant.hostname or "localhost"
QDRANT_PORT = parsed_qdrant.port or 6333

# Strip out endpoint suffixes to find Ollama's base URL route
OLLAMA_BASE = OLLAMA_URL.split("/v1")[0]

mem0_config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": QDRANT_HOST,
            "port": QDRANT_PORT,
            "collection_name": QDRANT_MEMORY_COLLECTION,
            "embedding_model_dims": 384,  # Dimension size for all-MiniLM-L6-v2
        }
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": OLLAMA_MODEL,
            "ollama_base_url": OLLAMA_BASE,
            "temperature": 0.0,
        }
    },
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": str(EMBEDDING_MODEL),  # Points straight to your local directory
        }
    }
}

class MemoryEngine:
    def __init__(self):
        logger.info("Initializing Local Air-Gapped Mem0 Engine...")
        # Set dummy key to bypass fallback validation checks inside mem0
        os.environ["OPENAI_API_KEY"] = "fully-offline"
        try:
            self.memory = Memory.from_config(mem0_config)
            logger.info(f"Mem0 successfully connected to Qdrant collection: {QDRANT_MEMORY_COLLECTION}")
        except Exception as e:
            logger.error(f"Failed to initialize Mem0 memory wrapper: {e}")
            self.memory = None

    def add_interaction_memory(self, operator_id: str, query: str, response: str):
        """Asynchronously converts explicit feedback or conversational habits into facts."""
        if not self.memory:
            return
        
        messages = [
            {"role": "user", "content": query},
            {"role": "assistant", "content": response}
        ]
        try:
            self.memory.add(messages, user_id=operator_id)
            logger.info(f"Updated operational cognitive profile memory layer for {operator_id}")
        except Exception as e:
            logger.warning(f"Failed to store conversation snapshot to memory context: {e}")

    def get_operator_context(self, operator_id: str, query: str) -> str:
        """Extracts operating rules, constraints, or preferences logged in past sessions."""
        if not self.memory:
            return ""
        try:
            # UPDATED SYNTAX:
            results = self.memory.search(query, filters={"user_id": operator_id})
            if not results:
                return ""
            
            facts = []
            for item in results:
                # Handle cases where results are dicts or objects depending on mem0 version
                fact = item.get("memory") if isinstance(item, dict) else getattr(item, "memory", None)
                if fact:
                    facts.append(f"- {fact}")
            
            return "\n".join(facts)
        except Exception as e:
            logger.error(f"Failed to pull background memory context: {e}")
            return ""