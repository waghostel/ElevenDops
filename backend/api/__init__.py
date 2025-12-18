"""API routers for ElevenDops backend."""

from backend.api.dashboard import router as dashboard_router
from backend.api.health import router as health_router

__all__ = ["health_router", "dashboard_router"]
