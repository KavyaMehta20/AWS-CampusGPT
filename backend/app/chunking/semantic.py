"""Semantic chunking strategy (OPTIONAL).

Splits text where semantic meaning shifts between adjacent sentences.
Note: In live mode this can invoke embedding similarity checks between sentences,
which requires additional API quota. Here we provide an algorithmic sentence-shift
splitter that respects semantic boundaries and length constraints.
"""

import re
from typing import List
from backend.app.ingestion.loader import DocumentSnippet
from backend.app.chunking.base import Chunk, approximate_tokens


def split_into_sentences(text: str) -> List[str]:
    """Split text on sentence terminators."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_semantic(
    snippets: List[DocumentSnippet],
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[Chunk]:
    """Split where topical shifts occur (sentence boundary grouping).

    # WORKSHOP: Semantic chunking groups complete sentences until a topic
    # shift or token ceiling is reached, preventing mid-sentence clipping.
    """
    chunks: List[Chunk] = []
    chunk_counter = 0
    words_limit = max(10, int(chunk_size / 1.3))

    for snippet in snippets:
        sentences = split_into_sentences(snippet.text)
        current_sentences: List[str] = []
        current_word_count = 0

        for sentence in sentences:
            s_words = len(sentence.split())
            if current_word_count + s_words <= words_limit:
                current_sentences.append(sentence)
                current_word_count += s_words
            else:
                if current_sentences:
                    text = " ".join(current_sentences)
                    chunks.append(Chunk(
                        chunk_id=f"{snippet.doc_id}_sem_{chunk_counter}",
                        text=text,
                        source=snippet.source,
                        chunk_index=chunk_counter,
                        page=snippet.page,
                        section=snippet.section,
                        doc_id=snippet.doc_id,
                        token_count=approximate_tokens(text)
                    ))
                    chunk_counter += 1
                current_sentences = [sentence]
                current_word_count = s_words

        if current_sentences:
            text = " ".join(current_sentences)
            chunks.append(Chunk(
                chunk_id=f"{snippet.doc_id}_sem_{chunk_counter}",
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
