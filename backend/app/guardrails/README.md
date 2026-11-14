# Guardrails Step (STEP 7)

CampusGPT applies a multi-layered guardrail defense matching Slide 13:

> **Important Concept:** Prompt instructions alone are NOT a complete security solution!
> A robust architecture implements server-side deterministic validation, input filtering, secret management, and output redaction.

## The Three Checkpoints:
1. **Input Guard (`input_guard.py`):**
   - Rejects empty questions or inputs exceeding `MAX_QUESTION_CHARS`.
   - Traps prompt injection, DAN mode, jailbreaks, and credential fishing attempts.
   - Exact refusal response: `I can't provide private credentials or system information.`
2. **Retrieval Guard (`retrieval_guard.py`):**
   - Restricts documents to approved sources.
   - Enforces `MIN_RELEVANCE` score floor.
   - Neutralizes injection triggers hidden inside retrieved documents (indirect prompt injection defense).
   - If nothing is relevant, skips the LLM call entirely and returns the standard refusal message.
3. **Output Guard (`output_guard.py`):**
   - Scans output with regex patterns to redact any leaked keys (`AIza...`).
   - Grounding check: ensures responses cite verified sources.

Students can tune thresholds and rules in `rules.yaml` without changing Python code.
