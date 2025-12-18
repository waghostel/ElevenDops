"""Backend API client for Streamlit frontend.

This module provides the BackendAPIClient class for communicating
with the FastAPI backend without exposing API logic in the UI layer.
"""

import os
from datetime import datetime

import httpx

from streamlit_app.services.exceptions import (
    APIConnectionError,
    APIError,
    APITimeoutError,
)
from streamlit_app.services.models import DashboardStats

# Default configuration
DEFAULT_BACKEND_URL = "http://localhost:8000"
DEFAULT_TIMEOUT = 10.0  # seconds


class BackendAPIClient:
    """Client for communicating with the ElevenDops backend API.

    This client handles all HTTP communication with the FastAPI backend,
    including error handling and response parsing.

    Attributes:
        base_url: The base URL of the backend API.
        timeout: Request timeout in seconds.
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the backend API client.

        Args:
            base_url: Backend API base URL. If not provided, uses
                BACKEND_API_URL environment variable or localhost default.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url or os.getenv("BACKEND_API_URL", DEFAULT_BACKEND_URL)
        self.timeout = timeout

    def _get_client(self) -> httpx.AsyncClient:
        """Create an async HTTP client with configured settings.

        Returns:
            Configured httpx.AsyncClient instance.
        """
        return httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout),
        )

    async def health_check(self) -> dict:
        """Check the health of the backend API.

        Returns:
            Dict containing status, timestamp, and version.

        Raises:
            APIConnectionError: If connection to backend fails.
            APITimeoutError: If request times out.
            APIError: For other API errors.
        """
        try:
            async with self._get_client() as client:
                response = await client.get("/api/health")
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.TimeoutException as e:
            raise APITimeoutError(f"Health check timed out: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Health check failed: {e.response.text}",
                status_code=e.response.status_code,
            ) from e

    async def get_dashboard_stats(self) -> DashboardStats:
        """Get dashboard statistics from the backend.

        Returns:
            DashboardStats dataclass with current statistics.

        Raises:
            APIConnectionError: If connection to backend fails.
            APITimeoutError: If request times out.
            APIError: For other API errors.
        """
        try:
            async with self._get_client() as client:
                response = await client.get("/api/dashboard/stats")
                response.raise_for_status()
                data = response.json()
                return DashboardStats(
                    document_count=data["document_count"],
                    agent_count=data["agent_count"],
                    audio_count=data["audio_count"],
                    last_activity=datetime.fromisoformat(data["last_activity"]),
                )
        except httpx.ConnectError as e:
            raise APIConnectionError(
                f"Failed to connect to backend: {e}"
            ) from e
        except httpx.TimeoutException as e:
            raise APITimeoutError(
                f"Dashboard stats request timed out: {e}"
            ) from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Failed to get dashboard stats: {e.response.text}",
                status_code=e.response.status_code,
            ) from e
        except (KeyError, ValueError) as e:
            raise APIError(
                message=f"Invalid response format: {e}",
                status_code=None,
            ) from e


# Convenience function for getting a client instance
def get_backend_client() -> BackendAPIClient:
    """Get a configured backend API client.

    Returns:
        BackendAPIClient instance with default configuration.
    """
    return BackendAPIClient()
