# WORKSHOP GUIDE: Slide-to-Folder Mapping & Student Experiments

Welcome to the **CampusGPT Workshop: "Build Your First AI Chatbot: From LLM APIs to RAG, Guardrails & AWS Deployment"**!

This guide is designed for university students to directly connect each concept presented on the slides with its corresponding folder and implementation file in this repository.

---

## 1. Slide to Folder & File Mapping

| Slide | Concept | Where in the repo | Description & Learning Focus |
|---|---|---|---|
| **4** | **Gemini API Call** | `backend/app/generation/` | Direct model invocation with `gemini-2.5-flash`, temperature controls, system instructions, and exponential backoff retry. |
| **6** | **Chunking Strategies** | `backend/app/chunking/`<br>`scripts/inspect_chunks.py` | Implementation of `overlapping`, `fixed`, `structure`, and `semantic` chunking behind one clean interface. Inspect with `inspect_chunks.py`. |
| **7** | **Dense Embeddings** | `backend/app/embeddings/`<br>`scripts/show_embeddings.py` | `gemini-embedding-001` integration, disk caching by hash, and geometric cosine similarity between phrases. |
| **8** | **Vector Database** | `backend/app/vectorstore/`<br>`vectorstore/` | Unified `VectorStore` interface with ChromaDB (local persistence) and FAISS (fast in-memory/Lambda search). |
| **9** | **Full RAG Pipeline** | `backend/app/pipeline.py`<br>`scripts/ingest.py` | Complete orchestration from ingestion to query embedding, candidate retrieval, reranking, and generation. |
| **10** | **Reranking** | `backend/app/reranking/` | Composite lexical scoring (60% vector + 40% keyword overlap) vs cross-encoders to refine candidate ordering. |
| **11** | **Model Context Protocol (MCP)** | `mcp_server/`<br>`backend/app/mcp_client/`<br>`scripts/mcp_demo.py` | Decoupled tool server exposing course details and calendar milestones over `stdio` without tight application coupling. |
| **13** | **Guardrails & Security** | `backend/app/guardrails/`<br>`rules.yaml`<br>`scripts/test_injection.py` | 3-checkpoint defense: Input Guard, Retrieval Guard, and Output Guard (secret redaction & exact refusal replies). |
| **14** | **Running the Application** | `RUN_GUIDE.md` | Step-by-step local and Codespaces guide to run backend & frontend together. |
| **15** | **Student Experiments** | Below in Section 2 | 4 hands-on customization challenges for students during the workshop. |
| **16** | **AWS Serverless Deployment** | `deploy/aws/` | AWS Lambda (Mangum) + HTTP API Gateway + Secrets Manager + FAISS vector search in `/tmp`. |

---

## 2. Slide 15: Student Hands-on Experiments

Try each of these four exercises in your Codespace or local machine:

### Experiment 1: Chunking Strategy Optimization
- **Goal:** Observe how different chunking techniques affect the granularity of knowledge.
- **File to Edit:** `.env` (or run `scripts/compare_chunking.py`).
- **Steps:**
  1. Open `.env` and change `CHUNK_SIZE=200` and `CHUNK_OVERLAP=20`.
  2. Run the comparison script:
     ```bash
     python scripts/compare_chunking.py
     ```
  3. Change `CHUNKING_STRATEGY=structure` in `.env` and re-ingest:
     ```bash
     python scripts/ingest.py
     ```
  4. Ask: *"What are the 11 courses in the common business core?"* in the UI. Did the smaller or structured chunks capture all 11 courses without truncation?

### Experiment 2: Prompt Engineering & Persona Tuning
- **Goal:** Customize the chatbot's voice, formatting, and strictness.
- **File to Edit:** [backend/app/generation/prompts.py](backend/app/generation/prompts.py) (`# WORKSHOP:` hot spot).
- **Steps:**
  1. Locate `SYSTEM_PROMPT_TEMPLATE`.
  2. Modify the persona: tell CampusGPT to answer in bullet points, adopt an energetic peer-mentor persona, or include an encouraging sign-off:
     ```python
     # WORKSHOP: Try adding this instruction:
     # "Always format course prerequisites with bold bullet points and end with a friendly emoji!"
     ```
  3. Save the file (FastAPI will auto-reload) and ask a course question in the chat UI. Observe how the answer structure transforms.

### Experiment 3: Retrieval & Reranking Tuning
- **Goal:** See the before/after effect of lexical reranking.
- **File to Edit:** `.env`
- **Steps:**
  1. Set `TOP_K_CANDIDATES=20` and `FINAL_K=3`.
  2. Try setting `RERANKER=none`, ask a question, and open the collapsible **"🔍 How CampusGPT answered"** panel under the chat bubble.
  3. Now set `RERANKER=lexical` in `.env`.
  4. Ask the same question again. Notice how chunks with high keyword overlap leap from position #12 up to #1 in the reranked list!

### Experiment 4: Guardrails Challenge
- **Goal:** Edit rules without touching code and test defense boundaries.
- **File to Edit:** [backend/app/guardrails/rules.yaml](backend/app/guardrails/rules.yaml)
- **Steps:**
  1. Add a new disallowed phrase under `inappropriate_phrases` (e.g., `- "cheat sheet"`).
  2. Run the injection attack suite:
     ```bash
     python scripts/test_injection.py
     ```
  3. **Mini Challenge:** Can you craft a sneaky prompt that convinces CampusGPT to give you information not in the university document without triggering the guardrail? Notice how the grounding check and the exact refusal reply (`I can't provide private credentials or system information.`) hold the line!
