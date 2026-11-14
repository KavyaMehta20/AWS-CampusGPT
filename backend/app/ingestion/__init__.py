"""Ingestion package exports."""
from backend.app.ingestion.loader import (
    DocumentSnippet,
    load_documents,
    load_pdf,
    load_docx,
    load_markdown_or_txt,
    clean_text
)

__all__ = [
    "DocumentSnippet",
    "load_documents",
    "load_pdf",
    "load_docx",
    "load_markdown_or_txt",
    "clean_text"
]
