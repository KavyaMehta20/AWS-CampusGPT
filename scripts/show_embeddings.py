"""Show Embeddings Cosine Similarity (Slide 7 Demo).

Embeds three phrases and prints their pairwise cosine similarity:
- Phrase A: "How do I register for courses?"
- Phrase B: "What is the course enrollment process?"
- Phrase C: "What is the weather today?"

Demonstrates how semantically related phrases have high similarity scores,
while topically unrelated phrases have low scores.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.embeddings import GeminiEmbedder, cosine_similarity


def demo():
    print("=" * 60)
    print("🧭 Embeddings & Cosine Similarity Demo (Slide 7)")
    print("=" * 60)

    phrases = [
        "How do I register for courses?",
        "What is the course enrollment process?",
        "What is the weather today?"
    ]

    print("\nPhrases to embed:")
    print(f"  [A]: \"{phrases[0]}\"")
    print(f"  [B]: \"{phrases[1]}\"")
    print(f"  [C]: \"{phrases[2]}\"")

    embedder = GeminiEmbedder()

    try:
        vectors = embedder.embed_texts(phrases)
    except Exception as e:
        print(f"\n❌ Embedding failed: {e}")
        print("Note: In offline/mock mode or before setting GEMINI_API_KEY, use the unit tests.")
        return

    sim_ab = cosine_similarity(vectors[0], vectors[1])
    sim_ac = cosine_similarity(vectors[0], vectors[2])
    sim_bc = cosine_similarity(vectors[1], vectors[2])

    print("\n📊 Pairwise Cosine Similarity Scores (Range -1.0 to 1.0):")
    print("-" * 55)
    print(f"  Similarity(A, B) [Enrollment vs Registration]: {sim_ab:.4f}  <-- High Semantic Match!")
    print(f"  Similarity(A, C) [Registration vs Weather]:    {sim_ac:.4f}  <-- Low (Unrelated)")
    print(f"  Similarity(B, C) [Enrollment vs Weather]:      {sim_bc:.4f}  <-- Low (Unrelated)")
    print("-" * 55)
    print("Conclusion: Dense vector embeddings capture semantic meaning rather than exact word matches.")


if __name__ == "__main__":
    demo()
