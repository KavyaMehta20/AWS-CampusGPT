"""Common chunk representation and utilities for chunking strategies."""

import re
from typing import Dict, Any, List
from backend.app.ingestion.loader import DocumentSnippet


class Chunk:
    """Represents a text chunk created by a chunking strategy."""
    def __init__(
        self,
        chunk_id: str,
        text: str,
        source: str,
        chunk_index: int,
        page: Any = None,
        section: Any = None,
        doc_id: str = "",
        token_count: int = 0
    ):
        self.chunk_id = chunk_id
        self.text = text
        self.source = source
        self.chunk_index = chunk_index
        self.page = page
        self.section = section
        self.doc_id = doc_id
        self.token_count = token_count or approximate_tokens(text)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "source": self.source,
            "chunk_index": self.chunk_index,
            "page": self.page,
            "section": self.section,
            "doc_id": self.doc_id,
            "token_count": self.token_count
        }


def approximate_tokens(text: str) -> int:
    """Approximate token count without requiring a heavy tokenizer download.
    Rule: word count * 1.3 (standard rule of thumb for English text).
    """
    if not text:
        return 0
    words = len(re.findall(r'\S+', text))
    return max(1, int(words * 1.3))
