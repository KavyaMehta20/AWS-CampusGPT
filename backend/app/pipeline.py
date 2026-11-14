"""Main CampusGPT Chat Pipeline.

Readable, step-by-step chat orchestration:
1. Input Guardrail
2. Vector Retrieval (Step 4)
3. Reranking (Step 5)
4. Retrieval Guardrail
5. Generation with Gemini (Step 6)
6. Output Guardrail
"""

import time
from typing import Dict, Any, Optional

from backend.app.config import settings
from backend.app.schemas import (
    ChatResponse,
    ResponseTrace,
    GuardrailTraceItem,
    RetrievedChunkTrace,
    SourceCitation
)
from backend.app.guardrails import InputGuard, RetrievalGuard, OutputGuard
from backend.app.retrieval import Retriever
from backend.app.reranking import rerank_candidates
from backend.app.generation import GeminiGenerator, FALLBACK_UNAVAILABLE_MESSAGE
from backend.app.mcp_client import CampusMCPClient


class ChatPipeline:
    """End-to-end chat orchestration pipeline."""
    def __init__(self):
        self.input_guard = InputGuard()
        self.retriever = Retriever()
        self.retrieval_guard = RetrievalGuard()
        self.generator = GeminiGenerator()
        self.output_guard = OutputGuard()
        self.mcp_client = CampusMCPClient()

    def process_chat(self, question: str) -> ChatResponse:
        """Execute the chat pipeline and construct response with debugging trace."""
        start_time = time.time()
        trace = ResponseTrace()

        # STEP 1: Input Guardrail Check
        in_pass, in_refusal, in_reason = self.input_guard.validate(question)
        trace.guardrails.append(GuardrailTraceItem(guard="Input Guard", passed=in_pass, reason=in_reason))
        if not in_pass:
            trace.timings_ms["total"] = round((time.time() - start_time) * 1000, 2)
            return ChatResponse(
                answer=in_refusal,
                sources=[],
                blocked=True,
                trace=trace if settings.include_trace else None
            )

        # STEP 2: Optional MCP Tool Handling (e.g. course or calendar question)
        if settings.enable_mcp and self.mcp_client.is_available():
            q_lower = question.lower()
            if any(term in q_lower for term in ["course", "prereq", "credits", "class"]):
                # Simple keyword heuristic demonstration for MCP tool
                code_match = [w for w in question.split() if any(c.isdigit() for c in w)]
                if code_match:
                    tool_res = self.mcp_client.call_tool("get_course_info", {"course_code": code_match[0]})
                    trace.mcp_tool_used = "get_course_info"
                    trace.mcp_result = tool_res

        # STEP 3: Vector Candidate Retrieval
        t_ret_start = time.time()
        try:
            candidates = self.retriever.retrieve(question)
        except Exception as e:
            trace.guardrails.append(GuardrailTraceItem(guard="Retrieval", passed=False, reason=f"Retriever error: {e}"))
            candidates = []
        trace.timings_ms["retrieval"] = round((time.time() - t_ret_start) * 1000, 2)

        for c in candidates:
            trace.initial_retrieval.append(RetrievedChunkTrace(
                chunk_id=c.get("chunk_id", ""),
                source=c.get("source", ""),
                page_or_section=str(c.get("section") or c.get("page") or ""),
                relevance_score=c.get("relevance_score", 0.0),
                snippet=c.get("text", "")[:120]
            ))

        # STEP 4: Reranking
        t_rerank_start = time.time()
        reranked = rerank_candidates(question, candidates)
        trace.timings_ms["reranking"] = round((time.time() - t_rerank_start) * 1000, 2)

        for c in reranked:
            trace.reranked_retrieval.append(RetrievedChunkTrace(
                chunk_id=c.get("chunk_id", ""),
                source=c.get("source", ""),
                page_or_section=str(c.get("section") or c.get("page") or ""),
                relevance_score=c.get("relevance_score", 0.0),
                rerank_score=c.get("rerank_score"),
                snippet=c.get("text", "")[:120]
            ))

        # STEP 5: Retrieval Guardrail Check
        ret_pass, safe_chunks, ret_refusal, ret_reason = self.retrieval_guard.validate(reranked)
        trace.guardrails.append(GuardrailTraceItem(guard="Retrieval Guard", passed=ret_pass, reason=ret_reason))
        if not ret_pass:
            trace.timings_ms["total"] = round((time.time() - start_time) * 1000, 2)
            return ChatResponse(
                answer=ret_refusal,
                sources=[],
                blocked=False,
                trace=trace if settings.include_trace else None
            )

        # STEP 6: Generation with Gemini
        t_gen_start = time.time()
        try:
            raw_answer, citations = self.generator.generate_answer(question, safe_chunks)
        except Exception as e:
            trace.guardrails.append(GuardrailTraceItem(guard="Generation", passed=False, reason=f"Gemini API error: {e}"))
            raw_answer, citations = FALLBACK_UNAVAILABLE_MESSAGE, []
        trace.timings_ms["generation"] = round((time.time() - t_gen_start) * 1000, 2)

        # STEP 7: Output Guardrail Check
        out_pass, final_answer, out_reason = self.output_guard.validate(raw_answer, citations, safe_chunks)
        trace.guardrails.append(GuardrailTraceItem(guard="Output Guard", passed=out_pass, reason=out_reason))

        trace.timings_ms["total"] = round((time.time() - start_time) * 1000, 2)
        return ChatResponse(
            answer=final_answer,
            sources=citations if out_pass else [],
            blocked=not out_pass,
            trace=trace if settings.include_trace else None
        )
