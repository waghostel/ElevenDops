"""Property tests for debug API endpoints.

Property 5: Debug API Trace ID Return
- Debug endpoint execution returns valid trace ID
- Trace ID can be used to retrieve trace data
Validates: Requirements 3.3

Property 6: Input Validation Consistency
- Invalid inputs rejected with appropriate error messages
- Valid inputs processed successfully
Validates: Requirements 3.4
"""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.config import get_settings
from backend.main import app
from backend.services.langsmith_tracer import reset_tracer


@pytest.fixture
def client():
    """Create a test client."""
    reset_tracer()
    get_settings.cache_clear()
    with patch.dict(os.environ, {"USE_MOCK_DATA": "true", "LANGSMITH_TRACE_LEVEL": "info"}):
        get_settings.cache_clear()
        yield TestClient(app)


class TestDebugAPITraceIDReturn:
    """Property 5: Debug API Trace ID Return.
    
    Feature: langsmith-debug-integration
    Validates: Requirements 3.3
    
    For any debug endpoint execution, the response should contain a valid
    trace ID that can be used to retrieve trace data from LangSmith.
    """

    def test_script_generation_returns_trace_id(self, client) -> None:
        """Test that debug script generation returns a trace ID."""
        response = client.post(
            "/api/debug/script-generation",
            json={
                "knowledge_content": "Test medical content about diabetes",
                "prompt": "Generate a patient education script",
                "model_name": "gemini-2.0-flash",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "trace_id" in data
        assert data["trace_id"] is not None
        assert len(data["trace_id"]) > 0

    def test_trace_id_is_unique_per_execution(self, client) -> None:
        """Test that each execution returns a unique trace ID."""
        response1 = client.post(
            "/api/debug/script-generation",
            json={
                "knowledge_content": "Content 1",
                "prompt": "Prompt 1",
            }
        )
        response2 = client.post(
            "/api/debug/script-generation",
            json={
                "knowledge_content": "Content 2",
                "prompt": "Prompt 2",
            }
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        trace_id_1 = response1.json()["trace_id"]
        trace_id_2 = response2.json()["trace_id"]
        
        assert trace_id_1 != trace_id_2

    def test_response_includes_execution_status(self, client) -> None:
        """Test that response includes execution status."""
        response = client.post(
            "/api/debug/script-generation",
            json={
                "knowledge_content": "Test content",
                "prompt": "Test prompt",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "execution_status" in data
        assert data["execution_status"] in ("completed", "error", "running")

    def test_response_includes_steps(self, client) -> None:
        """Test that response includes workflow steps."""
        response = client.post(
            "/api/debug/script-generation",
            json={
                "knowledge_content": "Test content",
                "prompt": "Test prompt",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "steps" in data
        assert isinstance(data["steps"], list)
        assert len(data["steps"]) >= 1

    def test_steps_include_timing_info(self, client) -> None:
        """Test that steps include timing information."""
        response = client.post(
            "/api/debug/script-generation",
            json={
                "knowledge_content": "Test content",
                "prompt": "Test prompt",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for step in data["steps"]:
            assert "node_name" in step
            assert "duration_ms" in step

    def test_session_id_returned_when_session_name_provided(self, client) -> None:
        """Test that session ID is returned when session name is provided."""
        response = client.post(
            "/api/debug/script-generation",
            json={
                "knowledge_content": "Test content",
                "prompt": "Test prompt",
                "session_name": "test-session",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["session_id"] is not None


class TestInputValidationConsistency:
    """Property 6: Input Validation Consistency.
    
    Feature: langsmith-debug-integration
    Validates: Requirements 3.4
    
    For any debug API request, invalid inputs should be rejected with
    appropriate error messages, and valid inputs should be processed
    successfully.
    """

    def test_missing_knowledge_content_rejected(self, client) -> None:
        """Test that missing knowledge_content is rejected."""
        response = client.post(
            "/api/debug/script-generation",
            json={
                "prompt": "Test prompt",
            }
        )
        
        assert response.status_code == 422  # Validation error

    def test_missing_prompt_rejected(self, client) -> None:
        """Test that missing prompt is rejected."""
        response = client.post(
            "/api/debug/script-generation",
            json={
                "knowledge_content": "Test content",
            }
        )
        
        assert response.status_code == 422  # Validation error

    def test_empty_knowledge_content_rejected(self, client) -> None:
        """Test that empty knowledge_content is rejected."""
        response = client.post(
            "/api/debug/script-generation",
            json={
                "knowledge_content": "",
                "prompt": "Test prompt",
            }
        )
        
        assert response.status_code == 422  # Validation error

    def test_empty_prompt_rejected(self, client) -> None:
        """Test that empty prompt is rejected."""
        response = client.post(
            "/api/debug/script-generation",
            json={
                "knowledge_content": "Test content",
                "prompt": "",
            }
        )
        
        assert response.status_code == 422  # Validation error

    def test_invalid_debug_level_rejected(self, client) -> None:
        """Test that invalid debug level is rejected."""
        response = client.post(
            "/api/debug/script-generation",
            json={
                "knowledge_content": "Test content",
                "prompt": "Test prompt",
                "debug_level": "invalid",
            }
        )
        
        assert response.status_code == 422  # Validation error

    def test_valid_debug_levels_accepted(self, client) -> None:
        """Test that all valid debug levels are accepted."""
        for level in ["debug", "info", "error"]:
            response = client.post(
                "/api/debug/script-generation",
                json={
                    "knowledge_content": "Test content",
                    "prompt": "Test prompt",
                    "debug_level": level,
                }
            )
            
            assert response.status_code == 200, f"Level {level} should be accepted"

    def test_optional_model_name_uses_default(self, client) -> None:
        """Test that omitting model_name uses default value."""
        response = client.post(
            "/api/debug/script-generation",
            json={
                "knowledge_content": "Test content",
                "prompt": "Test prompt",
            }
        )
        
        assert response.status_code == 200


class TestSessionEndpoints:
    """Tests for session management endpoints."""

    def test_create_session(self, client) -> None:
        """Test creating a new session."""
        response = client.post(
            "/api/debug/sessions",
            json={"name": "test-session"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["name"] == "test-session"

    def test_list_sessions_empty(self, client) -> None:
        """Test listing sessions when none exist."""
        response = client.get("/api/debug/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "total_count" in data

    def test_list_sessions_after_creation(self, client) -> None:
        """Test listing sessions after creating some."""
        # Create sessions
        client.post("/api/debug/sessions", json={"name": "session-1"})
        client.post("/api/debug/sessions", json={"name": "session-2"})
        
        response = client.get("/api/debug/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] >= 2

    def test_get_session_not_found(self, client) -> None:
        """Test getting a non-existent session."""
        response = client.get("/api/debug/sessions/nonexistent-id")
        
        assert response.status_code == 404

    def test_get_session_after_creation(self, client) -> None:
        """Test getting a session after creation."""
        create_response = client.post(
            "/api/debug/sessions",
            json={"name": "my-session"}
        )
        session_id = create_response.json()["session_id"]
        
        response = client.get(f"/api/debug/sessions/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "my-session"

    def test_end_session(self, client) -> None:
        """Test ending a session."""
        # Create session
        create_response = client.post(
            "/api/debug/sessions",
            json={"name": "ending-session"}
        )
        session_id = create_response.json()["session_id"]
        
        # End session
        response = client.post(f"/api/debug/sessions/{session_id}/end")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"


class TestDebugHealth:
    """Tests for debug health endpoint."""

    def test_health_endpoint_returns_status(self, client) -> None:
        """Test that health endpoint returns status."""
        response = client.get("/api/debug/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "langsmith_configured" in data
        assert "project" in data
        assert "trace_level" in data
