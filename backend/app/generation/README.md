# Generation Step (STEP 6)

This directory controls how the generative model crafts student responses:

- `prompts.py`: Defines the system instruction and strict grounding rules.
  - Treats retrieved document chunks as **untrusted data**, not system instructions.
  - Demands exact refusal fallback if context is missing.
  - Requires in-line citations.
- `generator.py`: Communicates with Google's GenAI API using model `GEMINI_MODEL` (e.g. `gemini-2.5-flash`), with exponential backoff retry on 429 errors.
