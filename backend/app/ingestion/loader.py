"""Document ingestion loader module (STEP 0).

Loads documents from PDF, DOCX, Markdown, and TXT files.
Extracts text with metadata (source, page/section, doc_id).
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None


class DocumentSnippet:
    """Represents a piece of raw loaded text with metadata."""
    def __init__(self, text: str, source: str, page: Optional[int] = None, section: Optional[str] = None, doc_id: str = ""):
        self.text = text
        self.source = source
        self.page = page
        self.section = section
        self.doc_id = doc_id or f"{source}_{page or section or '1'}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "source": self.source,
            "page": self.page,
            "section": self.section,
            "doc_id": self.doc_id
        }


def clean_text(text: str) -> str:
    """Strip obvious junk: repeated whitespace, repeated headers, page numbers."""
    # Remove standalone page numbers (e.g., "Page 12" or solitary numbers on lines)
    text = re.sub(r'(?i)^\s*page\s+\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    # Normalize multiple newlines and spaces
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    return text.strip()


def load_pdf(file_path: Path) -> List[DocumentSnippet]:
    """Extract text page-by-page from a PDF file."""
    if PdfReader is None:
        raise ImportError("pypdf is required to read PDF documents.")
    snippets = []
    reader = PdfReader(str(file_path))
    filename = file_path.name
    for idx, page in enumerate(reader.pages):
        raw_text = page.extract_text() or ""
        cleaned = clean_text(raw_text)
        if cleaned:
            snippets.append(DocumentSnippet(
                text=cleaned,
                source=filename,
                page=idx + 1,
                section=f"Page {idx + 1}",
                doc_id=f"{filename}_p{idx + 1}"
            ))
    return snippets


def load_docx(file_path: Path) -> List[DocumentSnippet]:
    """Extract text from DOCX grouped by nearest heading."""
    if DocxDocument is None:
        raise ImportError("python-docx is required to read DOCX documents.")
    snippets = []
    doc = DocxDocument(str(file_path))
    filename = file_path.name
    current_heading = "General"
    current_paragraphs = []

    for p in doc.paragraphs:
        style_name = p.style.name.lower() if p.style else ""
        text = p.text.strip()
        if not text:
            continue
        if "heading" in style_name:
            if current_paragraphs:
                cleaned = clean_text("\n\n".join(current_paragraphs))
                if cleaned:
                    snippets.append(DocumentSnippet(
                        text=cleaned,
                        source=filename,
                        section=current_heading,
                        doc_id=f"{filename}_{current_heading[:20]}"
                    ))
                current_paragraphs = []
            current_heading = text
        else:
            current_paragraphs.append(text)

    if current_paragraphs:
        cleaned = clean_text("\n\n".join(current_paragraphs))
        if cleaned:
            snippets.append(DocumentSnippet(
                text=cleaned,
                source=filename,
                section=current_heading,
                doc_id=f"{filename}_{current_heading[:20]}"
            ))
    return snippets


def load_markdown_or_txt(file_path: Path) -> List[DocumentSnippet]:
    """Extract text from Markdown or plain text by section headings."""
    filename = file_path.name
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()

    snippets = []
    current_heading = "Overview"
    current_lines = []

    for line in lines:
        stripped = line.strip()
        # Markdown heading detection
        if stripped.startswith("#"):
            if current_lines:
                cleaned = clean_text("\n".join(current_lines))
                if cleaned:
                    snippets.append(DocumentSnippet(
                        text=cleaned,
                        source=filename,
                        section=current_heading,
                        doc_id=f"{filename}_{current_heading[:20]}"
                    ))
                current_lines = []
            current_heading = stripped.lstrip("#").strip()
        else:
            current_lines.append(line)

    if current_lines:
        cleaned = clean_text("\n".join(current_lines))
        if cleaned:
            snippets.append(DocumentSnippet(
                text=cleaned,
                source=filename,
                section=current_heading,
                doc_id=f"{filename}_{current_heading[:20]}"
            ))
    return snippets


def load_documents(directory_path: Path) -> List[DocumentSnippet]:
    """Scan a directory and load all supported documents."""
    snippets: List[DocumentSnippet] = []
    if not directory_path.exists():
        return snippets

    for item in sorted(directory_path.iterdir()):
        if item.is_file():
            suffix = item.suffix.lower()
            if suffix == ".pdf":
                snippets.extend(load_pdf(item))
            elif suffix == ".docx":
                snippets.extend(load_docx(item))
            elif suffix in [".md", ".txt"]:
                snippets.extend(load_markdown_or_txt(item))
    return snippets
