"""FAISS VectorStore implementation (STEP 3).

FAISS is an in-memory similarity-search library.
Teaching Note:
- Chroma is a vector database (metadata filtering, persistence, rich querying).
- FAISS is a similarity-search library (compact, blazing fast, ideal for Lambda).
- In serverless AWS Lambda, local disk is ephemeral (/tmp) and Chroma is bulky,
  so FAISS is ideal for loading a prebuilt index on cold start.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

from backend.app.chunking.base import Chunk
from backend.app.vectorstore.base import VectorStore


class FaissVectorStore(VectorStore):
    """FAISS CPU implementation with companion JSON metadata storage."""
    def __init__(self, index_file: Optional[str] = None, meta_file: Optional[str] = None):
        idx = index_file or os.environ.get("FAISS_INDEX_FILE", "vectorstore/faiss_index.bin")
        meta = meta_file or os.environ.get("FAISS_META_FILE", "vectorstore/faiss_meta.json")
        self.index_file = Path(idx)
        self.meta_file = Path(meta)
        self.index = None
        self.metadata_store: List[Dict[str, Any]] = []
        self._load_if_exists()

    def _load_if_exists(self) -> None:
        """Load FAISS index and metadata if files exist on disk."""
        if self.index_file.exists() and self.meta_file.exists():
            try:
                import faiss
                self.index = faiss.read_index(str(self.index_file))
                self.metadata_store = json.loads(self.meta_file.read_text(encoding="utf-8"))
            except Exception:
                self.index = None
                self.metadata_store = []

    def save(self) -> None:
        """Persist FAISS index and metadata to disk."""
        if self.index is None:
            return
        try:
            import faiss
            self.index_file.parent.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self.index, str(self.index_file))
            self.meta_file.write_text(json.dumps(self.metadata_store, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            raise RuntimeError(f"Failed to persist FAISS index: {e}") from e

    def add(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        """Add vectors and normalize for inner-product (cosine) search."""
        if not chunks or not embeddings:
            return
        try:
            import faiss
        except ImportError:
            raise ImportError(
                "faiss-cpu is required to use the FAISS vector store backend. "
                "Install it with 'pip install faiss-cpu'."
            )

        vectors = np.array(embeddings, dtype=np.float32)
        # Normalize vectors for cosine similarity via IndexFlatIP
        faiss.normalize_L2(vectors)
        dim = vectors.shape[1]

        if self.index is None:
            self.index = faiss.IndexFlatIP(dim)

        self.index.add(vectors)

        for chunk in chunks:
            self.metadata_store.append({
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "source": str(chunk.source or ""),
                "page": str(chunk.page or ""),
                "section": str(chunk.section or ""),
                "doc_id": str(chunk.doc_id or "")
            })

        self.save()

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search nearest vectors using inner product on normalized embeddings."""
        if self.index is None or self.index.ntotal == 0:
            return []

        try:
            import faiss
        except ImportError:
            return []

        q_vec = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(q_vec)

        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(q_vec, k)

        results: List[Dict[str, Any]] = []
        for rank, idx in enumerate(indices[0]):
            if idx == -1 or idx >= len(self.metadata_store):
                continue
            item_meta = self.metadata_store[idx]

            # Optional metadata filtering
            if metadata_filter:
                match = all(str(item_meta.get(k)) == str(v) for k, v in metadata_filter.items())
                if not match:
                    continue

            score = float(scores[0][rank])
            # Inner product of normalized vectors = cosine similarity
            normalized_score = max(0.0, min(1.0, (score + 1.0) / 2.0 if score < 0 else score))

            results.append({
                "chunk_id": item_meta["chunk_id"],
                "text": item_meta["text"],
                "source": item_meta["source"],
                "page": item_meta["page"],
                "section": item_meta["section"],
                "relevance_score": round(normalized_score, 4)
            })

        return results

    def count(self) -> int:
        return self.index.ntotal if self.index is not None else 0

    def reset(self) -> None:
        self.index = None
        self.metadata_store = []
        if self.index_file.exists():
            self.index_file.unlink(missing_ok=True)
        if self.meta_file.exists():
            self.meta_file.unlink(missing_ok=True)
