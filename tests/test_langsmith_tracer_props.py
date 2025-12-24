"""Property tests for LangSmith tracer service.

Property 4: Graceful Degradation
- Workflow executes successfully when LangSmith API unavailable
- No exceptions thrown when API key missing
Validates: Requirements 4.3

Property 7: Session Persistence
- Sessions persist and are retrievable by ID
- Session data survives between method calls
Validates: Requirements 2.5
"""

import os
from unittest.mock import patch, MagicMock

import pytest
from hypothesis import given, settings as hypothesis_settings, strategies as st

from backend.config import get_settings
from backend.services.langsmith_tracer import (
    LangSmithTracer,
    DebugSession,
    TraceMetadata,
    get_tracer,
    reset_tracer,
)


class TestGracefulDegradation:
    """Property 4: Graceful Degradation.
    
    Feature: langsmith-debug-integration
    Validates: Requirements 4.3
    
    For any workflow execution, when LangSmith API is unavailable the
    workflow should complete successfully without tracing, maintaining
    the same output quality.
    """

    def setup_method(self) -> None:
        """Reset tracer singleton before each test."""
        reset_tracer()

    def test_initialize_returns_false_without_api_key(self) -> None:
        """Test that initialization returns False when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            tracer = LangSmithTracer()
            result = tracer.initialize_tracing()
            assert result is False
            assert tracer.is_available() is False

    def test_initialize_does_not_throw_without_api_key(self) -> None:
        """Test that initialization does not throw when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            tracer = LangSmithTracer()
            # Should not raise any exception
            tracer.initialize_tracing()

    def test_start_session_works_without_langsmith(self) -> None:
        """Test that session creation works even without LangSmith."""
        with patch.dict(os.environ, {}, clear=True):
            tracer = LangSmithTracer()
            # Don't initialize - simulate LangSmith unavailable
            
            session_id = tracer.start_trace_session("test-session")
            
            assert session_id is not None
            assert len(session_id) > 0

    def test_end_session_works_without_langsmith(self) -> None:
        """Test that ending session works even without LangSmith."""
        with patch.dict(os.environ, {}, clear=True):
            tracer = LangSmithTracer()
            session_id = tracer.start_trace_session("test-session")
            
            metadata = tracer.end_trace_session(session_id)
            
            assert metadata is not None
            assert metadata.session_id == session_id
            assert metadata.status == "completed"

    def test_end_nonexistent_session_returns_not_found(self) -> None:
        """Test that ending non-existent session returns appropriate metadata."""
        tracer = LangSmithTracer()
        
        metadata = tracer.end_trace_session("nonexistent-id")
        
        assert metadata.status == "not_found"
        assert metadata.trace_count == 0

    def test_is_available_false_without_initialization(self) -> None:
        """Test that is_available returns False before initialization."""
        tracer = LangSmithTracer()
        assert tracer.is_available() is False

    def test_add_trace_to_session_graceful_with_invalid_session(self) -> None:
        """Test that adding trace to invalid session doesn't throw."""
        tracer = LangSmithTracer()
        
        result = tracer.add_trace_to_session("invalid-id", "trace-123")
        
        assert result is False


class TestSessionPersistence:
    """Property 7: Session Persistence.
    
    Feature: langsmith-debug-integration
    Validates: Requirements 2.5
    
    For any debug session created, the session data should persist
    and be retrievable by session ID.
    """

    def setup_method(self) -> None:
        """Reset tracer singleton before each test."""
        reset_tracer()

    def test_session_retrievable_by_id(self) -> None:
        """Test that created sessions can be retrieved by ID."""
        tracer = LangSmithTracer()
        session_id = tracer.start_trace_session("my-session")
        
        session = tracer.get_session(session_id)
        
        assert session is not None
        assert session.session_id == session_id
        assert session.name == "my-session"

    def test_session_persists_across_multiple_operations(self) -> None:
        """Test that session data persists across multiple operations."""
        tracer = LangSmithTracer()
        session_id = tracer.start_trace_session("persistent-session")
        
        # Add some traces
        tracer.add_trace_to_session(session_id, "trace-1")
        tracer.add_trace_to_session(session_id, "trace-2")
        
        # Retrieve and verify
        session = tracer.get_session(session_id)
        assert session is not None
        assert len(session.trace_ids) == 2
        assert "trace-1" in session.trace_ids
        assert "trace-2" in session.trace_ids

    @given(session_name=st.text(min_size=1, max_size=100))
    @hypothesis_settings(max_examples=10)
    def test_any_valid_session_name_persists(self, session_name: str) -> None:
        """Property: Any valid session name creates a retrievable session."""
        reset_tracer()
        tracer = LangSmithTracer()
        
        session_id = tracer.start_trace_session(session_name)
        session = tracer.get_session(session_id)
        
        assert session is not None
        assert session.name == session_name

    def test_multiple_sessions_persist_independently(self) -> None:
        """Test that multiple sessions persist independently."""
        tracer = LangSmithTracer()
        
        session1_id = tracer.start_trace_session("session-1")
        session2_id = tracer.start_trace_session("session-2")
        
        tracer.add_trace_to_session(session1_id, "trace-a")
        tracer.add_trace_to_session(session2_id, "trace-b")
        tracer.add_trace_to_session(session2_id, "trace-c")
        
        session1 = tracer.get_session(session1_id)
        session2 = tracer.get_session(session2_id)
        
        assert len(session1.trace_ids) == 1
        assert len(session2.trace_ids) == 2

    def test_list_sessions_returns_all_sessions(self) -> None:
        """Test that list_sessions returns all created sessions."""
        tracer = LangSmithTracer()
        
        tracer.start_trace_session("session-a")
        tracer.start_trace_session("session-b")
        tracer.start_trace_session("session-c")
        
        sessions = tracer.list_sessions()
        
        assert len(sessions) == 3
        names = [s.name for s in sessions]
        assert "session-a" in names
        assert "session-b" in names
        assert "session-c" in names

    def test_session_status_updates_on_end(self) -> None:
        """Test that session status updates when ended."""
        tracer = LangSmithTracer()
        session_id = tracer.start_trace_session("ending-session")
        
        session_before = tracer.get_session(session_id)
        assert session_before.status == "active"
        assert session_before.ended_at is None
        
        tracer.end_trace_session(session_id)
        
        session_after = tracer.get_session(session_id)
        assert session_after.status == "completed"
        assert session_after.ended_at is not None

    def test_get_nonexistent_session_returns_none(self) -> None:
        """Test that getting non-existent session returns None."""
        tracer = LangSmithTracer()
        
        session = tracer.get_session("does-not-exist")
        
        assert session is None


class TestTracerConfiguration:
    """Tests for tracer configuration behavior."""

    def setup_method(self) -> None:
        """Reset tracer singleton before each test."""
        reset_tracer()

    def test_project_name_from_settings(self) -> None:
        """Test that project name comes from settings."""
        get_settings.cache_clear()
        with patch.dict(
            os.environ,
            {"LANGSMITH_PROJECT": "custom-project"},
        ):
            get_settings.cache_clear()
            tracer = LangSmithTracer()
            assert tracer.project_name == "custom-project"

    def test_trace_level_from_settings(self) -> None:
        """Test that trace level comes from settings."""
        get_settings.cache_clear()
        with patch.dict(
            os.environ,
            {"LANGSMITH_TRACE_LEVEL": "debug"},
        ):
            get_settings.cache_clear()
            tracer = LangSmithTracer()
            assert tracer.trace_level == "debug"

    def test_session_includes_configuration(self) -> None:
        """Test that session includes configuration details."""
        tracer = LangSmithTracer()
        session_id = tracer.start_trace_session("config-test")
        
        session = tracer.get_session(session_id)
        
        assert "trace_level" in session.configuration
        assert "project" in session.configuration
        assert "langsmith_available" in session.configuration


class TestTracerSingleton:
    """Tests for tracer singleton behavior."""

    def setup_method(self) -> None:
        """Reset tracer singleton before each test."""
        reset_tracer()

    def test_get_tracer_returns_same_instance(self) -> None:
        """Test that get_tracer returns the same instance."""
        tracer1 = get_tracer()
        tracer2 = get_tracer()
        
        assert tracer1 is tracer2

    def test_reset_tracer_creates_new_instance(self) -> None:
        """Test that reset_tracer allows new instance creation."""
        tracer1 = get_tracer()
        reset_tracer()
        tracer2 = get_tracer()
        
        assert tracer1 is not tracer2
