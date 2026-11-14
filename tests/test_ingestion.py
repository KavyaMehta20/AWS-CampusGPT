"""Tests for Document Ingestion and Cleaning (STEP 0)."""

from pathlib import Path
from backend.app.ingestion.loader import (
    clean_text,
    load_markdown_or_txt,
    load_documents,
    DocumentSnippet
)


def test_clean_text_removes_page_numbers_and_extra_whitespace():
    raw = "Header text\n\nPage 4\n\n\n   Paragraph text with   spaces.   \n\n12\n\nFooter"
    cleaned = clean_text(raw)
    assert "Page 4" not in cleaned
    assert "\n12\n" not in cleaned
    assert "Paragraph text with spaces." in cleaned


def test_load_markdown_file(tmp_path: Path):
    md_content = """# Section 1: Overview
Welcome to the university.

# Section 2: Advising
Advising is required every term.
"""
    test_file = tmp_path / "sample.md"
    test_file.write_text(md_content, encoding="utf-8")

    snippets = load_markdown_or_txt(test_file)
    assert len(snippets) == 2
    assert snippets[0].section == "Section 1: Overview"
    assert "Welcome" in snippets[0].text
    assert snippets[1].section == "Section 2: Advising"
    assert snippets[1].source == "sample.md"
