# CampusGPT: Beginner-Friendly University AI Assistant

> **"Build Your First AI Chatbot: From LLM APIs to RAG, Guardrails & AWS Deployment"**  
> A 90-minute hands-on workshop repository for university students.

---

## 5-Line Quick Start (For Workshop Attendees)

```bash
# 1. Clone & Enter
git clone https://github.com/your-org/campusgpt.git && cd campusgpt

# 2. Setup environment (Copy .env and paste your GEMINI_API_KEY)
cp .env.example .env

# 3. Ingest documents into the vector store
python scripts/ingest.py

# 4. Start the application
uvicorn backend.app.main:app --reload --port 8000

# 5. Open your browser at http://localhost:8000
```

---

## What is CampusGPT?

CampusGPT is an enterprise-grade, beginner-readable AI university assistant built on the official **Google GenAI SDK** (`gemini-2.5-flash` and `gemini-embedding-001`).

Instead of training or fine-tuning models, CampusGPT demonstrates **AI Application Engineering**:
- **Ingestion & Parsing:** Extracts structured text from PDFs, DOCX, Markdown, and TXT.
- **Smart Chunking:** Fixed, Overlapping, Structure-Aware, and Semantic-Shift chunking strategies.
- **Vector Search:** ChromaDB (persisted locally) and FAISS (optimized for serverless Lambda execution).
- **Reranking:** Hybrid scoring combining vector cosine distance with BM25 lexical keyword matching.
- **Strict Grounding:** Delimited context injection with mandatory source citations and fallback refusals.
- **3-Checkpoint Guardrails:** Deterministic Input Guard, Retrieval Guard, and Output Guard (secret redaction & prompt-injection traps).
- **Model Context Protocol (MCP):** Real MCP server exposing course and calendar tools over `stdio`.

---

## Repository Map

```
campusgpt/
├── README.md                          # Quick start & repository overview
├── WORKSHOP_GUIDE.md                  # Slide-to-folder mapping + 4 hands-on experiments
├── RUN_GUIDE.md                       # Complete step-by-step installation & run guide
├── .env.example                       # All environment settings with default values
├── requirements.txt                   # Light, verified Python dependencies
├── requirements-optional.txt          # PyTorch cross-encoder & heavy packages
├── .devcontainer/devcontainer.json    # GitHub Codespaces 1-click devcontainer
│
├── data/
│   ├── raw/                           # Knowledge Base: Real university documents (e.g. RIT)
│   ├── sample/                        # Fictional Sample University handbook & databases
│   └── processed/                     # Chunks output (chunks.jsonl) for student inspection
│
├── vectorstore/                       # ChromaDB persistent vector storage (gitignored)
│
├── backend/app/
│   ├── main.py                        # FastAPI application; serves frontend at "/"
│   ├── config.py                      # Pydantic configuration loaded from .env
│   ├── schemas.py                     # Request/response and trace schemas
│   ├── pipeline.py                    # Complete RAG & guardrail chat flow in ~30 lines
│   ├── ingestion/                     # STEP 0: Loading PDF, DOCX, MD, TXT + metadata
│   ├── chunking/                      # STEP 1: 4 interchangeable chunking strategies
│   ├── embeddings/                    # STEP 2: Gemini embeddings, disk caching & cosine math
│   ├── vectorstore/                   # STEP 3: Unified ChromaDB & FAISS vector stores
│   ├── retrieval/                     # STEP 4: Query embedding & top-K candidate search
│   ├── reranking/                     # STEP 5: Lexical & cross-encoder candidate rerankers
│   ├── generation/                    # STEP 6: System prompts & Gemini answer synthesis
│   ├── guardrails/                    # STEP 7: Input, Retrieval, and Output defense rules
│   └── mcp_client/                    # STEP MCP: Connects application to MCP Server
│
├── mcp_server/                        # Independent Model Context Protocol server
├── frontend/                          # Zero-build HTML, CSS & JS (Navy & Orange design)
├── scripts/                           # Self-contained CLI scripts for each workshop concept
├── deploy/aws/                        # AWS SAM template, Mangum Lambda handler & guide
├── tests/                             # Offline pytest suite with mocked Gemini clients
└── docs/                              # Verified dependency versions & architecture docs
```

---

## Key Workshop Hotspots (`# WORKSHOP:`)
Look for `# WORKSHOP:` comments across the code to customize CampusGPT:
1. `backend/app/generation/prompts.py`: Edit system instructions, tone, and formatting rules.
2. `backend/app/guardrails/rules.yaml`: Add injection phrases and regex security patterns.
3. `backend/app/chunking/`: Experiment with chunk sizes and overlap windows.
4. `.env`: Toggle vector stores, rerankers, temperature, and MCP tools.
