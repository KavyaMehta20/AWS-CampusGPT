"""Input guardrail validation (STEP 7 - Guardrails Checkpoint 1).

Teaching Note:
Prompt instructions alone are NOT a complete security solution!
Server-side deterministic validation, input filtering, secret management,
and output redactions are essential defense-in-depth layers.

Rule:
On a credentials, key, or system-info request, reply EXACTLY with:
"I can't provide private credentials or system information."
"""

import re
from pathlib import Path
from typing import Tuple, Dict, Any
import yaml

EXACT_INJECTION_REPLY = "I can't provide private credentials or system information."


def load_rules() -> Dict[str, Any]:
    """Load guardrail configurations from rules.yaml."""
    rules_path = Path(__file__).parent / "rules.yaml"
    if rules_path.exists():
        try:
            with open(rules_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            pass
    return {}


class InputGuard:
    """Validates user input before invoking retrieval or LLMs."""
    def __init__(self):
        self.rules = load_rules().get("input_guard", {})
        self.max_chars = self.rules.get("max_characters", 500)
        self.injection_phrases = [p.lower() for p in self.rules.get("injection_phrases", [])]
        self.inappropriate_phrases = [p.lower() for p in self.rules.get("inappropriate_phrases", [])]

    def validate(self, text: str) -> Tuple[bool, str, str]:
        """Validate user input.

        Returns:
            (passed: bool, refusal_reply: str, trace_reason: str)
        """
        # 1. Reject empty or whitespace-only input
        if not text or not text.strip():
            return False, "Please enter a valid question about the university.", "Empty input rejected"

        cleaned = text.strip()

        # 2. Reject input exceeding character limit
        if len(cleaned) > self.max_chars:
            return False, f"Question exceeds the maximum allowed length of {self.max_chars} characters.", f"Input too long ({len(cleaned)} > {self.max_chars})"

        lower_text = cleaned.lower()

        # 3. Detect prompt injection and credential extraction attempts
        for phrase in self.injection_phrases:
            if phrase in lower_text:
                return False, EXACT_INJECTION_REPLY, f"Prompt injection / credential probe detected: '{phrase}'"

        # 4. Inappropriate or exploit attempts
        for phrase in self.inappropriate_phrases:
            if phrase in lower_text:
                return False, "Your request contains disallowed phrases or formatting.", f"Disallowed phrase: '{phrase}'"

        return True, "", "Input passed all guardrail checks"
