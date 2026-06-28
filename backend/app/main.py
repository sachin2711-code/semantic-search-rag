from dotenv import load_dotenv

load_dotenv()  # must run before app.rag is imported, since it reads GROQ_API_KEY at import time

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.data_loader import load_artifacts
from app.rag import generate_answer
from app.schemas import AskRequest, AskResponse, SearchRequest, SearchResponse
from app.search import production_search

artifacts = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the server starts — loads chunk data, builds FAISS/BM25,
    # loads both models into memory. Everything below reuses this, no reloading per request.
    artifacts.update(load_artifacts())
    yield


app = FastAPI(title="Semantic Search API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "chunks_loaded": len(artifacts.get("chunk_store", []))}


@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    results = production_search(req.query, artifacts, top_k=req.top_k)
    return {"query": req.query, "results": results}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    answer, chunks = generate_answer(req.query, artifacts, top_k=req.top_k)
    return {"query": req.query, "answer": answer, "sources": chunks}
