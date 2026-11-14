"""Fixed-size chunking strategy.

Splits text strictly after N tokens (no overlap).
"""

from typing import List
from backend.app.ingestion.loader import DocumentSnippet
from backend.app.chunking.base import Chunk, approximate_tokens


def chunk_fixed(
    snippets: List[DocumentSnippet],
    chunk_size: int = 500,
    chunk_overlap: int = 0
) -> List[Chunk]:
    """Split snippets into fixed token-sized blocks without overlap.

    # WORKSHOP: Try changing chunk_size to 200 or 1000 in .env to observe
    # how strict splitting impacts retrieval precision vs context loss.
    """
    chunks: List[Chunk] = []
    chunk_counter = 0

    for snippet in snippets:
        words = snippet.text.split()
        if not words:
            continue

        # Approximate words per chunk: chunk_size / 1.3
        words_per_chunk = max(10, int(chunk_size / 1.3))
        
        for i in range(0, len(words), words_per_chunk):
            segment_words = words[i:i + words_per_chunk]
            segment_text = " ".join(segment_words)
            chunk_id = f"{snippet.doc_id}_fixed_{chunk_counter}"
            
            chunks.append(Chunk(
                chunk_id=chunk_id,
                text=segment_text,
                source=snippet.source,
                chunk_index=chunk_counter,
                page=snippet.page,
                section=snippet.section,
                doc_id=snippet.doc_id,
                token_count=approximate_tokens(segment_text)
            ))
            chunk_counter += 1

    return chunks
