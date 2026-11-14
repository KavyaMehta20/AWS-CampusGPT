# Scripts Directory

One self-contained command per concept so students can run and experiment with each step individually:

| Script | Concept Demonstrated | Usage |
|---|---|---|
| `ingest.py` | Full indexing pipeline (Load → Chunk → Embed → Store) | `python scripts/ingest.py` |
| `inspect_chunks.py` | Inspect chunks & token approximations from `data/processed` | `python scripts/inspect_chunks.py` |
| `compare_chunking.py` | Side-by-side comparison of fixed, overlapping, structure, and semantic strategies | `python scripts/compare_chunking.py` |
| `show_embeddings.py` | Slide 7 phrase embeddings and pairwise cosine similarity calculation | `python scripts/show_embeddings.py` |
| `ask_cli.py` | Terminal chat client printing answer, sources, and full trace | `python scripts/ask_cli.py "question"` |
| `test_injection.py` | Runs 8 prompt-injection and security attack tests | `python scripts/test_injection.py` |
| `mcp_demo.py` | Connects to MCP server, lists tools, and executes calls (<40 lines output) | `python scripts/mcp_demo.py` |
| `build_faiss_index.py` | Generates lightweight FAISS index for AWS Lambda deployment | `python scripts/build_faiss_index.py` |
