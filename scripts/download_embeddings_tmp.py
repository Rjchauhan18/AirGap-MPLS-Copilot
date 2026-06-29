import os
from pathlib import Path
from sentence_transformers import SentenceTransformer

BASE = Path(__file__).resolve().parent.parent
EMBED_DIR = BASE / "ai_stack" / "models" / "embeddings" / "all-MiniLM-L6-v2"
EMBED_DIR.mkdir(parents=True, exist_ok=True)

print(f"Saving embedding model to: {EMBED_DIR}")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
embed_model.save(str(EMBED_DIR))
