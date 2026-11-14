"""Tests for Chunking Strategies (STEP 1)."""

from backend.app.ingestion.loader import DocumentSnippet
from backend.app.chunking import (
    chunk_fixed,
    chunk_overlapping,
    chunk_structure,
    chunk_semantic,
    approximate_tokens
)


def test_approximate_tokens():
    text = "One two three four five six seven eight nine ten"
    tokens = approximate_tokens(text)
    # 10 words * 1.3 = 13 tokens
    assert tokens == 13


def test_chunk_overlapping_creates_windows(sample_snippets):
    chunks = chunk_overlapping(sample_snippets, chunk_size=50, chunk_overlap=10)
    assert len(chunks) >= 2
    for c in chunks:
        assert c.chunk_id
        assert c.source == "handbook.md"
        assert c.token_count > 0


def test_chunk_fixed_respects_token_boundaries(sample_snippets):
    chunks = chunk_fixed(sample_snippets, chunk_size=30, chunk_overlap=0)
    assert len(chunks) >= 2
    assert chunks[0].chunk_index == 0


def test_chunk_structure_respects_paragraphs():
    long_snippet = [DocumentSnippet(
        text="Paragraph one info.\n\nParagraph two with more details.\n\nParagraph three final thoughts.",
        source="test.md",
        section="Intro"
    )]
    chunks = chunk_structure(long_snippet, chunk_size=100)
    assert len(chunks) >= 1
    assert "Paragraph one" in chunks[0].text
