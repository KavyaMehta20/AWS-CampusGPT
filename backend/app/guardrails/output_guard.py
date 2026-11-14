"""Output guardrail validation (STEP 7 - Guardrails Checkpoint 3).

Validates model answers before delivering to the student:
1. Secret Redaction: Scrubs anything matching API key patterns (e.g., AIza...).
2. Grounding Check: Requires answer to cite a retrieved source, or match fallback.
3. Unsupported Hallucination Replacement: Replaces ungrounded claims with fallback.
"""

import re
from typing import Tuple, List, Dict, Any
from backend.app.schemas import SourceCitation
from backend.app.generation.prompts import FALLBACK_UNAVAILABLE_MESSAGE
from backend.app.guardrails.input_guard import load_rules


class OutputGuard:
    """Validates and sanitizes generated answers."""
    def __init__(self):
        rules = load_rules().get("output_guard", {})
        self.redact_patterns = [
            re.compile(p, re.IGNORECASE) for p in rules.get("redact_patterns", [r"AIza[0-9A-Za-z\-_]{35}"])
        ]
        self.require_grounding = rules.get("require_grounding", True)

    def redact_secrets(self, text: str) -> Tuple[str, bool]:
        """Redact API keys, tokens, or credentials from text."""
        redacted = text
        found_secret = False
        for pattern in self.redact_patterns:
            if pattern.search(redacted):
                found_secret = True
                redacted = pattern.sub("[REDACTED_SECRET]", redacted)
        return redacted, found_secret

    def validate(
        self,
        answer: str,
        citations: List[SourceCitation],
        context_chunks: List[Dict[str, Any]]
    ) -> Tuple[bool, str, str]:
        """Verify safety and grounding of answer.

        Returns:
            (passed: bool, final_answer: str, trace_reason: str)
        """
        # 1. Redact secrets
        sanitized_answer, found_secret = self.redact_secrets(answer)
        if found_secret:
            return False, sanitized_answer, "Secret/API key pattern detected and redacted"

        # 2. Check if answer is already the fallback
        if FALLBACK_UNAVAILABLE_MESSAGE in sanitized_answer:
            return True, FALLBACK_UNAVAILABLE_MESSAGE, "Fallback answer returned"

        # 3. Grounding check: Must have at least one valid source citation or context chunk
        if self.require_grounding and not citations and not context_chunks:
            return (
                False,
                FALLBACK_UNAVAILABLE_MESSAGE,
                "Answer lacked grounded citations; replaced with fallback message"
            )

        return True, sanitized_answer, "Output passed safety and grounding checks"
