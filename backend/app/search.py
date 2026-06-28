from .data_loader import COLLECTION_NAME, tokenize

import numpy as np


def hybrid_search(query, artifacts, top_k=20, dense_k=20, sparse_k=20, rrf_k=60):
    model = artifacts["model"]
    qdrant = artifacts["qdrant"]
    bm25 = artifacts["bm25"]
    chunk_store = artifacts["chunk_store"]

    # dense leg — Qdrant handles cosine similarity internally, no manual normalization needed
    q_emb = model.encode([query]).tolist()[0]
    dense_results = qdrant.query_points(
        collection_name=COLLECTION_NAME, query=q_emb, limit=dense_k
    ).points
    dense_ranks = {r.id: rank for rank, r in enumerate(dense_results)}

    # sparse leg — unchanged from the FAISS version
    bm25_scores = bm25.get_scores(tokenize(query))
    sparse_idx = np.argsort(bm25_scores)[::-1][:sparse_k]
    sparse_ranks = {int(idx): rank for rank, idx in enumerate(sparse_idx)}

    # fuse by rank position (reciprocal rank fusion) — identical logic either way
    fused = {}
    for idx, rank in dense_ranks.items():
        fused[idx] = fused.get(idx, 0) + 1 / (rrf_k + rank + 1)
    for idx, rank in sparse_ranks.items():
        fused[idx] = fused.get(idx, 0) + 1 / (rrf_k + rank + 1)

    top = sorted(fused.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [{**chunk_store[idx], "idx": idx} for idx, _ in top]


def production_search(query, artifacts, top_k=5, dense_k=20, sparse_k=20):
    reranker = artifacts["reranker"]

    candidates = hybrid_search(
        query, artifacts, top_k=max(dense_k, sparse_k),
        dense_k=dense_k, sparse_k=sparse_k,
    )

    pairs = [[query, c["text"]] for c in candidates]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
    return [{**doc, "score": float(score)} for score, doc in ranked[:top_k]]
