"""Terminal Ask CLI with Full Trace Printout.

Allows students to query CampusGPT directly from their terminal
and inspect every step of the trace (Guardrails, Retrieval, Rerank, Latency).
"""

import sys
import argparse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.pipeline import ChatPipeline


def ask(question: str):
    print("=" * 65)
    print("💬 CampusGPT CLI Query")
    print(f"Question: \"{question}\"")
    print("=" * 65)

    pipeline = ChatPipeline()
    response = pipeline.process_chat(question)

    print("\n[ANSWER]")
    print(response.answer)

    if response.sources:
        print("\n[SOURCES CITED]")
        for s in response.sources:
            print(f"  • {s.source} ({s.page_or_section})")

    if response.trace:
        t = response.trace
        print("\n[TEACHING TRACE]")
        print("1. Guardrail Status:")
        for g in t.guardrails:
            status = "PASSED" if g.passed else "BLOCKED"
            print(f"   [{status}] {g.guard}: {g.reason}")

        print(f"2. Retrieved Candidates: {len(t.initial_retrieval)}")
        for i, c in enumerate(t.initial_retrieval[:3]):
            print(f"   #{i+1} [Score {c.relevance_score}] {c.source} ({c.page_or_section})")

        print(f"3. After Reranking ({len(t.reranked_retrieval)} chunks):")
        for i, c in enumerate(t.reranked_retrieval[:3]):
            print(f"   #{i+1} [Rerank Score {c.rerank_score}] {c.source} ({c.page_or_section})")

        if t.mcp_tool_used:
            print(f"4. MCP Tool Invoked: {t.mcp_tool_used}")

        print(f"5. Latencies: {t.timings_ms}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ask CampusGPT a question from terminal")
    parser.add_argument("question", nargs="?", default="What are the common business core courses?", help="The question to ask")
    args = parser.parse_args()
    ask(args.question)
