# MCP Client Step (STEP MCP)

This directory connects the CampusGPT backend pipeline to the standalone `mcp_server`.

## Workshop Distinction:
- **Function Calling:** The LLM inspects a query, figures out it needs a tool, and returns a structured call request.
- **MCP (Model Context Protocol):** The standard open protocol allowing tools, servers, and agents to interact across systems.

When `ENABLE_MCP=true`, tools declared by the MCP server are passed to the Gemini model. When requested, CampusGPT executes them via `CampusMCPClient` and feeds results back to Gemini.
