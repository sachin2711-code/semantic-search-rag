import os
from groq import Groq

from .search import production_search

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

RAG_SYSTEM_PROMPT = """You are a helpful assistant that answers questions using ONLY the provided context from a document.
Rules:
- If the answer is not in the context, say "I don't have enough information in the provided document to answer that."
- Always cite which source(s) you used, like [Source 2].
- Be concise and accurate. Do not add outside knowledge.
"""


def build_context(chunks):
    parts = []
    for i, c in enumerate(chunks, start=1):
        parts.append(f"[Source {i} - Page {c['page']}]\n{c['text']}")
    return "\n\n".join(parts)


def generate_answer(query, artifacts, top_k=5):
    chunks = production_search(query, artifacts, top_k=top_k)
    context = build_context(chunks)

    user_prompt = f"""Context:
{context}

Question: {query}

Answer using only the context above, and cite sources like [Source 1]."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=500,
        messages=[
            {"role": "system", "content": RAG_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    answer = response.choices[0].message.content
    return answer, chunks
