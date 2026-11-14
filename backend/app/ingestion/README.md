# Ingestion Step (STEP 0)

This directory contains the document loading and normalization logic for CampusGPT.

- `loader.py`: Handles loading `.pdf` (via `pypdf`), `.docx` (via `python-docx`), `.md`, and `.txt` files.
- Extracts document metadata (`source`, `page`, `section`, `doc_id`) so every answer can be cited.
- Cleans obvious artifacts (page numbers, repeated headers/footers).
