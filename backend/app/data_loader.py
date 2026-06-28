import json
import os
import re
import time
from pathlib import Path

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from rank_bm25 import BM25Okapi

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")
COLLECTION_NAME = "pdf_chunks"


def tokenize(text: str):
    return re.findall(r"\w+", text.lower())


def connect_to_qdrant(retries=10, delay=2):
    for attempt in range(retries):
        try:
            client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60)
            client.get_collections()
            return client
        except Exception as e:
            print(f"Qdrant not ready yet (attempt {attempt + 1}/{retries}): {e}")
            time.sleep(delay)
    raise RuntimeError(f"Could not connect to Qdrant at {QDRANT_URL} after {retries} attempts")


def load_artifacts():
    with open(DATA_DIR / "chunk_store.json") as f:
        chunk_store = json.load(f)

    embeddings = np.load(DATA_DIR / "embeddings.npy").astype(np.float32)

    bm25_corpus = [tokenize(c["text"]) for c in chunk_store]
    bm25 = BM25Okapi(bm25_corpus)

    print(f"Connecting to Qdrant at {QDRANT_URL}...")
    qdrant = connect_to_qdrant()

    existing = [c.name for c in qdrant.get_collections().collections]

    if COLLECTION_NAME not in existing:
        print(f"Creating '{COLLECTION_NAME}' and uploading {len(chunk_store)} vectors...")
        dim = embeddings.shape[1]
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
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
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists — skipping upload.")

    print(f"Ready. {len(chunk_store)} chunks indexed.")

    return {
        "chunk_store": chunk_store,
        "qdrant": qdrant,
        "bm25": bm25,
    }
