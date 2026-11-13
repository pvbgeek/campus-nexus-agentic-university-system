"""Real dense semantic retrieval: FastEmbed ONNX embeddings and on-disk Qdrant."""
from functools import lru_cache
from pathlib import Path
import hashlib
import json
import os
import uuid

from filelock import FileLock
from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("CAMPUS_NEXUS_DATA", str(ROOT / "data"))).resolve()
MODEL = "BAAI/bge-small-en-v1.5"
COLLECTION_PREFIX = "support_policy_"


@lru_cache(maxsize=1)
def embedding_model():
    return TextEmbedding(model_name=MODEL, cache_dir=str(ROOT / ".cache/embeddings"), threads=2)


def paths():
    DATA.mkdir(parents=True, exist_ok=True)
    return DATA / "policy-index.json", DATA / "policy-index.lock"


def build_policy_index(source=None):
    source = Path(source or ROOT / "docs/policies/current-policy.md")
    text = source.read_text(encoding="utf-8")
    digest = hashlib.sha256(text.encode()).hexdigest()
    chunks = []
    for paragraph in text.split("\n\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        # Keep chunks within the small model's context window.
        for offset in range(0, len(paragraph), 1200):
            chunks.append(paragraph[offset:offset+1200])
    if not chunks:
        raise ValueError("Cannot index an empty policy")
    vectors = list(embedding_model().embed(chunks))
    manifest_path, lock_path = paths()
    collection = COLLECTION_PREFIX + digest[:20]
    with FileLock(str(lock_path), timeout=60):
        client = QdrantClient(path=str(DATA / "vectors"))
        try:
            if not client.collection_exists(collection):
                client.create_collection(collection, vectors_config=models.VectorParams(
                    size=len(vectors[0]), distance=models.Distance.COSINE))
            points = [models.PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_URL, digest+":"+str(i))),
                vector=vector.tolist(),
                payload=dict(text=chunk, source=source.name, source_sha256=digest,
                             approved=True, policy_version="refund-v1", chunk_id=i),
            ) for i, (chunk, vector) in enumerate(zip(chunks, vectors))]
            client.upsert(collection_name=collection, points=points, wait=True)
            manifest = dict(collection=collection, embedding_model=MODEL, dimensions=len(vectors[0]),
                            source=source.name, source_sha256=digest, chunks=len(chunks))
            temp = manifest_path.with_suffix(".tmp")
            temp.write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
            temp.replace(manifest_path)
            return manifest
        finally:
            client.close()


def search_policy(query, limit=3):
    if not isinstance(query, str) or not query.strip() or len(query) > 2000:
        raise ValueError("Policy query must contain 1 to 2000 characters")
    if not 1 <= limit <= 5:
        raise ValueError("Retrieval limit must be between 1 and 5")
    manifest_path, lock_path = paths()
    if not manifest_path.is_file():
        raise RuntimeError("Build the policy index with scripts/build_policy_index.py first")
    vector = list(embedding_model().query_embed([query]))[0].tolist()
    with FileLock(str(lock_path), timeout=60):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        client = QdrantClient(path=str(DATA / "vectors"))
        try:
            result = client.query_points(collection_name=manifest["collection"], query=vector,
                query_filter=models.Filter(must=[models.FieldCondition(
                    key="approved", match=models.MatchValue(value=True))]), limit=limit)
            return [dict(point_id=str(point.id), score=float(point.score), **point.payload)
                    for point in result.points]
        finally:
            client.close()
