"""FastAPI application entry point for ElevenDops backend."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.dashboard import router as dashboard_router
from backend.api.health import router as health_router
from backend.api.routes.knowledge import router as knowledge_router
from backend.api.routes.audio import router as audio_router
from backend.api.routes.agent import router as agent_router
from backend.api.routes.patient import router as patient_router
from backend.api.routes.conversation import router as conversation_router

# Application configuration
APP_TITLE = "ElevenDops Backend API"
APP_DESCRIPTION = "Backend API for ElevenDops intelligent medical assistant system"
APP_VERSION = "0.1.0"

# CORS configuration - configurable via environment
DEFAULT_ORIGINS = ["http://localhost:8501", "http://127.0.0.1:8501"]
CORS_ORIGINS = os.getenv("CORS_ORIGINS", ",".join(DEFAULT_ORIGINS)).split(",")

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health_router)
app.include_router(dashboard_router)
app.include_router(knowledge_router)
app.include_router(audio_router)
app.include_router(agent_router)
app.include_router(patient_router, prefix="/api/patient", tags=["patient"])
app.include_router(conversation_router, prefix="/api/conversations", tags=["conversations"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": APP_TITLE, "version": APP_VERSION}
