"""Pydantic schemas for request and response models."""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming user chat request."""
    question: str = Field(..., description="The user's question about the university")


class SourceCitation(BaseModel):
    """Citation information for a chunk used in an answer."""
    source: str = Field(..., description="Filename or origin document")
    page_or_section: str = Field(..., description="Page number or section heading")
    snippet: str = Field(..., description="Short text excerpt from the document")


class GuardrailTraceItem(BaseModel):
    """Trace entry for an individual guardrail evaluation."""
    guard: str = Field(..., description="Guardrail name: Input, Retrieval, or Output")
    passed: bool = Field(..., description="Whether the check passed")
    reason: str = Field(..., description="Explanation of the evaluation")


class RetrievedChunkTrace(BaseModel):
    """Trace entry representing a retrieved chunk before/after reranking."""
    chunk_id: str
    source: str
    page_or_section: str
    relevance_score: float
    rerank_score: Optional[float] = None
    snippet: str


class ResponseTrace(BaseModel):
    """Detailed pipeline trace rendered by the teaching panel."""
    guardrails: List[GuardrailTraceItem] = Field(default_factory=list)
    initial_retrieval: List[RetrievedChunkTrace] = Field(default_factory=list)
    reranked_retrieval: List[RetrievedChunkTrace] = Field(default_factory=list)
    mcp_tool_used: Optional[str] = None
    mcp_result: Optional[Any] = None
    timings_ms: Dict[str, float] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    """Outbound chat response."""
    answer: str = Field(..., description="Generated answer or guardrail refusal")
    sources: List[SourceCitation] = Field(default_factory=list, description="Citations used")
    blocked: bool = Field(default=False, description="Whether guardrails intercepted the request")
    trace: Optional[ResponseTrace] = Field(default=None, description="Pipeline inspection trace")


class ConfigResponse(BaseModel):
    """Non-secret application configuration returned to the frontend."""
    university_name: str
    gemini_model: str
    gemini_embedding_model: str
    chunking_strategy: str
    chunk_size: int
    chunk_overlap: int
    vector_store: str
    top_k_candidates: int
    final_k: int
    reranker: str
    min_relevance: float
    enable_mcp: bool
