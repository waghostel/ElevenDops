"""LangSmith tracer service for debugging LangGraph workflows.

This module provides tracing and debugging capabilities for LangGraph
workflows using LangSmith. It supports graceful degradation when
LangSmith is unavailable.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field

from backend.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class TraceMetadata:
    """Metadata returned when a trace session ends."""
    session_id: str
    session_name: str
    start_time: datetime
    end_time: datetime
    trace_count: int
    status: str
    langsmith_url: Optional[str] = None


@dataclass
class DebugSession:
    """Represents a debug tracing session."""
    session_id: str
    name: str
    created_at: datetime
    trace_ids: list[str] = field(default_factory=list)
    status: str = "active"
    configuration: dict = field(default_factory=dict)
    ended_at: Optional[datetime] = None


class LangSmithTracer:
    """Manages LangSmith tracing integration for LangGraph workflows.
    
    Provides graceful degradation when LangSmith is unavailable - all methods
    return appropriate no-op values without throwing exceptions.
    
    Example:
        tracer = LangSmithTracer()
        if tracer.initialize_tracing():
            session_id = tracer.start_trace_session("debug-run-1")
            # ... run workflow ...
            metadata = tracer.end_trace_session(session_id)
    """
    
    def __init__(self) -> None:
        """Initialize the tracer with configuration from settings."""
        self._settings = get_settings()
        self._client: Optional[object] = None
        self._initialized = False
        self._sessions: dict[str, DebugSession] = {}
    
    @property
    def project_name(self) -> str:
        """Get the LangSmith project name."""
        return self._settings.langsmith_project
    
    @property
    def trace_level(self) -> str:
        """Get the configured trace level."""
        return self._settings.langsmith_trace_level
    
    def initialize_tracing(self) -> bool:
        """Initialize LangSmith tracing.
        
        Validates the API key and establishes connection to LangSmith.
        Returns True if initialization succeeds, False otherwise.
        
        This method implements graceful degradation - it will not throw
        exceptions if LangSmith is unavailable.
        
        Returns:
            bool: True if LangSmith is configured and reachable, False otherwise.
        """
        if not self._settings.is_langsmith_configured():
            logger.info("LangSmith not configured - tracing disabled")
            return False
        
        try:
            # Configure environment variables for langsmith
            self._settings.configure_langsmith_environment()
            
            # Try to import and create the LangSmith client
            from langsmith import Client
            self._client = Client()
            
            # Verify connection by checking if we can access the API
            # The list_projects call will fail if API key is invalid
            try:
                # Limit to 1 to minimize API overhead
                list(self._client.list_projects(limit=1))
                self._initialized = True
                logger.info(
                    f"LangSmith tracing initialized for project: {self.project_name}"
                )
                return True
            except Exception as e:
                logger.warning(f"LangSmith API connection failed: {e}")
                self._client = None
                return False
                
        except ImportError:
            logger.warning("langsmith package not available")
            return False
        except Exception as e:
            logger.warning(f"Failed to initialize LangSmith: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if LangSmith tracing is available.
        
        Returns:
            bool: True if LangSmith is initialized and ready to use.
        """
        return self._initialized and self._client is not None
    
    def start_trace_session(self, session_name: str) -> str:
        """Start a new trace session.
        
        Creates a new debug session for grouping related traces.
        Works even when LangSmith is unavailable (returns a local session ID).
        
        Args:
            session_name: Human-readable name for the session.
            
        Returns:
            str: Unique session ID.
        """
        session_id = str(uuid.uuid4())
        session = DebugSession(
            session_id=session_id,
            name=session_name,
            created_at=datetime.now(timezone.utc),
            configuration={
                "trace_level": self.trace_level,
                "project": self.project_name,
                "langsmith_available": self.is_available(),
            }
        )
        self._sessions[session_id] = session
        
        logger.info(f"Started trace session: {session_name} ({session_id})")
        return session_id
    
    def end_trace_session(self, session_id: str) -> TraceMetadata:
        """End a trace session and return metadata.
        
        Args:
            session_id: The session ID returned from start_trace_session.
            
        Returns:
            TraceMetadata: Summary of the session including trace count and status.
        """
        session = self._sessions.get(session_id)
        
        if session is None:
            logger.warning(f"Session not found: {session_id}")
            return TraceMetadata(
                session_id=session_id,
                session_name="unknown",
                start_time=datetime.now(timezone.utc),
                end_time=datetime.now(timezone.utc),
                trace_count=0,
                status="not_found",
            )
        
        session.ended_at = datetime.now(timezone.utc)
        session.status = "completed"
        
        # Build LangSmith URL if available
        langsmith_url = None
        if self.is_available():
            langsmith_url = f"https://smith.langchain.com/o/default/projects/p/{self.project_name}"
        
        metadata = TraceMetadata(
            session_id=session.session_id,
            session_name=session.name,
            start_time=session.created_at,
            end_time=session.ended_at,
            trace_count=len(session.trace_ids),
            status=session.status,
            langsmith_url=langsmith_url,
        )
        
        logger.info(f"Ended trace session: {session.name} ({session_id})")
        return metadata
    
    def get_session(self, session_id: str) -> Optional[DebugSession]:
        """Retrieve a session by ID.
        
        Args:
            session_id: The session ID to look up.
            
        Returns:
            Optional[DebugSession]: The session if found, None otherwise.
        """
        return self._sessions.get(session_id)
    
    def add_trace_to_session(self, session_id: str, trace_id: str) -> bool:
        """Add a trace ID to a session.
        
        Args:
            session_id: The session to add the trace to.
            trace_id: The trace ID to add.
            
        Returns:
            bool: True if the trace was added, False if session not found.
        """
        session = self._sessions.get(session_id)
        if session is None:
            return False
        
        session.trace_ids.append(trace_id)
        return True
    
    def list_sessions(self) -> list[DebugSession]:
        """List all trace sessions.
        
        Returns:
            list[DebugSession]: All sessions, sorted by creation time (newest first).
        """
        return sorted(
            self._sessions.values(),
            key=lambda s: s.created_at,
            reverse=True
        )


# Singleton instance for easy access
_tracer_instance: Optional[LangSmithTracer] = None


def get_tracer() -> LangSmithTracer:
    """Get the singleton LangSmithTracer instance.
    
    Returns:
        LangSmithTracer: The tracer instance.
    """
    global _tracer_instance
    if _tracer_instance is None:
        _tracer_instance = LangSmithTracer()
    return _tracer_instance


def reset_tracer() -> None:
    """Reset the singleton tracer (useful for testing)."""
    global _tracer_instance
    _tracer_instance = None
