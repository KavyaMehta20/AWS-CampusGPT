# Embeddings Step (STEP 2)

This directory manages text embeddings via the official `google-genai` SDK using `gemini-embedding-001`.

## Important Concept
> **The embedding model and the generation model do DIFFERENT jobs:**
> - The **embedding model** converts textual semantics into high-dimensional geometric coordinates.
> - The **generation model** (e.g. Gemini 2.5 Flash) synthesizes natural language answers based on retrieved context.

## Key Features
- **Disk Caching:** Embeddings are cached in `.cache/embeddings/` keyed by SHA/MD5 hash. Re-running ingestion on identical text incurs zero additional API calls or quota consumption.
- **Rate-limit Retry:** Automatic exponential backoff retries if free-tier rate limits (HTTP 429) are encountered.
- **Math Utilities:** Built-in `cosine_similarity(a, b)` function to measure geometric alignment between query and chunk vectors.
