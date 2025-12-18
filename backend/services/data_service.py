"""Data service layer for ElevenDops backend.

This module provides a mock data service that can be easily replaced
with a Firestore client for production use.
"""

from datetime import datetime
from typing import Protocol

from backend.models.schemas import DashboardStatsResponse


class DataServiceProtocol(Protocol):
    """Protocol defining the data service interface."""

    async def get_dashboard_stats(self) -> DashboardStatsResponse:
        """Get dashboard statistics."""
        ...


class MockDataService:
    """Mock data service for development and testing.

    This service returns mock data and can be replaced with
    FirestoreDataService for production use.
    """

    async def get_dashboard_stats(self) -> DashboardStatsResponse:
        """Get mock dashboard statistics.

        Returns:
            DashboardStatsResponse with mock data:
            - document_count: 5
            - agent_count: 2
            - audio_count: 10
            - last_activity: current timestamp
        """
        return DashboardStatsResponse(
            document_count=5,
            agent_count=2,
            audio_count=10,
            last_activity=datetime.now(),
        )


# Default data service instance for dependency injection
def get_data_service() -> MockDataService:
    """Get the data service instance.

    This function serves as a dependency injection point.
    Replace with FirestoreDataService for production.
    """
    return MockDataService()
