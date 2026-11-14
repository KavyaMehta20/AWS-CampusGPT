"""Model Context Protocol (MCP) Server for CampusGPT.

Exposes tools via the official MCP Python SDK:
1. search_documents(query, k): Semantic search over the vector store.
2. get_course_info(course_code): Reads course catalog from data/<source>/courses.json.
3. lookup_calendar_event(query): Reads academic dates from calendar.json.
4. list_documents(): Resource listing available documents.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    FastMCP = None

# Locate data root
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def resolve_data_file(filename: str) -> Path:
    """Find file in data/raw or data/sample."""
    raw_file = DATA_DIR / "raw" / filename
    if raw_file.exists():
        return raw_file
    sample_file = DATA_DIR / "sample" / filename
    return sample_file


# Initialize FastMCP Server
mcp = FastMCP("campusgpt-mcp-server") if FastMCP else None


if mcp:
    @mcp.tool()
    def get_course_info(course_code: str) -> str:
        """Look up official course details, credits, and prerequisites by course code (e.g., 'CS 101', 'MGMT 101')."""
        courses_file = resolve_data_file("courses.json")
        if not courses_file.exists():
            return f"Course catalog data not found at {courses_file}."

        try:
            courses = json.loads(courses_file.read_text(encoding="utf-8"))
            clean_code = course_code.replace(" ", "").upper()
            for c in courses:
                c_code = c.get("course_code", "").replace(" ", "").upper()
                if clean_code in c_code or c_code in clean_code:
                    return json.dumps(c, indent=2)
            return f"No course found matching '{course_code}'."
        except Exception as e:
            return f"Error reading course data: {e}"


    @mcp.tool()
    def lookup_calendar_event(query: str) -> str:
        """Search the academic calendar for dates, deadlines, and semester milestones."""
        cal_file = resolve_data_file("calendar.json")
        if not cal_file.exists():
            return f"Calendar data not found at {cal_file}."

        try:
            events = json.loads(cal_file.read_text(encoding="utf-8"))
            q_lower = query.lower()
            matches = [e for e in events if q_lower in e.get("event", "").lower() or q_lower in e.get("notes", "").lower()]
            if matches:
                return json.dumps(matches, indent=2)
            return f"No calendar events found matching '{query}'."
        except Exception as e:
            return f"Error reading calendar data: {e}"


    @mcp.tool()
    def search_documents(query: str, k: int = 3) -> str:
        """Semantic search over indexed university documents."""
        try:
            # Import vector store directly
            sys.path.insert(0, str(BASE_DIR))
            from backend.app.retrieval import Retriever
            retriever = Retriever()
            results = retriever.retrieve(query=query, top_k=k)
            if not results:
                return "No matching documents found in vector store."
            return json.dumps([{
                "source": r.get("source"),
                "section": r.get("section") or r.get("page"),
                "snippet": r.get("text", "")[:200]
            } for r in results], indent=2)
        except Exception as e:
            return f"Error searching vector store: {e}"


    @mcp.resource("documents://catalog")
    def get_document_catalog() -> str:
        """List all available documents in the knowledge base."""
        docs = []
        for folder in ["raw", "sample"]:
            f_dir = DATA_DIR / folder
            if f_dir.exists():
                for f in f_dir.iterdir():
                    if f.is_file():
                        docs.append({"folder": folder, "filename": f.name})
        return json.dumps(docs, indent=2)


if __name__ == "__main__":
    if mcp is None:
        print("MCP SDK is not installed. Install with 'pip install mcp'.")
        sys.exit(1)
    # Run stdio transport
    mcp.run()
