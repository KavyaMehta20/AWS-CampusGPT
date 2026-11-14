"""Compare Chunking Strategies Side-by-Side (Workshop Experiment 1).

Runs chunking with different settings and shows how the resulting chunks differ.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.ingestion import load_documents
from backend.app.chunking import create_chunks


def compare():
    print("=" * 60)
    print("🔬 Chunking Strategy Comparison Experiment")
    print("=" * 60)

    raw_path = ROOT_DIR / "data" / "raw"
    sample_path = ROOT_DIR / "data" / "sample"
    data_path = raw_path if any(raw_path.glob("*.*")) else sample_path

    snippets = load_documents(data_path)
    if not snippets:
        print("No documents found to chunk.")
        return

    configs = [
        {"name": "Fixed (200 tokens, 0 overlap)", "strategy": "fixed", "size": 200, "overlap": 0},
        {"name": "Overlapping (500 tokens, 50 overlap - Default)", "strategy": "overlapping", "size": 500, "overlap": 50},
        {"name": "Structure-Aware (500 tokens)", "strategy": "structure", "size": 500, "overlap": 50},
        {"name": "Semantic-Shift (500 tokens)", "strategy": "semantic", "size": 500, "overlap": 50},
    ]

    for cfg in configs:
        chunks = create_chunks(
            snippets,
            strategy=cfg["strategy"],
            chunk_size=cfg["size"],
            chunk_overlap=cfg["overlap"],
            save_to_jsonl=False
        )
        avg_tokens = sum(c.token_count for c in chunks) / max(1, len(chunks))
        print(f"\n▶ {cfg['name']}:")
        print(f"  • Total chunks produced: {len(chunks)}")
        print(f"  • Average tokens per chunk: ~{int(avg_tokens)}")
        if chunks:
            print(f"  • Sample Chunk 1 ID: {chunks[0].chunk_id}")
            print(f"    Text: \"{chunks[0].text[:120]}...\"")


if __name__ == "__main__":
    compare()
