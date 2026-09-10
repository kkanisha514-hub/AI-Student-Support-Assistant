"""
Semantic retrieval over the ChromaDB vector store.
"""
from dataclasses import dataclass
from typing import List

from config import settings
from rag.ingest import get_vector_store
from logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class RetrievedChunk:
    text: str
    source: str
    page: int
    score: float


def retrieve(query: str, k: int = None) -> List[RetrievedChunk]:
    """
    Runs semantic similarity search against ChromaDB and returns the top-k
    chunks along with their source document and page number.
    """
    k = k or settings.RAG_TOP_K
    store = get_vector_store()

    try:
        results = store.similarity_search_with_relevance_scores(query, k=k)
    except Exception as e:
        logger.error(f"RAG retrieval failed: {e}")
        return []

    chunks: List[RetrievedChunk] = []
    for doc, score in results:
        chunks.append(
            RetrievedChunk(
                text=doc.page_content,
                source=doc.metadata.get("source", "unknown"),
                page=doc.metadata.get("page", 0),
                score=score,
            )
        )
    return chunks


def format_chunks_for_prompt(chunks: List[RetrievedChunk]) -> str:
    """Formats retrieved chunks into a context block for the LLM prompt."""
    if not chunks:
        return ""
    parts = []
    for i, c in enumerate(chunks, start=1):
        parts.append(f"[Excerpt {i} | Source: {c.source}, Page: {c.page}]\n{c.text}")
    return "\n\n".join(parts)
