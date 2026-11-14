"""API Route definitions: POST /chat, GET /health, GET /config."""

from fastapi import APIRouter, HTTPException
from backend.app.config import settings
from backend.app.schemas import ChatRequest, ChatResponse, ConfigResponse
from backend.app.pipeline import ChatPipeline

router = APIRouter()
pipeline = ChatPipeline()


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Chat endpoint executing the CampusGPT RAG and guardrails pipeline."""
    try:
        response = pipeline.process_chat(request.question)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your question: {str(e)}"
        )


@router.get("/health")
def health_endpoint():
    """Health check endpoint."""
    return {"status": "ok", "service": "campusgpt"}


@router.get("/config", response_model=ConfigResponse)
def config_endpoint() -> ConfigResponse:
    """Non-secret runtime configuration returned for student inspection.
    Hard rule: Never exposes GEMINI_API_KEY.
    """
    return ConfigResponse(
        university_name=settings.university_name,
        gemini_model=settings.gemini_model,
        gemini_embedding_model=settings.gemini_embedding_model,
        chunking_strategy=settings.chunking_strategy,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        vector_store=settings.vector_store,
        top_k_candidates=settings.top_k_candidates,
        final_k=settings.final_k,
        reranker=settings.reranker,
        min_relevance=settings.min_relevance,
        enable_mcp=settings.enable_mcp
    )
