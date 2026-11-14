"""Retrieval guardrail validation (STEP 7 - Guardrails Checkpoint 2).

Validates retrieved chunks:
1. Only uses chunks from allowed university document sources.
2. Checks that at least one chunk satisfies the minimum relevance threshold.
3. If nothing relevant is found, halts the pipeline early (skips LLM call)
   and returns the standard fallback message.
4. Neutralizes instruction-like text inside chunks to prevent indirect injection.
"""

import re
import fnmatch
from typing import List, Dict, Any, Tuple
from backend.app.config import settings
from backend.app.generation.prompts import FALLBACK_UNAVAILABLE_MESSAGE
from backend.app.guardrails.input_guard import load_rules


class RetrievalGuard:
    """Validates retrieved chunks before passing to generation."""
    def __init__(self):
        rules = load_rules().get("retrieval_guard", {})
        self.allowed_sources = rules.get("allowed_sources", ["*.md", "*.txt", "*.pdf", "*.docx", "*.json"])
        self.min_relevance = rules.get("min_relevance_threshold", settings.min_relevance)

    def is_source_allowed(self, source_name: str) -> bool:
        """Check if source filename matches allowlist patterns."""
        for pattern in self.allowed_sources:
            if fnmatch.fnmatch(source_name.lower(), pattern.lower()):
                return True
        return False

    def neutralize_chunk_text(self, text: str) -> str:
        """Sanitize instruction-like keywords inside document chunks (indirect injection defense)."""
        # Neutralize common indirect injection attack triggers
        neutralized = re.sub(
            r'(?i)\b(ignore all previous instructions|system instruction|reveal api key|system prompt)\b',
            '[SANITIZED_INSTRUCTION]',
            text
        )
        return neutralized

    def validate(self, chunks: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]], str, str]:
        """Validate, filter, and sanitize retrieved chunks.

        Returns:
            (passed: bool, sanitized_chunks: list, refusal_reply: str, trace_reason: str)
        """
        if not chunks:
            return False, [], FALLBACK_UNAVAILABLE_MESSAGE, "No candidate chunks retrieved"

        valid_chunks: List[Dict[str, Any]] = []
        for c in chunks:
            source = c.get("source", "")
            if not self.is_source_allowed(source):
                continue
            if c.get("relevance_score", 0.0) < self.min_relevance:
                continue

            c_clean = dict(c)
            c_clean["text"] = self.neutralize_chunk_text(c.get("text", ""))
            valid_chunks.append(c_clean)

        if not valid_chunks:
            return (
                False,
                [],
                FALLBACK_UNAVAILABLE_MESSAGE,
                f"No chunks met relevance threshold of {self.min_relevance}"
            )

        return True, valid_chunks, "", f"{len(valid_chunks)} chunks approved for generation"
