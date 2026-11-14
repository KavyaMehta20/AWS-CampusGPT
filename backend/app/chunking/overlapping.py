"""Overlapping chunking strategy (DEFAULT).

Splits text into fixed-size windows with an overlap buffer so concepts
straddling boundaries are not lost between chunks.
"""

from typing import List
from backend.app.ingestion.loader import DocumentSnippet
from backend.app.chunking.base import Chunk, approximate_tokens


def chunk_overlapping(
    snippets: List[DocumentSnippet],
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[Chunk]:
    """Split snippets into overlapping windows.

    # WORKSHOP: Default settings are 500 tokens with 50 tokens overlap.
    # Try 300 / 100 or 800 / 20. Note how overlap prevents answering errors
    # when key facts span chunk edges.
    """
    chunks: List[Chunk] = []
    chunk_counter = 0

    # Ensure valid overlap
    if chunk_overlap >= chunk_size:
        chunk_overlap = max(0, chunk_size - 10)

    words_per_chunk = max(10, int(chunk_size / 1.3))
    words_overlap = int(chunk_overlap / 1.3)
    step = max(1, words_per_chunk - words_overlap)

    for snippet in snippets:
        words = snippet.text.split()
        if not words:
            continue

        if len(words) <= words_per_chunk:
            # Fits in a single chunk
            text = " ".join(words)
            chunks.append(Chunk(
                chunk_id=f"{snippet.doc_id}_ov_{chunk_counter}",
                text=text,
                source=snippet.source,
                chunk_index=chunk_counter,
                page=snippet.page,
                section=snippet.section,
                doc_id=snippet.doc_id,
                token_count=approximate_tokens(text)
            ))
            chunk_counter += 1
            continue

        # Sliding window
        for i in range(0, len(words), step):
            window_words = words[i:i + words_per_chunk]
            if not window_words:
                break
            text = " ".join(window_words)
            chunks.append(Chunk(
                chunk_id=f"{snippet.doc_id}_ov_{chunk_counter}",
                text=text,
                source=snippet.source,
                chunk_index=chunk_counter,
                page=snippet.page,
                section=snippet.section,
                doc_id=snippet.doc_id,
                token_count=approximate_tokens(text)
            ))
            chunk_counter += 1
            if i + words_per_chunk >= len(words):
                break

    return chunks
