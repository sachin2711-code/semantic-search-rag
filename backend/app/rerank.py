import os

import cohere

COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
RERANK_MODEL = "rerank-english-v3.0"

co = cohere.Client(COHERE_API_KEY)


def rerank(query, documents, top_k=5):
    """documents: list of plain text strings.
    Returns (original_index, relevance_score) pairs, sorted best-first.
    relevance_score is already a 0-1 probability — no rescaling needed,
    unlike the raw logits the local cross-encoder used to return."""
    response = co.rerank(query=query, documents=documents, model=RERANK_MODEL, top_n=top_k)
    return [(r.index, r.relevance_score) for r in response.results]
