const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

async function postJSON(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Request failed (${res.status}): ${detail}`);
  }

  return res.json();
}

export function search(query, topK = 5) {
  return postJSON("/search", { query, top_k: topK });
}

export function ask(query, topK = 5) {
  return postJSON("/ask", { query, top_k: topK });
}
