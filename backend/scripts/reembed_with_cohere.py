"""
One-time migration: re-embeds all chunks using Cohere's Embed API instead of
the local sentence-transformers model, then re-uploads them to Qdrant.

Run this ONCE, locally, after switching the backend to Cohere. It targets
whichever Qdrant instance the env vars below point to — point it at your
Qdrant Cloud cluster (the same one Render will use), not your local Docker one.

Usage:
    pip install cohere qdrant-client numpy

    Windows (cmd):
        set COHERE_API_KEY=your_cohere_key
        set QDRANT_URL=https://your-cluster-url.cloud.qdrant.io:6333
        set QDRANT_API_KEY=your_qdrant_key
        python reembed_with_cohere.py

    Mac/Linux:
        export COHERE_API_KEY=your_cohere_key
        export QDRANT_URL=https://your-cluster-url.cloud.qdrant.io:6333
        export QDRANT_API_KEY=your_qdrant_key
        python reembed_with_cohere.py
"""
import json
import os
from pathlib import Path

import cohere
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

COHERE_API_KEY = os.environ["COHERE_API_KEY"]
QDRANT_URL = os.environ["QDRANT_URL"]
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")
COLLECTION_NAME = "pdf_chunks"
EMBED_MODEL = "embed-english-v3.0"
BATCH_SIZE = 90  # stay safely under Cohere's per-call input limit

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

co = cohere.Client(COHERE_API_KEY)
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60)

with open(DATA_DIR / "chunk_store.json") as f:
    chunk_store = json.load(f)

texts = [c["text"] for c in chunk_store]
print(f"Re-embedding {len(texts)} chunks with Cohere ({EMBED_MODEL})...")

all_embeddings = []
for i in range(0, len(texts), BATCH_SIZE):
    batch = texts[i : i + BATCH_SIZE]
    response = co.embed(texts=batch, model=EMBED_MODEL, input_type="search_document")
    all_embeddings.extend(response.embeddings)
    print(f"  embedded {min(i + BATCH_SIZE, len(texts))}/{len(texts)}")

embeddings = np.array(all_embeddings, dtype=np.float32)
np.save(DATA_DIR / "embeddings.npy", embeddings)
print(f"Saved new embeddings.npy with shape {embeddings.shape}")

# Cohere's vectors are a different size than MiniLM's — the old collection
# can't just be appended to, it has to be replaced entirely.
print(f"Recreating Qdrant collection '{COLLECTION_NAME}'...")
qdrant.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=embeddings.shape[1], distance=Distance.COSINE),
)

points = [
    PointStruct(
        id=i,
        vector=embeddings[i].tolist(),
        payload={"text": chunk_store[i]["text"], "page": chunk_store[i]["page"]},
    )
    for i in range(len(chunk_store))
]
qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
print(f"Uploaded {len(points)} vectors to Qdrant.")
print("Done. The backend will see this collection already populated on its next startup.")
