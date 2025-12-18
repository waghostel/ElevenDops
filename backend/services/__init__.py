"""Service layer for ElevenDops backend."""

from backend.services.data_service import (
    DataServiceProtocol,
    MockDataService,
    get_data_service,
)

__all__ = ["DataServiceProtocol", "MockDataService", "get_data_service"]
