"""Retrieval engine module (STEP 4).

Embeds the incoming user question, searches the VectorStore for candidate chunks,
optionally filters by metadata, and applies the MIN_RELEVANCE score threshold.
"""

from typing import List, Dict, Any, Optional
from backend.app.config import settings
from backend.app.embeddings.client import GeminiEmbedder
from backend.app.vectorstore import get_vector_store, VectorStore


class Retriever:
    """Handles semantic candidate retrieval from the vector store."""
    def __init__(self, embedder: Optional[GeminiEmbedder] = None, vector_store: Optional[VectorStore] = None):
        self.embedder = embedder or GeminiEmbedder()
        self.vector_store = vector_store or get_vector_store()

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_relevance: Optional[float] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve candidate chunks for a query.

        # WORKSHOP: Try adjusting TOP_K_CANDIDATES and MIN_RELEVANCE in .env
        # to observe how wide candidate pools capture more context while filtering
        # out low-quality distractors.
        """
        k = top_k if top_k is not None else settings.top_k_candidates
        threshold = min_relevance if min_relevance is not None else settings.min_relevance

        # 1. Embed user query
        query_embedding = self.embedder.embed_query(query)

        # 2. Vector search
        candidates = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=k,
            metadata_filter=metadata_filter
        )

        # 3. Filter by minimum relevance threshold
        filtered = [c for c in candidates if c.get("relevance_score", 0.0) >= threshold]
        return filtered
