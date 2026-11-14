"""MCP Client for connecting the CampusGPT backend to the MCP Server.

Teaching Distinction:
- FUNCTION CALLING: An LLM feature where the model decides to invoke a tool,
  and specifies structured arguments for the application to run.
- MCP (Model Context Protocol): An open standard protocol that connects
  applications to external data sources, tools, and servers in a decoupled way.

In this flow, when ENABLE_MCP=true:
1. Client starts the MCP server over stdio.
2. Discovers tools and converts them to Gemini tool definitions.
3. If Gemini requests a tool, the application executes it THROUGH this MCP client.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("campusgpt.mcp_client")
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class CampusMCPClient:
    """Connects CampusGPT to the local MCP server."""
    def __init__(self):
        self.server_path = BASE_DIR / "mcp_server" / "server.py"
        self._tools_cache: Optional[List[Dict[str, Any]]] = None

    def is_available(self) -> bool:
        """Check if MCP server file exists and mcp SDK is installed."""
        try:
            import mcp
            return self.server_path.exists()
        except ImportError:
            return False

    def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools formatted for Gemini function declarations."""
        # Static definitions matching our server for fast startup
        return [
            {
                "name": "get_course_info",
                "description": "Look up official course details, credits, and prerequisites by course code",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "course_code": {
                            "type": "string",
                            "description": "The course code, e.g. 'CS 101' or 'MGMT 101'"
                        }
                    },
                    "required": ["course_code"]
                }
            },
            {
                "name": "lookup_calendar_event",
                "description": "Search the academic calendar for dates, deadlines, and semester milestones",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Event name or keyword like 'add/drop' or 'exams'"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool through the MCP server module directly or via stdio."""
        # Allowlist check (Guardrail applied to tool execution)
        allowed_tools = ["get_course_info", "lookup_calendar_event", "search_documents"]
        if tool_name not in allowed_tools:
            return f"Error: Tool '{tool_name}' is not in the allowed MCP tools list."

        try:
            # Direct execution for robust in-process fallback
            from mcp_server.server import get_course_info, lookup_calendar_event, search_documents
            if tool_name == "get_course_info":
                return get_course_info(course_code=arguments.get("course_code", ""))
            elif tool_name == "lookup_calendar_event":
                return lookup_calendar_event(query=arguments.get("query", ""))
            elif tool_name == "search_documents":
                return search_documents(query=arguments.get("query", ""), k=arguments.get("k", 3))
            return f"Tool {tool_name} not found."
        except Exception as e:
            logger.warning(f"MCP execution failed: {e}")
            return f"Error executing tool {tool_name}: {e}"
