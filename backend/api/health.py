from datetime import datetime
from fastapi import APIRouter
from backend.services.firestore_service import get_firestore_service
from backend.services.storage_service import get_storage_service
from backend.config import get_settings

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check():
    """Comprehensive health check for all services."""
    settings = get_settings()
    
    # Check Firestore
    firestore_healthy = False
    firestore_error = None
    try:
        firestore_service = get_firestore_service()
        firestore_healthy = firestore_service.health_check()
    except Exception as e:
        firestore_error = str(e)
    
    # Check Storage
    storage_healthy = False
    storage_error = None
    try:
        storage_service = get_storage_service()
        storage_healthy = storage_service.health_check()
    except Exception as e:
        storage_error = str(e)
    
    # Overall status
    # We consider it healthy if we can talk to the services that are configured
    all_healthy = firestore_healthy and storage_healthy
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0",
        "services": {
            "firestore": {
                "status": "healthy" if firestore_healthy else "unhealthy",
                "emulator": settings.use_firestore_emulator,
                "error": firestore_error
            },
            "storage": {
                "status": "healthy" if storage_healthy else "unhealthy",
                "emulator": settings.use_gcs_emulator,
                "error": storage_error
            }
        },
        "config": {
            "project": settings.google_cloud_project,
            "debug": settings.debug
        }
    }


@router.get("/health/ready")
async def readiness_check():
    """Simple readiness check for container orchestration."""
    return {"status": "ready"}
