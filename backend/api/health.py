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
    
    if settings.use_mock_data:
        firestore_healthy = True
        firestore_status = "healthy (mock)"
        firestore_error = None
    else:
        try:
            firestore_service = get_firestore_service()
            firestore_healthy = firestore_service.health_check()
            firestore_status = "healthy" if firestore_healthy else "unhealthy"
        except Exception as e:
            firestore_status = "unhealthy"
            firestore_error = str(e)
    
    # Check Storage
    storage_healthy = False
    storage_error = None
    
    try:
        storage_service = get_storage_service()
        storage_healthy = storage_service.health_check()
        if settings.use_mock_storage:
             storage_status = "healthy (mock)" if storage_healthy else "unhealthy"
        else:
             storage_status = "healthy" if storage_healthy else "unhealthy"
    except Exception as e:
        storage_status = "unhealthy"
        storage_error = str(e)
    
    # Overall status
    all_healthy = firestore_healthy and storage_healthy
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.1-MOCK-fix",
        "services": {
            "firestore": {
                "status": firestore_status,
                "emulator": settings.use_firestore_emulator,
                "mock": settings.use_mock_data,
                "error": firestore_error
            },
            "storage": {
                "status": storage_status,
                "emulator": settings.use_gcs_emulator,
                "mock": settings.use_mock_storage,
                "error": storage_error
            }
        },
        "config": {
            "project": settings.google_cloud_project,
            "debug": settings.debug,
            "use_mock_data": settings.use_mock_data,
            "use_mock_storage": settings.use_mock_storage
        }
    }


@router.get("/health/ready")
async def readiness_check():
    """Simple readiness check for container orchestration."""
    return {"status": "ready"}
