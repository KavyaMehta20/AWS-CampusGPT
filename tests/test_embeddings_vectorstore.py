"""Tests for Embeddings and Vector Stores (STEPS 2 & 3)."""

from backend.app.embeddings.client import cosine_similarity, GeminiEmbedder
from backend.app.chunking.base import Chunk
from backend.app.vectorstore.chroma_store import ChromaVectorStore
from backend.app.vectorstore.faiss_store import FaissVectorStore


def test_cosine_similarity():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]
    # Identical vectors should have similarity 1.0
    assert round(cosine_similarity(v1, v2), 4) == 1.0
    # Orthogonal vectors should have similarity 0.0
    assert round(cosine_similarity(v1, v3), 4) == 0.0


def test_chroma_vector_store(tmp_path):
    store = ChromaVectorStore(persist_dir=str(tmp_path / "chroma_test"), collection_name="test_col")
    chunks = [
        Chunk("c1", "Accounting course details", "catalog.md", 0, section="Accounting"),
        Chunk("c2", "Computer science fundamentals", "catalog.md", 1, section="CS")
    ]
    embeddings = [
        [0.9, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.1, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ]
    store.reset()
    store.add(chunks, embeddings)
    assert store.count() == 2

    results = store.search([0.9, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], top_k=1)
    assert len(results) == 1
    assert results[0]["chunk_id"] == "c1"
    assert results[0]["relevance_score"] > 0.8
