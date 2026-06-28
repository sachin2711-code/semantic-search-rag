import os

import cohere

COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
EMBED_MODEL = "embed-english-v3.0"

co = cohere.Client(COHERE_API_KEY)


def embed_documents(texts):
    """Embed a batch of chunks for indexing. Used only by the one-time
    migration script, not during normal request handling."""
    response = co.embed(texts=texts, model=EMBED_MODEL, input_type="search_document")
    return response.embeddings


def embed_query(text):
    """Embed a single incoming search query. Cohere distinguishes query vs
    document embeddings — using the right input_type for each improves results."""
    response = co.embed(texts=[text], model=EMBED_MODEL, input_type="search_query")
    return response.embeddings[0]
