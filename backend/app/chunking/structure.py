"""Structure-aware chunking strategy.

Splits on headings and paragraphs first, then enforces size limits.
Preserves natural document hierarchy and section context.
"""

from typing import List
from backend.app.ingestion.loader import DocumentSnippet
from backend.app.chunking.base import Chunk, approximate_tokens


def chunk_structure(
    snippets: List[DocumentSnippet],
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[Chunk]:
    """Split on document paragraphs and headings, respecting natural boundaries.

    # WORKSHOP: Structure chunking is ideal for manuals and handbooks with
    # distinct sections. Compare this with 'overlapping' in compare_chunking.py.
    """
    chunks: List[Chunk] = []
    chunk_counter = 0
    words_limit = max(10, int(chunk_size / 1.3))

    for snippet in snippets:
        paragraphs = [p.strip() for p in snippet.text.split("\n\n") if p.strip()]
        current_words: List[str] = []

        for p in paragraphs:
            p_words = p.split()
            # If paragraph itself is larger than word limit, break it
            if len(p_words) > words_limit:
                if current_words:
                    text = " ".join(current_words)
                    chunks.append(Chunk(
                        chunk_id=f"{snippet.doc_id}_struct_{chunk_counter}",
                        text=text,
                        source=snippet.source,
                        chunk_index=chunk_counter,
                        page=snippet.page,
                        section=snippet.section,
                        doc_id=snippet.doc_id,
                        token_count=approximate_tokens(text)
                    ))
                    chunk_counter += 1
                    current_words = []

                for i in range(0, len(p_words), words_limit):
                    sub = p_words[i:i + words_limit]
                    text = " ".join(sub)
                    chunks.append(Chunk(
                        chunk_id=f"{snippet.doc_id}_struct_{chunk_counter}",
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

            if len(current_words) + len(p_words) <= words_limit:
                current_words.extend(p_words)
            else:
                text = " ".join(current_words)
                chunks.append(Chunk(
                    chunk_id=f"{snippet.doc_id}_struct_{chunk_counter}",
                    text=text,
                    source=snippet.source,
                    chunk_index=chunk_counter,
                    page=snippet.page,
                    section=snippet.section,
                    doc_id=snippet.doc_id,
                    token_count=approximate_tokens(text)
                ))
                chunk_counter += 1
                current_words = list(p_words)

        if current_words:
            text = " ".join(current_words)
            chunks.append(Chunk(
                chunk_id=f"{snippet.doc_id}_struct_{chunk_counter}",
                text=text,
                source=snippet.source,
                chunk_index=chunk_counter,
                page=snippet.page,
                section=snippet.section,
                doc_id=snippet.doc_id,
                token_count=approximate_tokens(text)
            ))
            chunk_counter += 1

    return chunks
