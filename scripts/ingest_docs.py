import os
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent.parent
RAG_DIR = BASE_DIR / "rag_docs"
DOC_DIRS = {
    "topology": RAG_DIR / "topology",
    "runbook": RAG_DIR / "runbooks",
    "incident": RAG_DIR / "incidents",
}

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "sdwan_copilot")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
EMBED_MODEL = os.getenv("EMBED_MODEL", "./ai_stack/models/embeddings/all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "900"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))

client = QdrantClient(url=QDRANT_URL)
model = SentenceTransformer(EMBED_MODEL)


def read_file(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() == ".json":
        try:
            obj = json.loads(text)
            return json.dumps(obj, indent=2, ensure_ascii=False)
        except Exception:
            return text
    return text


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    text = text.replace("\r\n", "\n").strip()
    if not text:
        return []

    chunks = []
    start = 0
    n = len(text)

    while start < n:
        end = min(n, start + size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        start = max(end - overlap, start + 1)

    return chunks


def infer_site(file_path: Path):
    s = str(file_path).lower()
    if "branch" in s or "br_" in s or "_br" in s or "edge-br" in s:
        return "branch"
    if "dc" in s or "datacenter" in s or "edge-dc" in s:
        return "datacenter"
    if "hub" in s:
        return "hub"
    if "p-core" in s or "provider" in s:
        return "provider"
    return "unknown"


def infer_device_role(file_path: Path):
    s = str(file_path).lower()
    if "edge-br" in s:
        return "ce"
    if "edge-dc" in s:
        return "ce"
    if "pe-br" in s:
        return "pe"
    if "pe-dc" in s:
        return "pe"
    if "p-core" in s:
        return "p-core"
    return "unknown"


def infer_protocol(file_path: Path, content: str):
    s = f"{file_path.name.lower()} {content.lower()}"
    if "bgp" in s:
        return "bgp"
    if "ospf" in s:
        return "ospf"
    if "mpls" in s:
        return "mpls"
    if "ipsec" in s or "tunnel" in s:
        return "ipsec"
    return "unknown"


def infer_fault_type(file_path: Path, content: str):
    s = f"{file_path.name.lower()} {content.lower()}"
    if "congestion" in s or "utilization" in s or "jitter" in s or "latency" in s:
        return "congestion"
    if "bgp" in s or "route flap" in s or "neighbor reset" in s or "route churn" in s:
        return "routing_instability"
    if "tunnel" in s or "packet loss" in s or "rekey" in s:
        return "tunnel_degradation"
    if "policy drift" in s or "misconfiguration" in s or "controller" in s:
        return "policy_drift"
    if "ospf" in s or "convergence" in s:
        return "routing_instability"
    return "unknown"


def infer_severity(doc_type: str, content: str):
    s = content.lower()
    if doc_type == "incident":
        return "high"
    if "critical" in s:
        return "critical"
    if "high" in s:
        return "high"
    if "medium" in s:
        return "medium"
    if "low" in s:
        return "low"
    return "info"


def infer_title(path: Path, content: str):
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("_", " ").title()


def load_documents():
    docs = []
    for doc_type, folder in DOC_DIRS.items():
        if not folder.exists():
            continue
        for path in folder.glob("*"):
            if path.suffix.lower() not in [".md", ".txt", ".log", ".json"]:
                continue
            content = read_file(path)
            if not content.strip():
                continue
            docs.append((doc_type, path, content))
    return docs


def ensure_collection():
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        sample_vec = model.encode(["sample"], normalize_embeddings=True)[0]
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=len(sample_vec), distance=Distance.COSINE),
        )


def main():
    docs = load_documents()
    if not docs:
        print("No documents found in rag_docs/")
        return

    ensure_collection()

    points = []
    now = datetime.now(timezone.utc).isoformat()

    for doc_type, path, content in docs:
        title = infer_title(path, content)
        site = infer_site(path)
        device_role = infer_device_role(path)
        protocol = infer_protocol(path, content)
        fault_type = infer_fault_type(path, content)
        severity = infer_severity(doc_type, content)
        tags = [
            "sdwan",
            "mpls",
            "airgapped",
            doc_type,
            site,
            device_role,
            protocol,
            fault_type,
        ]

        chunks = chunk_text(content)
        if not chunks:
            continue

        vectors = model.encode(chunks, normalize_embeddings=True)

        for idx, (chunk, vec) in enumerate(zip(chunks, vectors)):
            payload = {
                "doc_id": f"{path.stem}",
                "chunk_id": idx,
                "source_file": path.name,
                "source_path": str(path),
                "doc_type": doc_type,
                "site": site,
                "device_role": device_role,
                "protocol": protocol,
                "fault_type": fault_type,
                "severity": severity,
                "tags": tags,
                "title": title,
                "text": chunk,
                "created_at": now,
            }
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vec.tolist(),
                    payload=payload,
                )
            )

    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"Ingested {len(points)} chunks into collection '{COLLECTION_NAME}'")
    else:
        print("No chunks generated.")

if __name__ == "__main__":
    main()