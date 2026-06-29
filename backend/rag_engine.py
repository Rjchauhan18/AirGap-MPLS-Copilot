import os
import logging
from typing import List, Dict, Any

# These must be installed in your environment:
# pip install qdrant-client sentence-transformers
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class RagEngine:
    def __init__(self, collection_name: str = "sdwan_copilot"):
        self.collection_name = collection_name
        
        # Dynamically resolve paths based on your specific project tree
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.qdrant_path = os.path.join(base_dir, "ai_stack", "qdrant_storage")
        self.model_path = os.path.join(base_dir, "ai_stack", "models", "embeddings", "all-MiniLM-L6-v2")
        
        logger.info("Initializing Air-Gapped RAG Engine...")
        try:
            # 1. Load Local Embedding Model (Zero cloud dependency)
            logger.info(f"Loading local embedding model from: {self.model_path}")
            self.embedder = SentenceTransformer(self.model_path)
            
            # 2. Connect to Qdrant Storage
            # If you are using the Qdrant UI, it means the server is running on port 6333.
            # We must connect via URL, otherwise file-locks will hide the collections!
            logger.info("Connecting to Qdrant Server via HTTP...")
            self.qdrant = QdrantClient(url="http://localhost:6333")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG Engine components: {str(e)}")
            raise

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Embeds the user query and retrieves the most relevant documents from Qdrant.
        """
        try:
            logger.debug(f"Embedding query: '{query}'")
            query_vector = self.embedder.encode(query).tolist()
            
            # --- UPDATED QDRANT API CALL ---
            search_results = self.qdrant.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=top_k
            ).points
            # -------------------------------
            
            # Extract payload/metadata defensively
            docs = []
            for hit in search_results:
                # Our ingestion script stores fields directly on payload:
                # - text (chunk)
                # - source_file / source_path
                # Earlier versions used langchain-style page_content/metadata.
                payload = hit.payload or {}
                content = (
                    payload.get("text")
                    or payload.get("page_content")
                    or ""
                )
                source = (
                    payload.get("source_file")
                    or payload.get("source_path")
                    or (payload.get("metadata", {}) or {}).get("source")
                    or "Unknown Runbook"
                )
                docs.append({
                    "score": hit.score,
                    "content": content,
                    "source": source,
                })
            return docs
            
        except Exception as e:
            logger.error(f"Retrieval failed for query '{query}': {str(e)}")
            return []

    def build_context_string(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """
        Formats the retrieved documents into a strict string for the LLM prompt.
        """
        if not retrieved_docs:
            return "No relevant internal documentation found for this incident."
            
        context_parts = ["--- INTERNAL RUNBOOKS AND TOPOLOGY DATA ---"]
        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(f"\n[Source: {doc['source']} | Relevance Match: {doc['score']:.2f}]")
            context_parts.append(doc['content'].strip())
        context_parts.append("\n-------------------------------------------")
        
        return "\n".join(context_parts)

if __name__ == "__main__":
    # Standalone Test
    logging.basicConfig(level=logging.INFO)
    
    try:
        engine = RagEngine()
        test_query = "What is the remediation for BGP route flapping on a PE router?"
        
        print(f"\nTesting Retrieval for query: '{test_query}'")
        results = engine.retrieve(test_query)
        
        if results:
            print("\nGenerated Context Block for LLM:")
            print(engine.build_context_string(results))
        else:
            print("\nNo results found. (Ensure ingest_docs.py has populated your Qdrant storage).")
    except Exception as e:
        print(f"\n[!] Setup Error: {str(e)}")