from typing import List

from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    idx: int
    text: str
    page: int
    score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]


class AskRequest(BaseModel):
    query: str
    top_k: int = 5


class AskResponse(BaseModel):
    query: str
    answer: str
    sources: List[SearchResult]
