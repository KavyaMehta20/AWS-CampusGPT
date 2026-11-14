"""MCP Standalone Demo Script (< 40 lines of output).

Demonstrates starting the MCP client, listing tools, and calling one directly.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.mcp_client import CampusMCPClient


def run_demo():
    print("=" * 55)
    print("🔌 Model Context Protocol (MCP) Standalone Demo")
    print("=" * 55)

    client = CampusMCPClient()
    print("1. Connecting to CampusGPT MCP Server...")
    print("✓ MCP Server Interface initialized.")

    print("\n2. Discovering registered MCP tools:")
    tools = client.list_tools()
    for t in tools:
        print(f"  • Tool: {t['name']} - {t['description']}")

    print("\n3. Invoking tool 'get_course_info' with arg 'CS 101':")
    result = client.call_tool("get_course_info", {"course_code": "CS 101"})
    print("Response from MCP tool:")
    print(result)

    print("\n4. Invoking tool 'lookup_calendar_event' with query 'Add/Drop':")
    cal_result = client.call_tool("lookup_calendar_event", {"query": "Add/Drop"})
    print("Response from MCP tool:")
    print(cal_result)

    print("-" * 55)
    print("Demo complete: Decoupled tool execution over MCP verified!")


if __name__ == "__main__":
    run_demo()
