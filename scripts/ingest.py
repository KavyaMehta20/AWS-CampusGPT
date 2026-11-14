"""Ingestion CLI Script (STEP 0 -> STEP 3).

Executes the end-to-end indexing pipeline:
1. Loads documents from data/raw/ if populated, otherwise data/sample/.
2. Splits into chunks using the configured CHUNKING_STRATEGY.
3. Generates vector embeddings with Gemini (cached to disk).
4. Stores vectors and text in the configured VectorStore (ChromaDB or FAISS).

Prints human-readable progress at every step:
e.g. "Loaded 3 files, 41 pages → 118 chunks → embedding batch 1/3 → stored 118 vectors"
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.config import settings
from backend.app.ingestion import load_documents
from backend.app.chunking import create_chunks
from backend.app.embeddings import GeminiEmbedder
from backend.app.vectorstore import get_vector_store


def run_ingest(source_dir: str = None):
    print("=" * 60)
    print("🎓 CampusGPT Knowledge Ingestion Pipeline")
    print("=" * 60)

    # 1. Resolve source folder
    if source_dir:
        input_path = Path(source_dir)
        print(f"Using explicitly specified source folder: {input_path}")
    else:
        raw_path = ROOT_DIR / "data" / "raw"
        raw_files = [f for f in raw_path.iterdir() if f.is_file() and not f.name.startswith(".")] if raw_path.exists() else []
        if raw_files:
            input_path = raw_path
            print(f"Detected {len(raw_files)} documents in data/raw/ -> Using REAL raw documents.")
        else:
            input_path = ROOT_DIR / "data" / "sample"
            print("Notice: data/raw/ is empty. Falling back to data/sample/ (FICTIONAL SAMPLE DATA).")

    # 2. Ingestion
    print(f"\n[Step 0] Loading documents from: {input_path}")
    snippets = load_documents(input_path)
    if not snippets:
        print("Error: No valid documents (.pdf, .docx, .md, .txt) found to ingest.")
        return

    unique_files = {s.source for s in snippets}
    pages_or_sections = len(snippets)
    print(f"✓ Loaded {len(unique_files)} files, {pages_or_sections} pages/sections.")

    # 3. Chunking
    print(f"\n[Step 1] Chunking with strategy: '{settings.chunking_strategy}' (Size: {settings.chunk_size}, Overlap: {settings.chunk_overlap})")
    chunks = create_chunks(
        snippets,
        strategy=settings.chunking_strategy,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        output_path=str(ROOT_DIR / "data" / "processed" / "chunks.jsonl")
    )
    print(f"✓ Generated {len(chunks)} chunks -> Saved to data/processed/chunks.jsonl")

    # 4. Embeddings
    print(f"\n[Step 2] Generating embeddings with model: '{settings.gemini_embedding_model}'")
    texts = [c.text for c in chunks]
    embedder = GeminiEmbedder()

    batch_size = 16
    total_batches = (len(texts) + batch_size - 1) // batch_size
    print(f"Embedding {len(texts)} chunks across {total_batches} batch(es)...")

    try:
        embeddings = embedder.embed_texts(texts, batch_size=batch_size)
        print(f"✓ Successfully computed {len(embeddings)} vector embeddings.")
    except Exception as e:
        print(f"\n❌ Embedding failed: {e}")
        print("Tip: If GEMINI_API_KEY is not configured yet, add it to your .env file.")
        return

    # 5. Vector Store
    print(f"\n[Step 3] Storing vectors in {settings.vector_store.upper()}...")
    store = get_vector_store()
    store.reset()
    store.add(chunks, embeddings)
    total_stored = store.count()
    print(f"✓ Stored {total_stored} vectors and metadata successfully!")
    print("\n🎉 Ingestion complete! CampusGPT is ready to answer questions.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documents into CampusGPT vector store")
    parser.add_argument("--source", type=str, default=None, help="Directory to load documents from (overrides default)")
    args = parser.parse_args()
    run_ingest(source_dir=args.source)
