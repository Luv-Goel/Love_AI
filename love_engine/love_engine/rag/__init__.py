"""
LoveEngine RAG (Retrieval Augmented Generation) Module.

Provides an all-in-one API for document ingestion:
Upload -> (OCR) -> Chunk -> Embed -> Vector Store
"""

from love_engine.rag.main import aingest, aquery, ingest, query

__all__ = ["ingest", "aingest", "query", "aquery"]


# Expose at love_engine.rag level for convenience
async def arag_ingest(*args, **kwargs):
    """Alias for aingest."""
    return await aingest(*args, **kwargs)


def rag_ingest(*args, **kwargs):
    """Alias for ingest."""
    return ingest(*args, **kwargs)
