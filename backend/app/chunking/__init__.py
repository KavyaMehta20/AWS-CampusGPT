"""Chunking factory router and unified dispatcher."""

import json
from pathlib import Path
from typing import List, Callable
from backend.app.ingestion.loader import DocumentSnippet
from backend.app.chunking.base import Chunk, approximate_tokens
from backend.app.chunking.fixed import chunk_fixed
from backend.app.chunking.overlapping import chunk_overlapping
from backend.app.chunking.structure import chunk_structure
from backend.app.chunking.semantic import chunk_semantic

STRATEGIES: dict[str, Callable[..., List[Chunk]]] = {
    "fixed": chunk_fixed,
    "overlapping": chunk_overlapping,
    "structure": chunk_structure,
    "semantic": chunk_semantic
}


def create_chunks(
    snippets: List[DocumentSnippet],
    strategy: str = "overlapping",
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    save_to_jsonl: bool = True,
    output_path: str = "data/processed/chunks.jsonl"
) -> List[Chunk]:
    """Execute the configured chunking strategy and optionally write to chunks.jsonl.

    # WORKSHOP: You can swap the strategy with the CHUNKING_STRATEGY env var:
    # 'overlapping' (default), 'fixed', 'structure', or 'semantic'.
    """
    strategy_fn = STRATEGIES.get(strategy.lower(), chunk_overlapping)
    chunks = strategy_fn(snippets, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    if save_to_jsonl and chunks:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            for c in chunks:
                f.write(json.dumps(c.to_dict(), ensure_ascii=False) + "\n")

    return chunks


__all__ = [
    "Chunk",
    "approximate_tokens",
    "create_chunks",
    "chunk_fixed",
    "chunk_overlapping",
    "chunk_structure",
    "chunk_semantic",
    "STRATEGIES"
]
