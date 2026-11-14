# CampusGPT MCP Server

This is an independent Model Context Protocol (MCP) server providing standard tools and resources over `stdio`.

## Exposed Tools
1. `get_course_info(course_code)`: Retrieves course details from `courses.json`.
2. `lookup_calendar_event(query)`: Queries academic deadlines from `calendar.json`.
3. `search_documents(query, k)`: Runs semantic vector search on the knowledge base.

## Standalone Execution
You can run this server on its own or inspect it via the MCP demo script:
```bash
python scripts/mcp_demo.py
```
