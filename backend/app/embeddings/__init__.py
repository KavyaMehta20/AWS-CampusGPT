"""Embeddings package exports."""
from backend.app.embeddings.client import (
    GeminiEmbedder,
    cosine_similarity,
    compute_text_hash,
    get_cached_embedding,
    save_cached_embedding
)

__all__ = [
    "GeminiEmbedder",
    "cosine_similarity",
    "compute_text_hash",
    "get_cached_embedding",
    "save_cached_embedding"
]
