"""Mock Gemini client and test fixtures for offline pytest execution."""

import pytest
from typing import List, Any
from unittest.mock import MagicMock

from backend.app.chunking.base import Chunk
from backend.app.ingestion.loader import DocumentSnippet


class MockGeminiEmbeddingItem:
    def __init__(self, values: List[float]):
        self.values = values


class MockGeminiEmbeddingResponse:
    def __init__(self, embeddings: List[MockGeminiEmbeddingItem]):
        self.embeddings = embeddings


class MockGeminiGenerateResponse:
    def __init__(self, text: str):
        self.text = text


class MockGeminiModels:
    def embed_content(self, model: str, contents: Any, **kwargs):
        # Generate predictable mock 8-dimensional vectors based on string length
        if isinstance(contents, str):
            contents = [contents]
        items = []
        for text in contents:
            val = float(len(text) % 10) / 10.0 + 0.1
            items.append(MockGeminiEmbeddingItem([val, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]))
        return MockGeminiEmbeddingResponse(items)

    def generate_content(self, model: str, contents: Any, **kwargs):
        return MockGeminiGenerateResponse(
            "Based on the official curriculum, the common business core includes 11 courses "
            "[Source: handbook.md, Section: Business Core]."
        )


class MockGenAIClient:
    def __init__(self, api_key: str = "mock-key"):
        self.models = MockGeminiModels()


@pytest.fixture
def mock_genai_client(monkeypatch):
    """Patch the GenAI client constructor to return our mock."""
    client = MockGenAIClient()
    monkeypatch.setattr("google.genai.Client", lambda *args, **kwargs: client)
    return client


@pytest.fixture
def sample_snippets() -> List[DocumentSnippet]:
    return [
        DocumentSnippet(
            text="The common business core consists of 11 courses including ACCT 110, ACCT 210, and MGMT 101.",
            source="handbook.md",
            section="Business Core",
            page=1,
            doc_id="test_doc_1"
        ),
        DocumentSnippet(
            text="Advising is mandatory before you enroll each semester. Book through Starfish.",
            source="handbook.md",
            section="Academic Advising",
            page=2,
            doc_id="test_doc_2"
        )
    ]
