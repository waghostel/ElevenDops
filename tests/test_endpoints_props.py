"""Property tests for API endpoints.

Property 1: Health endpoint response structure
- Test response always contains status, timestamp, version with correct types
Validates: Requirements 2.1

Property 2: Dashboard stats response completeness
- Test response contains all required fields with correct types
Validates: Requirements 2.2
"""

from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

import pytest
from fastapi.testclient import TestClient
from hypothesis import given, settings, strategies as st

from backend.main import app
from backend.services.data_service import get_data_service
from backend.services.firestore_service import get_firestore_service
from backend.services.storage_service import get_storage_service
from backend.models.schemas import DashboardStatsResponse

# Mock Data Service
mock_data_service = AsyncMock()
mock_data_service.get_dashboard_stats.return_value = DashboardStatsResponse(
    document_count=10,
    agent_count=5,
    audio_count=20,
    last_activity=datetime.now()
)

# Mock Firestore Service (for health check)
mock_firestore_service = MagicMock()
mock_firestore_service.health_check.return_value = True

# Mock Storage Service (for health check)
mock_storage_service = MagicMock()
mock_storage_service.health_check.return_value = True

# Override dependency
app.dependency_overrides[get_data_service] = lambda: mock_data_service
# Health endpoint uses direct imports or get methods, not Depends()?
# Checking backend/api/health.py...
# It imports: from backend.services.firestore_service import get_firestore_service
# It calls: firestore_service = get_firestore_service()
# It does NOT use Depends(). 
# So app.dependency_overrides WON'T work for health check unless health check uses Depends.

# Since health_check() does NOT use Depends(), we must patch the imports.
# We can use unittest.mock.patch.
# But TestClient(app) is global. We need to patch before importing/using client?
# Or we can patch inside the test methods?
# Since health_check is an async def, but TestClient calls it sync?
# Wait, TestClient wraps FastAPI app.
# If I patch "backend.api.health.get_firestore_service", it should work.

# Let's adjust the structure to use patch.

from unittest.mock import patch

# We can keep data service override as dashboard likely uses Depends (checking...)
# backend/api/dashboard.py likely uses Depends(get_data_service).

@pytest.fixture(autouse=True)
def mock_health_dependencies():
    with patch("backend.api.health.get_firestore_service") as mock_fs, \
         patch("backend.api.health.get_storage_service") as mock_storage:
        
        mock_fs_instance = MagicMock()
        mock_fs_instance.health_check.return_value = True
        mock_fs.return_value = mock_fs_instance
        
        mock_storage_instance = MagicMock()
        mock_storage_instance.health_check.return_value = True
        mock_storage.return_value = mock_storage_instance
        
        yield

client = TestClient(app)


class TestHealthEndpointProperties:
    """Property tests for health endpoint response structure."""

    def test_health_endpoint_returns_status_field(self) -> None:
        """Test that health endpoint response contains status field."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert isinstance(data["status"], str)
        assert data["status"] == "healthy"

    def test_health_endpoint_returns_timestamp_field(self) -> None:
        """Test that health endpoint response contains valid timestamp."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        # Verify timestamp is parseable
        timestamp = datetime.fromisoformat(data["timestamp"])
        assert isinstance(timestamp, datetime)

    def test_health_endpoint_returns_version_field(self) -> None:
        """Test that health endpoint response contains version field."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0

    @settings(max_examples=10)
    @given(st.just(None))
    def test_health_endpoint_response_structure_consistent(self, _: None) -> None:
        """Property: Health endpoint always returns consistent structure."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()

        # All required fields present
        required_fields = {"status", "timestamp", "version"}
        assert required_fields.issubset(data.keys())

        # Types are correct
        assert isinstance(data["status"], str)
        assert isinstance(data["version"], str)
        # Timestamp should be ISO format string
        datetime.fromisoformat(data["timestamp"])


class TestDashboardStatsEndpointProperties:
    """Property tests for dashboard stats endpoint response completeness."""

    def test_dashboard_stats_returns_document_count(self) -> None:
        """Test that dashboard stats contains document_count field."""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert "document_count" in data
        assert isinstance(data["document_count"], int)
        assert data["document_count"] >= 0

    def test_dashboard_stats_returns_agent_count(self) -> None:
        """Test that dashboard stats contains agent_count field."""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert "agent_count" in data
        assert isinstance(data["agent_count"], int)
        assert data["agent_count"] >= 0

    def test_dashboard_stats_returns_audio_count(self) -> None:
        """Test that dashboard stats contains audio_count field."""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert "audio_count" in data
        assert isinstance(data["audio_count"], int)
        assert data["audio_count"] >= 0

    def test_dashboard_stats_returns_last_activity(self) -> None:
        """Test that dashboard stats contains valid last_activity timestamp."""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert "last_activity" in data
        # Verify timestamp is parseable
        timestamp = datetime.fromisoformat(data["last_activity"])
        assert isinstance(timestamp, datetime)

    @settings(max_examples=10)
    @given(st.just(None))
    def test_dashboard_stats_response_structure_consistent(self, _: None) -> None:
        """Property: Dashboard stats always returns complete structure."""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()

        # All required fields present
        required_fields = {"document_count", "agent_count", "audio_count", "last_activity"}
        assert required_fields.issubset(data.keys())

        # Types are correct
        assert isinstance(data["document_count"], int)
        assert isinstance(data["agent_count"], int)
        assert isinstance(data["audio_count"], int)
        # Timestamp should be ISO format string
        datetime.fromisoformat(data["last_activity"])

        # Non-negative values
        assert data["document_count"] >= 0
        assert data["agent_count"] >= 0
        assert data["audio_count"] >= 0
