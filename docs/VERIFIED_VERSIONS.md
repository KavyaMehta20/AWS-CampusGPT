# Verified Dependencies and Model IDs for CampusGPT

**Verification Date:** November 14, 2026  
**Reference Sources:** Official Google Gemini API Documentation (`ai.google.dev`), ModelContextProtocol Python SDK (`modelcontextprotocol.io`), PyPI package registry.

---

## 1. Google GenAI Python SDK (`google-genai`)

- **Package Name:** `google-genai` (replaces legacy `google-generativeai`).
- **Verified Version Range:** `>=1.0.0, <2.0.0`
- **Client Import:**
  ```python
  from google import genai
  from google.genai import types

  # Automatically reads GEMINI_API_KEY from environment or explicit api_key param
  client = genai.Client(api_key=api_key)
  ```
- **Text Generation API:**
  ```python
  response = client.models.generate_content(
      model=model_name,
      contents=prompt,
      config=types.GenerateContentConfig(
          temperature=0.2,
          system_instruction=system_prompt,
      )
  )
  answer_text = response.text
  ```

---

## 2. Gemini Model IDs & Status

| Model ID | Verified Status | Purpose / Role in CampusGPT | Notes |
|---|---|---|---|
| `gemini-2.5-flash` | **Active / Recommended** | Primary Generation Model (`GEMINI_MODEL`) | High-speed, low-latency, 1M context window, reasoning/thinking capabilities. Free-tier available. |
| `gemini-2.0-flash` | Legacy / Deprecated | Retired in newer SDK baselines | Do not use as default. |
| `gemini-1.5-flash` | Legacy / Superseded | Older Generation | Superseded by 2.5 Flash. |
| `gemini-embedding-001` | **Active / Recommended** | Primary Embedding Model (`GEMINI_EMBEDDING_MODEL`) | Google's primary unified text embedding model (replaces retired `text-embedding-004`). |
| `text-embedding-004` | **Retired / Deprecated** | Returns 404 on API endpoints | Officially shut down by Google. Replaced by `gemini-embedding-001`. |

### Embedding API Call:
```python
response = client.models.embed_content(
    model="gemini-embedding-001",
    contents=["Text chunk 1", "Text chunk 2"],
)
# Returns response.embeddings list containing .values
```

---

## 3. Model Context Protocol (MCP) Python SDK

- **Package Name:** `mcp>=1.2.0` (with `fastmcp` support)
- **Verified Server Usage:**
  ```python
  from mcp.server.fastmcp import FastMCP

  mcp = FastMCP("campusgpt-server")

  @mcp.tool()
  def get_course_info(course_code: str) -> str:
      ...
  
  if __name__ == "__main__":
      mcp.run() # stdio transport
  ```
- **Transport:** Standard input/output (`stdio`) for local process isolation and demo scripts.

---

## 4. Vector Stores & Deployment Backends

- **ChromaDB:** `chromadb>=0.4.22` (default local persistent vector database in `vectorstore/`).
- **FAISS:** `faiss-cpu>=1.7.4` (in-memory similarity search library ideal for AWS Lambda `/tmp` or packaging without native background servers).
- **AWS Serverless Wrapper:** `mangum>=0.17.0` wraps FastAPI for AWS Lambda + HTTP API Gateway.
