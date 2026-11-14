# Retrieval Step (STEP 4)

This directory implements query embedding and candidate retrieval:

1. Takes the user query and embeds it with `gemini-embedding-001`.
2. Queries the vector store for `TOP_K_CANDIDATES` (default: 20).
3. Applies `MIN_RELEVANCE` (default: 0.25) to discard unrelated documents before reranking.
