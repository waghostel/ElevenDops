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
from backend.api.routes.debug import router as debug_router
from backend.api.routes.templates import router as templates_router

from backend.config import get_settings
from backend.utils.logging import setup_application_logging, get_logger

# Initialize structured logging based on environment
settings = get_settings()
setup_application_logging(settings.app_env)
logger = get_logger(__name__)

# Application configuration
APP_TITLE = "ElevenDops Backend API"
APP_DESCRIPTION = "Backend API for ElevenDops intelligent medical assistant system"
APP_VERSION = "0.1.0"

# CORS configuration - managed by centralized config
CORS_ORIGINS = settings.get_cors_origins_list()

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


# Security Headers Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses.
    
    This middleware adds standard security headers to protect against:
    - Clickjacking (X-Frame-Options)
    - MIME type sniffing (X-Content-Type-Options)
    - Referrer leakage (Referrer-Policy)
    """

    async def dispatch(
        self, request: StarletteRequest, call_next
    ) -> Response:
        """Process request and add security headers to response."""
        response: Response = await call_next(request)
        
        # Prevent clickjacking by disallowing iframe embedding
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Control referrer information sent with requests
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response


app.add_middleware(SecurityHeadersMiddleware)

# Rate Limiting - protect against abuse and DoS attacks
from backend.middleware.rate_limit import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include API routers
app.include_router(health_router)
app.include_router(dashboard_router)
app.include_router(knowledge_router)
app.include_router(audio_router)
app.include_router(agent_router)
app.include_router(patient_router, prefix="/api/patient", tags=["patient"])
app.include_router(conversation_router, prefix="/api/conversations", tags=["conversations"])
# Only include debug router in non-production environments (security)
if not settings.is_production():
    app.include_router(debug_router)
else:
    logger.info("Debug router disabled in production environment")
app.include_router(templates_router)

# Mount static files for mock storage mode
if settings.use_mock_storage:
    from pathlib import Path
    from fastapi.staticfiles import StaticFiles
    
    mock_storage_dir = Path("temp_storage") / settings.gcs_bucket_name
    mock_storage_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/api/storage/files", StaticFiles(directory=str(mock_storage_dir)), name="mock_storage")


@app.get("/")
async def root():
    """Root endpoint."""
    logger.info("Root endpoint accessed")
    return {"message": APP_TITLE, "version": APP_VERSION}


from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected errors."""
    from backend.utils.errors import get_error_response, map_exception_to_status_code
    from backend.utils.logging import log_error_with_context
    
    # Determine status code and response content
    status_code = map_exception_to_status_code(exc)
    error_response = get_error_response(exc)

    # Log based on severity using structured logging
    if status_code >= 500:
        log_error_with_context(
            logger,
            f"Global exception: {exc}",
            exc,
            status_code=status_code,
            path=str(request.url.path),
            method=request.method,
        )
    else:
        logger.warning(
            f"Handled exception: {exc}",
            extra={
                "extra_fields": {
                    "status_code": status_code,
                    "path": str(request.url.path),
                    "method": request.method,
                    "error_type": type(exc).__name__,
                }
            }
        )

    return JSONResponse(
        status_code=status_code,
        content=error_response,
    )
