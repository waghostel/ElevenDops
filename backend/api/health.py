"""Health check API endpoints."""

from datetime import datetime

from fastapi import APIRouter

from backend.models.schemas import HealthResponse

router = APIRouter(prefix="/api", tags=["health"])

# API version - should match pyproject.toml
API_VERSION = "0.1.0"


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns the current health status of the API service.

    Returns:
        HealthResponse with status, timestamp, and version.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=API_VERSION,
    )
