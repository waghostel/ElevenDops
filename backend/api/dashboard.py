"""Dashboard API endpoints."""

from fastapi import APIRouter, Depends

from backend.models.schemas import DashboardStatsResponse
from backend.services.data_service import MockDataService, get_data_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    data_service: MockDataService = Depends(get_data_service),
) -> DashboardStatsResponse:
    """Get dashboard statistics.

    Returns aggregated statistics for the doctor dashboard including
    document count, agent count, audio count, and last activity time.

    Args:
        data_service: Injected data service instance.

    Returns:
        DashboardStatsResponse with current statistics.
    """
    return await data_service.get_dashboard_stats()
