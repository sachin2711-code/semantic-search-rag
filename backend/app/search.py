import numpy as np

from .data_loader import COLLECTION_NAME, tokenize
from .embeddings import embed_query
from .rerank import rerank as cohere_rerank


def hybrid_search(query, artifacts, top_k=20, dense_k=20, sparse_k=20, rrf_k=60):
    qdrant = artifacts["qdrant"]
    bm25 = artifacts["bm25"]
    chunk_store = artifacts["chunk_store"]

    # dense leg — Cohere embeds the query via API call, Qdrant does the vector search
    q_emb = embed_query(query)
    dense_results = qdrant.query_points(
        collection_name=COLLECTION_NAME, query=q_emb, limit=dense_k
    ).points
    dense_ranks = {r.id: rank for rank, r in enumerate(dense_results)}

    # sparse leg — unchanged, pure local computation, no API call needed
    bm25_scores = bm25.get_scores(tokenize(query))
    sparse_idx = np.argsort(bm25_scores)[::-1][:sparse_k]
    sparse_ranks = {int(idx): rank for rank, idx in enumerate(sparse_idx)}

    # fuse by rank position — identical logic to every previous version
    fused = {}
    for idx, rank in dense_ranks.items():
        fused[idx] = fused.get(idx, 0) + 1 / (rrf_k + rank + 1)
    for idx, rank in sparse_ranks.items():
        fused[idx] = fused.get(idx, 0) + 1 / (rrf_k + rank + 1)

    top = sorted(fused.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [{**chunk_store[idx], "idx": idx} for idx, _ in top]


def production_search(query, artifacts, top_k=5, dense_k=20, sparse_k=20):
    candidates = hybrid_search(
        query, artifacts, top_k=max(dense_k, sparse_k),
        dense_k=dense_k, sparse_k=sparse_k,
    )

    docs = [c["text"] for c in candidates]
    ranked = cohere_rerank(query, docs, top_k=top_k)

    return [{**candidates[doc_idx], "score": float(score)} for doc_idx, score in ranked]
