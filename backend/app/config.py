"""Application configuration module.

Reads environment variables from .env using Pydantic Settings.
Hard rules:
- No hardcoded secrets.
- No hardcoded model names (read from GEMINI_MODEL and GEMINI_EMBEDDING_MODEL).
"""

from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Explicit path to .env file relative to repository root
ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    """Central configuration settings for CampusGPT."""
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # API Keys & Gemini Config
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-flash", alias="GEMINI_MODEL")
    gemini_embedding_model: str = Field(default="gemini-embedding-001", alias="GEMINI_EMBEDDING_MODEL")

    # Application & University Identity
    university_name: str = Field(default="RIT Dubai", alias="UNIVERSITY_NAME")
    temperature: float = Field(default=0.2, alias="TEMPERATURE")
    max_question_chars: int = Field(default=500, alias="MAX_QUESTION_CHARS")
    include_trace: bool = Field(default=True, alias="INCLUDE_TRACE")
    allowed_origins: str = Field(default="*", alias="ALLOWED_ORIGINS")

    # Chunking
    chunking_strategy: str = Field(default="overlapping", alias="CHUNKING_STRATEGY")
    chunk_size: int = Field(default=500, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, alias="CHUNK_OVERLAP")

    # Retrieval & Vector Store
    vector_store: str = Field(default="chroma", alias="VECTOR_STORE")
    top_k_candidates: int = Field(default=20, alias="TOP_K_CANDIDATES")
    final_k: int = Field(default=5, alias="FINAL_K")
    min_relevance: float = Field(default=0.25, alias="MIN_RELEVANCE")
    reranker: str = Field(default="lexical", alias="RERANKER")

    # MCP
    enable_mcp: bool = Field(default=False, alias="ENABLE_MCP")

    @property
    def cors_origins(self) -> List[str]:
        """Return allowed origins as a parsed list."""
        if self.allowed_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


# Global settings singleton
settings = Settings()
