# Reranking Step (STEP 5)

This directory refines initial retrieved chunks to pick the most relevant `FINAL_K` passages.

## Supported Strategies:
- `lexical` (**Default**): Fast, lightweight composite scoring combining cosine vector similarity (60%) and exact keyword overlap (40%). Requires no heavy dependencies.
- `none`: Truncates candidates to `FINAL_K` keeping the original retrieval order.
- `cross_encoder`: Neural deep-learning cross-encoder model via `sentence-transformers` (optional heavy package).

The pipeline records both the initial retrieval order and the reranked order in the trace so students can inspect the before/after effects.
