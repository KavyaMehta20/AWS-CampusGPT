# Chunking Step (STEP 1)

This directory contains chunking strategies that transform raw document snippets into sized, indexable chunks.

## Strategies Available
All strategies share the exact same function signature so you can switch them via `.env` with `CHUNKING_STRATEGY`:

1. `overlapping` (`overlapping.py`): **Default**. Fixed token size with a sliding overlap window (default 500 size, 50 overlap).
2. `fixed` (`fixed.py`): Splits after N tokens without overlap.
3. `structure` (`structure.py`): Splits on natural paragraph and heading boundaries, then respects size limits.
4. `semantic` (`semantic.py`): Splits on sentence boundaries and topical shifts without mid-sentence clipping.

Generated chunks are automatically recorded into `data/processed/chunks.jsonl` for inspection.
