# Raw University Documents (Knowledge Base)

Drop your real university documents here!

CampusGPT supports:
- `.pdf` (Portable Document Format)
- `.docx` (Microsoft Word)
- `.md` (Markdown)
- `.txt` (Plain Text)

When you run `python scripts/ingest.py`, the pipeline checks this directory first. If files are found here, they will be ingested into the vector store. If this folder is empty, CampusGPT automatically falls back to `data/sample/`.
