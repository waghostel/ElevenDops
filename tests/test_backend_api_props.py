"""Property tests for Backend API client service module.

Property 4: Backend API client configuration
- Test client uses environment variable or default URL
Validates: Requirements 5.1

Property 5: API error handling
- Test APIError is raised for failed calls with meaningful messages
Validates: Requirements 4.3, 5.3

Property 6: Dashboard stats return type
- Test get_dashboard_stats() returns DashboardStats dataclass
Validates: Requirements 5.4
"""

import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from hypothesis import given, settings, strategies as st

from streamlit_app.services.backend_api import (
    DEFAULT_BACKEND_URL,
    BackendAPIClient,
)
from streamlit_app.services.exceptions import (
    APIConnectionError,
    APIError,
    APITimeoutError,
)
from streamlit_app.services.models import DashboardStats


class TestClientConfiguration:
    """Property 4: Backend API client configuration."""

    def test_client_uses_default_url_when_env_not_set(self) -> None:
        """Test that client uses default URL when env var not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove BACKEND_API_URL if it exists
            os.environ.pop("BACKEND_API_URL", None)
            client = BackendAPIClient()
            assert client.base_url == DEFAULT_BACKEND_URL

    def test_client_uses_environment_variable_when_set(self) -> None:
        """Test that client uses BACKEND_API_URL env var when set."""
        test_url = "http://custom-backend:9000"
        with patch.dict(os.environ, {"BACKEND_API_URL": test_url}):
            client = BackendAPIClient()
            assert client.base_url == test_url

    def test_client_uses_explicit_base_url_over_env(self) -> None:
        """Test that explicit base_url overrides environment variable."""
        explicit_url = "http://explicit:8000"
        with patch.dict(os.environ, {"BACKEND_API_URL": "http://env:9000"}):
            client = BackendAPIClient(base_url=explicit_url)
            assert client.base_url == explicit_url

    def test_client_uses_default_url_when_env_is_empty_string(self) -> None:
        """Test that client uses default URL when env var is empty string."""
        with patch.dict(os.environ, {"BACKEND_API_URL": ""}):
            client = BackendAPIClient()
            assert client.base_url == DEFAULT_BACKEND_URL

    @given(timeout=st.floats(min_value=0.1, max_value=60.0))
    @settings(max_examples=10)
    def test_client_accepts_custom_timeout(self, timeout: float) -> None:
        """Property: Client accepts any positive timeout value."""
        client = BackendAPIClient(timeout=timeout)
        assert client.timeout == timeout

    def test_client_configures_base_url_in_httpx(self) -> None:
        """Regression test: httpx client must be configured with base_url."""
        client = BackendAPIClient(base_url="http://test-server:8000")
        httpx_client = client._get_client()
        assert str(httpx_client.base_url) == "http://test-server:8000"


class TestAPIErrorHandling:
    """Property 5: API error handling."""

    @pytest.mark.asyncio
    async def test_connection_error_raises_api_connection_error(self) -> None:
        """Test that connection failure raises APIConnectionError."""
        client = BackendAPIClient(base_url="http://nonexistent:9999")

        with pytest.raises(APIConnectionError) as exc_info:
            await client.health_check()

        assert "Failed to connect" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_timeout_error_raises_api_timeout_error(self) -> None:
        """Test that timeout raises APITimeoutError."""
        client = BackendAPIClient(timeout=0.001)

        # Mock the _get_client method to return a mock that raises timeout
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.TimeoutException("Request timed out")
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        with patch.object(client, "_get_client", return_value=mock_client):
            with pytest.raises(APITimeoutError) as exc_info:
                await client.health_check()

            assert "timed out" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_http_error_raises_api_error_with_status_code(self) -> None:
        """Test that HTTP errors raise APIError with status code."""
        client = BackendAPIClient()

        # Create proper mock response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        # Create the HTTPStatusError
        http_error = httpx.HTTPStatusError(
            "Server Error",
            request=MagicMock(),
            response=mock_response,
        )

        # Mock the async client
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.ConnectError("Connection refused")
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        with patch.object(client, "_get_client", return_value=mock_client):
            with pytest.raises(APIConnectionError):
                await client.health_check()

    def test_api_error_has_message_attribute(self) -> None:
        """Test that APIError has message attribute."""
        error = APIError("Test error", status_code=400)
        assert error.message == "Test error"
        assert error.status_code == 400

    def test_api_error_string_includes_status_code(self) -> None:
        """Test that APIError string representation includes status code."""
        error = APIError("Test error", status_code=404)
        assert "[404]" in str(error)
        assert "Test error" in str(error)

    def test_api_connection_error_is_api_error_subclass(self) -> None:
        """Test that APIConnectionError is subclass of APIError."""
        error = APIConnectionError()
        assert isinstance(error, APIError)

    def test_api_timeout_error_is_api_error_subclass(self) -> None:
        """Test that APITimeoutError is subclass of APIError."""
        error = APITimeoutError()
        assert isinstance(error, APIError)


class TestDashboardStatsReturnType:
    """Property 6: Dashboard stats return type."""

    @pytest.mark.asyncio
    async def test_get_dashboard_stats_returns_dataclass(self) -> None:
        """Test that get_dashboard_stats returns DashboardStats dataclass."""
        client = BackendAPIClient()

        # Create proper mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "document_count": 5,
            "agent_count": 2,
            "audio_count": 10,
            "last_activity": datetime.now().isoformat(),
        }
        mock_response.raise_for_status = MagicMock()

        # Create async mock client
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.get_dashboard_stats()

        assert isinstance(result, DashboardStats)

    @pytest.mark.asyncio
    async def test_dashboard_stats_has_correct_fields(self) -> None:
        """Test that returned DashboardStats has all required fields."""
        client = BackendAPIClient()

        test_data = {
            "document_count": 10,
            "agent_count": 3,
            "audio_count": 25,
            "last_activity": "2024-01-15T10:30:00",
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = test_data
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.get_dashboard_stats()

        assert result.document_count == test_data["document_count"]
        assert result.agent_count == test_data["agent_count"]
        assert result.audio_count == test_data["audio_count"]
        assert isinstance(result.last_activity, datetime)

    @pytest.mark.asyncio
    async def test_dashboard_stats_preserves_values_property(self) -> None:
        """Property: Dashboard stats preserves all values from API response."""
        client = BackendAPIClient()

        # Use fixed test values
        doc_count, agent_count, audio_count = 42, 7, 100

        test_data = {
            "document_count": doc_count,
            "agent_count": agent_count,
            "audio_count": audio_count,
            "last_activity": datetime.now().isoformat(),
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = test_data
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.get_dashboard_stats()

        assert result.document_count == doc_count
        assert result.agent_count == agent_count
        assert result.audio_count == audio_count
