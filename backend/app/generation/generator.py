"""Gemini generation engine module (STEP 6).

Calls Google Gemini API using google-genai SDK with:
- Configured model name from GEMINI_MODEL (never hardcoded)
- Temperature setting from config (default 0.2)
- Exponential backoff retry on 429 / quota exhaustion
- Extraction of cited sources
"""

import time
from typing import List, Dict, Any, Tuple, Optional
from backend.app.config import settings
from backend.app.schemas import SourceCitation
from backend.app.generation.prompts import (
    build_generation_prompt,
    FALLBACK_UNAVAILABLE_MESSAGE
)


class GeminiGenerator:
    """Invokes the Gemini model to synthesize answers from grounded context."""
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model
        self.temperature = settings.temperature
        self.university_name = settings.university_name
        self._client = None

    def _get_client(self):
        """Lazy initialization of Google GenAI client."""
        if self._client is not None:
            return self._client
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing! Please configure GEMINI_API_KEY in your .env file."
            )
        try:
            from google import genai
            # Use api_version='v1beta' to support system_instruction / developer instruction
            self._client = genai.Client(api_key=self.api_key, http_options={"api_version": "v1beta"})
            return self._client
        except ImportError:
            raise ImportError(
                "google-genai SDK is not installed. Install with 'pip install -r requirements.txt'."
            )

    def generate_answer(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        max_retries: int = 5
    ) -> Tuple[str, List[SourceCitation]]:
        """Generate a grounded response using retrieved context chunks."""
        if not context_chunks:
            return FALLBACK_UNAVAILABLE_MESSAGE, []

        system_instruction, user_content = build_generation_prompt(
            university_name=self.university_name,
            query=query,
            context_chunks=context_chunks
        )

        client = self._get_client()

        # Build citations list from chunks
        citations: List[SourceCitation] = []
        for c in context_chunks:
            snippet = c.get("text", "")[:150] + ("..." if len(c.get("text", "")) > 150 else "")
            sec = str(c.get("section") or (f"Page {c.get('page')}" if c.get("page") else "General"))
            citations.append(SourceCitation(
                source=str(c.get("source", "Unknown")),
                page_or_section=sec,
                snippet=snippet
            ))

        # API invocation with retry for rate limits
        delay = 1.0
        for attempt in range(max_retries):
            try:
                from google.genai import types

                config = types.GenerateContentConfig(
                    temperature=self.temperature,
                    system_instruction=system_instruction
                )

                response = client.models.generate_content(
                    model=self.model,
                    contents=user_content,
                    config=config
                )

                answer_text = response.text or ""
                return answer_text.strip(), citations

            except Exception as e:
                err_msg = str(e).lower()
                if "429" in err_msg or "quota" in err_msg or "resource_exhausted" in err_msg:
                    if attempt == max_retries - 1:
                        raise RuntimeError(
                            f"Gemini API rate limit exceeded (429) after {max_retries} attempts. "
                            "Please check your Google AI Studio quota."
                        ) from e
                    time.sleep(delay)
                    delay *= 2.0
                else:
                    raise e

        return FALLBACK_UNAVAILABLE_MESSAGE, citations
