"""Inspect Chunks CLI Script.

Reads data/processed/chunks.jsonl and displays chunk metadata,
approximate token counts, and text previews for students.
"""

import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
CHUNKS_FILE = ROOT_DIR / "data" / "processed" / "chunks.jsonl"


def inspect():
    print("=" * 60)
    print("📋 CampusGPT Processed Chunks Inspector")
    print("=" * 60)

    if not CHUNKS_FILE.exists():
        print(f"Error: {CHUNKS_FILE} does not exist.")
        print("Run 'python scripts/ingest.py' first to process documents into chunks.")
        return

    chunks = []
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))

    print(f"Total chunks found: {len(chunks)}\n")

    for i, c in enumerate(chunks[:8]):
        print(f"[{i+1}] ID: {c.get('chunk_id')}")
        print(f"    Source: {c.get('source')} | Section: {c.get('section') or c.get('page')}")
        print(f"    Tokens: ~{c.get('token_count')} tokens")
        snippet = c.get('text', '').replace('\n', ' ')[:140]
        print(f"    Preview: \"{snippet}...\"\n")

    if len(chunks) > 8:
        print(f"... and {len(chunks) - 8} more chunks in {CHUNKS_FILE}")


if __name__ == "__main__":
    inspect()
