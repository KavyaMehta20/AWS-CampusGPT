"""FastAPI Application entry point.

Mounts:
- API routes (/chat, /health, /config)
- CORS middleware with configurable origins
- Serves static frontend files at root "/"
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import settings
from backend.app.api.routes import router as api_router

app = FastAPI(
    title=f"{settings.university_name} CampusGPT",
    description="Beginner-friendly RAG chatbot workshop project",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(api_router, prefix="/api")
# Also mount directly at root for convenience (/chat, /health, /config)
app.include_router(api_router)

# Mount frontend directory to serve UI at "/"
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
