"""Gemini Embeddings Client and Caching (STEP 2).

Key Teaching Point:
The embedding model and the generation model do DIFFERENT jobs:
- The EMBEDDING model maps text into dense vector space coordinates.
- The GENERATION model reads retrieved text as context to generate answers.

Includes:
- Batch embedding requests.
- Exponential backoff retry for rate limits (429).
- Disk caching by MD5 hash of text to prevent re-spending API quota.
- Cosine similarity helper.
"""

import os
import time
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np

from backend.app.config import settings

# In-memory and disk cache directory (use /tmp when in Lambda)
CACHE_DIR = Path("/tmp/.cache/embeddings") if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") else Path(".cache/embeddings")


def compute_text_hash(text: str, model_name: str) -> str:
    """Compute a deterministic hash for a text string and model."""
    h = hashlib.md5(f"{model_name}::{text}".encode("utf-8")).hexdigest()
    return h


def get_cached_embedding(text_hash: str) -> Optional[List[float]]:
    """Retrieve cached vector from disk if available."""
    cache_file = CACHE_DIR / f"{text_hash}.json"
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def save_cached_embedding(text_hash: str, vector: List[float]) -> None:
    """Save an embedding vector to disk cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{text_hash}.json"
    try:
        cache_file.write_text(json.dumps(vector), encoding="utf-8")
    except Exception:
        pass


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate the cosine similarity between two numeric vectors.
    Cosine similarity ranges from -1.0 to 1.0 (typically 0.0 to 1.0 for normalized text).
    """
    arr_a = np.array(a, dtype=np.float32)
    arr_b = np.array(b, dtype=np.float32)
    norm_a = np.linalg.norm(arr_a)
    norm_b = np.linalg.norm(arr_b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(arr_a, arr_b) / (norm_a * norm_b))


class GeminiEmbedder:
    """Embedder using Google GenAI SDK with disk caching and retry logic."""
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_embedding_model
        self._client = None

    def _get_client(self):
        """Lazy load the GenAI client to avoid failing if credentials aren't set yet."""
        if self._client is not None:
            return self._client
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured! Please add your key to .env or set it in your environment."
            )
        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
            return self._client
        except ImportError:
            raise ImportError("The 'google-genai' SDK is not installed. Run 'pip install -r requirements.txt'.")

    def embed_texts(self, texts: List[str], batch_size: int = 16, max_retries: int = 5) -> List[List[float]]:
        """Embed a batch of text strings, utilizing cache and handling rate limits."""
        results: List[Optional[List[float]]] = [None] * len(texts)
        uncached_indices: List[int] = []

        # 1. Check disk cache
        for idx, text in enumerate(texts):
            thash = compute_text_hash(text, self.model)
            cached = get_cached_embedding(thash)
            if cached is not None:
                results[idx] = cached
            else:
                uncached_indices.append(idx)

        if not uncached_indices:
            return [r for r in results if r is not None]

        client = self._get_client()

        # 2. Batch requests for uncached items
        for b_start in range(0, len(uncached_indices), batch_size):
            batch_slice = uncached_indices[b_start:b_start + batch_size]
            batch_texts = [texts[i] for i in batch_slice]

            # Retry loop with exponential backoff for rate limits
            delay = 1.0
            for attempt in range(max_retries):
                try:
                    response = client.models.embed_content(
                        model=self.model,
                        contents=batch_texts
                    )
                    # Extract vectors
                    embeddings_data = response.embeddings
                    for i, emb in enumerate(embeddings_data):
                        vector = list(emb.values)
                        orig_idx = batch_slice[i]
                        results[orig_idx] = vector
                        thash = compute_text_hash(texts[orig_idx], self.model)
                        save_cached_embedding(thash, vector)
                    break
                except Exception as e:
                    err_msg = str(e).lower()
                    if "429" in err_msg or "quota" in err_msg or "resource_exhausted" in err_msg:
                        if attempt == max_retries - 1:
                            raise RuntimeError(
                                f"Gemini API rate limit exceeded (429) after {max_retries} retries. "
                                "Please wait a moment or verify your quota on Google AI Studio."
                            ) from e
                        time.sleep(delay)
                        delay *= 2.0
                    else:
                        raise e

        return [r for r in results if r is not None]

    def embed_query(self, query: str) -> List[float]:
        """Embed a single search query."""
        vectors = self.embed_texts([query])
        return vectors[0]
