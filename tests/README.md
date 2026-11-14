# Tests Directory

Offline test suite powered by `pytest` and mock Gemini clients.

Passes 100% offline with **no Gemini API key** and **no active internet connection**:
- Loaders and junk cleaners
- Chunking strategies (fixed, overlapping, structure, semantic)
- Cosine similarity vector mathematics
- Vector stores (ChromaDB and FAISS)
- Reranking order adjustments
- Guardrails (injection trap, exact credentials reply, key redaction)
- FastAPI endpoints (`/chat`, `/health`, `/config`)
