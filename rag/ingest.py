"""
RAG ingestion pipeline:
Documents -> Text extraction -> Chunking -> Embeddings -> ChromaDB
"""
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma

from config import settings
from rag.loader import load_all_documents
from rag.embeddings import get_embedding_model
from logging_config import get_logger

logger = get_logger(__name__)


def get_vector_store() -> Chroma:
    """Returns a handle to the persistent Chroma collection."""
    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
    return Chroma(
        collection_name=settings.CHROMA_COLLECTION_NAME,
        embedding_function=get_embedding_model(),
        persist_directory=settings.CHROMA_PERSIST_DIR,
    )


def ingest_documents(force: bool = False) -> int:
    """
    Loads documents, chunks them, embeds them, and stores them in ChromaDB.
    If the collection already has data and force=False, ingestion is skipped.
    Returns the number of chunks stored.
    """
    store = get_vector_store()

    existing_count = store._collection.count()
    if existing_count > 0 and not force:
        logger.info(
            f"ChromaDB collection already has {existing_count} chunks. Skipping ingestion "
            f"(call ingest_documents(force=True) to re-ingest)."
        )
        return existing_count

    if force and existing_count > 0:
        ids = store._collection.get()["ids"]
        if ids:
            store._collection.delete(ids=ids)
        logger.info("Cleared existing ChromaDB collection before re-ingesting.")

    segments = load_all_documents()
    if not segments:
        logger.warning("No documents found to ingest.")
        return 0

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    lc_documents = []
    for seg in segments:
        chunks = splitter.split_text(seg.text)
        for chunk in chunks:
            lc_documents.append(
                Document(
                    page_content=chunk,
                    metadata={"source": seg.source, "page": seg.page},
                )
            )

    if not lc_documents:
        logger.warning("Document splitting produced zero chunks.")
        return 0

    store.add_documents(lc_documents)
    logger.info(f"Ingested {len(lc_documents)} chunks into ChromaDB.")
    return len(lc_documents)


if __name__ == "__main__":
    count = ingest_documents(force=True)
    print(f"Ingestion complete. Total chunks stored: {count}")
