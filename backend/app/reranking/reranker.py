"""Reranking algorithms and strategies (STEP 5).

Supported strategies (selected via RERANKER=none|lexical|gemini|cross_encoder):
- 'lexical' (Default): Blends vector similarity with keyword/n-gram lexical overlap. Lightweight, fast, zero dependencies.
- 'none': Simply trims the retrieved candidates down to FINAL_K without altering order.
- 'gemini': Uses the Gemini LLM to score relevance of each candidate against the query.
- 'cross_encoder': Uses sentence-transformers (PyTorch, optional dependency).
"""

import re
from typing import List, Dict, Any, Optional
from backend.app.config import settings


def tokenize_words(text: str) -> set[str]:
    """Extract lowercased alphanumeric words for lexical matching."""
    return set(re.findall(r'\b\w+\b', text.lower()))


def rerank_lexical(query: str, candidates: List[Dict[str, Any]], final_k: int) -> List[Dict[str, Any]]:
    """Rerank candidates combining vector cosine similarity with BM25-like word overlap.
    Composite Score = 0.6 * vector_relevance + 0.4 * lexical_overlap_ratio.
    """
    q_words = tokenize_words(query)
    if not q_words:
        return candidates[:final_k]

    scored = []
    for c in candidates:
        doc_words = tokenize_words(c.get("text", ""))
        overlap = len(q_words.intersection(doc_words))
        lexical_ratio = overlap / len(q_words)
        relevance = float(c.get("relevance_score", 0.0))

        # Composite score
        composite_score = round(0.6 * relevance + 0.4 * lexical_ratio, 4)
        c_copy = dict(c)
        c_copy["rerank_score"] = composite_score
        scored.append(c_copy)

    # Sort descending by rerank_score
    scored.sort(key=lambda x: x["rerank_score"], reverse=True)
    return scored[:final_k]


def rerank_none(query: str, candidates: List[Dict[str, Any]], final_k: int) -> List[Dict[str, Any]]:
    """Passthrough without reordering; assigns original relevance_score to rerank_score."""
    result = []
    for c in candidates[:final_k]:
        c_copy = dict(c)
        c_copy["rerank_score"] = c.get("relevance_score", 0.0)
        result.append(c_copy)
    return result


def rerank_cross_encoder(query: str, candidates: List[Dict[str, Any]], final_k: int) -> List[Dict[str, Any]]:
    """Neural cross-encoder reranker using sentence-transformers (optional)."""
    try:
        from sentence_transformers import CrossEncoder
        model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        pairs = [[query, c.get("text", "")] for c in candidates]
        scores = model.predict(pairs)
        scored = []
        for idx, c in enumerate(candidates):
            c_copy = dict(c)
            c_copy["rerank_score"] = round(float(scores[idx]), 4)
            scored.append(c_copy)
        scored.sort(key=lambda x: x["rerank_score"], reverse=True)
        return scored[:final_k]
    except ImportError:
        # Fallback gracefully to lexical if sentence-transformers is missing
        return rerank_lexical(query, candidates, final_k)


def rerank_candidates(
    query: str,
    candidates: List[Dict[str, Any]],
    strategy: Optional[str] = None,
    final_k: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Rerank candidates using the specified strategy.

    # WORKSHOP: Try setting RERANKER=none vs RERANKER=lexical in .env.
    # Observe the collapsible 'How CampusGPT answered' panel in the UI to see
    # how chunks shift positions between initial retrieval and final selection!
    """
    k = final_k if final_k is not None else settings.final_k
    strat = (strategy or settings.reranker).lower().strip()

    if not candidates:
        return []

    if strat == "none":
        return rerank_none(query, candidates, k)
    elif strat == "cross_encoder":
        return rerank_cross_encoder(query, candidates, k)
    else:
        # Default lexical
        return rerank_lexical(query, candidates, k)
