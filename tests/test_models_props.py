"""Property tests for Pydantic model validation.

Property 3: Pydantic model validation
- Test that invalid input data raises ValidationError
Validates: Requirements 2.3
"""

from datetime import datetime

import pytest
from hypothesis import given, strategies as st
from pydantic import ValidationError

from backend.models.schemas import (
    DashboardStatsResponse,
    ErrorResponse,
    HealthResponse,
)


class TestHealthResponseValidation:
    """Property tests for HealthResponse model validation."""

    @given(
        status=st.text(min_size=1),
        version=st.text(min_size=1),
    )
    def test_valid_health_response_accepts_valid_data(
        self, status: str, version: str
    ) -> None:
        """Test that valid data creates a valid HealthResponse."""
        response = HealthResponse(
            status=status,
            timestamp=datetime.now(),
            version=version,
        )
        assert response.status == status
        assert response.version == version
        assert isinstance(response.timestamp, datetime)

    def test_health_response_rejects_missing_status(self) -> None:
        """Test that missing status raises ValidationError."""
        with pytest.raises(ValidationError):
            HealthResponse(
                timestamp=datetime.now(),
                version="0.1.0",
            )  # type: ignore

    def test_health_response_rejects_missing_timestamp(self) -> None:
        """Test that missing timestamp raises ValidationError."""
        with pytest.raises(ValidationError):
            HealthResponse(
                status="healthy",
                version="0.1.0",
            )  # type: ignore

    def test_health_response_rejects_missing_version(self) -> None:
        """Test that missing version raises ValidationError."""
        with pytest.raises(ValidationError):
            HealthResponse(
                status="healthy",
                timestamp=datetime.now(),
            )  # type: ignore

    def test_health_response_rejects_invalid_timestamp(self) -> None:
        """Test that invalid timestamp type raises ValidationError."""
        with pytest.raises(ValidationError):
            HealthResponse(
                status="healthy",
                timestamp="not-a-datetime",
                version="0.1.0",
            )


class TestDashboardStatsResponseValidation:
    """Property tests for DashboardStatsResponse model validation."""

    @given(
        document_count=st.integers(min_value=0, max_value=1000000),
        agent_count=st.integers(min_value=0, max_value=1000),
        audio_count=st.integers(min_value=0, max_value=1000000),
    )
    def test_valid_dashboard_stats_accepts_valid_data(
        self, document_count: int, agent_count: int, audio_count: int
    ) -> None:
        """Test that valid data creates a valid DashboardStatsResponse."""
        response = DashboardStatsResponse(
            document_count=document_count,
            agent_count=agent_count,
            audio_count=audio_count,
            last_activity=datetime.now(),
        )
        assert response.document_count == document_count
        assert response.agent_count == agent_count
        assert response.audio_count == audio_count

    def test_dashboard_stats_rejects_negative_counts(self) -> None:
        """Test that negative counts raise ValidationError."""
        with pytest.raises(ValidationError):
            DashboardStatsResponse(
                document_count=-1,
                agent_count=2,
                audio_count=10,
                last_activity=datetime.now(),
            )

    def test_dashboard_stats_rejects_missing_fields(self) -> None:
        """Test that missing fields raise ValidationError."""
        with pytest.raises(ValidationError):
            DashboardStatsResponse(
                document_count=5,
                agent_count=2,
                # missing audio_count and last_activity
            )  # type: ignore


class TestErrorResponseValidation:
    """Property tests for ErrorResponse model validation."""

    @given(
        detail=st.text(min_size=1),
        error_code=st.text(min_size=1),
    )
    def test_valid_error_response_accepts_valid_data(
        self, detail: str, error_code: str
    ) -> None:
        """Test that valid data creates a valid ErrorResponse."""
        response = ErrorResponse(detail=detail, error_code=error_code)
        assert response.detail == detail
        assert response.error_code == error_code

    def test_error_response_rejects_missing_detail(self) -> None:
        """Test that missing detail raises ValidationError."""
        with pytest.raises(ValidationError):
            ErrorResponse(error_code="ERR001")  # type: ignore

    def test_error_response_rejects_missing_error_code(self) -> None:
        """Test that missing error_code raises ValidationError."""
        with pytest.raises(ValidationError):
            ErrorResponse(detail="Something went wrong")  # type: ignore
