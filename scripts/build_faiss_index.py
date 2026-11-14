"""Build FAISS Index Script for AWS Lambda Deployment.

Exports the vector store into a lightweight FAISS binary index and companion
JSON metadata file ready for packaging into an AWS Lambda container/layer or S3 upload.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.ingestion import load_documents
from backend.app.chunking import create_chunks
from backend.app.embeddings import GeminiEmbedder
from backend.app.vectorstore.faiss_store import FaissVectorStore


def build_faiss():
    print("=" * 60)
    print("⚡ Building Portable FAISS Vector Index for AWS Lambda")
    print("=" * 60)

    raw_path = ROOT_DIR / "data" / "raw"
    sample_path = ROOT_DIR / "data" / "sample"
    data_path = raw_path if any(raw_path.glob("*.*")) else sample_path

    print(f"1. Loading documents from: {data_path}")
    snippets = load_documents(data_path)
    chunks = create_chunks(snippets, strategy="overlapping", chunk_size=500, chunk_overlap=50)
    print(f"✓ Generated {len(chunks)} chunks.")

    print("2. Computing embeddings with Gemini...")
    embedder = GeminiEmbedder()
    try:
        texts = [c.text for c in chunks]
        embeddings = embedder.embed_texts(texts)
    except Exception as e:
        print(f"❌ Failed to compute embeddings: {e}")
        return

    print("3. Exporting FAISS index and metadata...")
    store = FaissVectorStore(
        index_file=str(ROOT_DIR / "vectorstore" / "faiss_index.bin"),
        meta_file=str(ROOT_DIR / "vectorstore" / "faiss_meta.json")
    )
    store.reset()
    store.add(chunks, embeddings)
    print(f"✓ FAISS index successfully created with {store.count()} vectors.")
    print(f"  • Index file: vectorstore/faiss_index.bin")
    print(f"  • Metadata:   vectorstore/faiss_meta.json")
    print("Ready for S3 upload or deployment packaging!")


if __name__ == "__main__":
    build_faiss()
