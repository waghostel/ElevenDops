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

from backend.config import get_settings

# Application configuration
APP_TITLE = "ElevenDops Backend API"
APP_DESCRIPTION = "Backend API for ElevenDops intelligent medical assistant system"
APP_VERSION = "0.1.0"

# CORS configuration - managed by centralized config
CORS_ORIGINS = get_settings().get_cors_origins_list()

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


from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected errors."""
    import logging
    logging.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please contact support.", "error_code": "INTERNAL_SERVER_ERROR"},
    )
