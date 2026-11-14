"""Tests for Reranker Ordering (STEP 5)."""

from backend.app.reranking.reranker import rerank_lexical, rerank_none


def test_rerank_lexical_promotes_exact_word_matches():
    query = "Where do I find business core courses?"
    candidates = [
        {"chunk_id": "c1", "text": "General biology and natural science lab requirements.", "relevance_score": 0.70},
        {"chunk_id": "c2", "text": "The business core courses include ACCT and MGMT.", "relevance_score": 0.65}
    ]

    reranked = rerank_lexical(query, candidates, final_k=2)
    # c2 has lower vector relevance (0.65 vs 0.70) but high word overlap ("business", "core", "courses")
    # So rerank_lexical should promote c2 to rank 1
    assert reranked[0]["chunk_id"] == "c2"
    assert "rerank_score" in reranked[0]


def test_rerank_none_preserves_order():
    query = "Any question"
    candidates = [
        {"chunk_id": "c1", "text": "Snippet one", "relevance_score": 0.8},
        {"chunk_id": "c2", "text": "Snippet two", "relevance_score": 0.5}
    ]
    reranked = rerank_none(query, candidates, final_k=2)
    assert reranked[0]["chunk_id"] == "c1"
