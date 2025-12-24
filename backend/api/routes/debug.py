"""Debug API routes for LangGraph workflow debugging.

Provides endpoints for:
- Script generation with tracing
- Trace retrieval and inspection
- Debug session management
"""

import logging
from datetime import datetime
from typing import Optional, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.config import get_settings
from backend.services.langsmith_tracer import get_tracer, reset_tracer
from backend.services.langgraph_workflow import (
    run_traced_workflow,
    WorkflowTrace,
    TraceStep,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/debug", tags=["debug"])


# ============================================================================
# Request/Response Models
# ============================================================================

class DebugExecutionRequest(BaseModel):
    """Request for debug script generation."""
    knowledge_content: str = Field(..., min_length=1, description="Knowledge document content")
    prompt: str = Field(..., min_length=1, description="Generation prompt")
    model_name: str = Field(default="gemini-2.0-flash", description="Gemini model to use")
    debug_level: Literal["debug", "info", "error"] = Field(
        default="info", 
        description="Trace verbosity level"
    )
    session_name: Optional[str] = Field(
        default=None, 
        description="Optional session name for grouping traces"
    )


class TraceStepResponse(BaseModel):
    """Response model for a trace step."""
    step_id: str
    node_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None
    error: Optional[str] = None
    has_stack_trace: bool = False


class DebugExecutionResponse(BaseModel):
    """Response from debug script generation."""
    trace_id: str
    session_id: Optional[str] = None
    execution_status: str
    generated_script: Optional[str] = None
    error_details: Optional[dict] = None
    steps: list[TraceStepResponse]
    total_duration_ms: Optional[int] = None
    langsmith_url: Optional[str] = None


class TraceDetailResponse(BaseModel):
    """Detailed trace response."""
    trace_id: str
    workflow_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str
    input_data: dict
    output_data: Optional[dict] = None
    metadata: dict
    steps: list[TraceStepResponse]


class SessionResponse(BaseModel):
    """Response model for a debug session."""
    session_id: str
    name: str
    created_at: datetime
    ended_at: Optional[datetime] = None
    trace_count: int
    status: str


class SessionListResponse(BaseModel):
    """Response for listing debug sessions."""
    sessions: list[SessionResponse]
    total_count: int


class StartSessionRequest(BaseModel):
    """Request to start a new debug session."""
    name: str = Field(..., min_length=1, description="Session name")


class StartSessionResponse(BaseModel):
    """Response from starting a debug session."""
    session_id: str
    name: str
    created_at: datetime


# ============================================================================
# Helper Functions
# ============================================================================

def _trace_step_to_response(step: TraceStep) -> TraceStepResponse:
    """Convert a TraceStep to response model."""
    return TraceStepResponse(
        step_id=step.step_id,
        node_name=step.node_name,
        start_time=step.start_time,
        end_time=step.end_time,
        duration_ms=step.duration_ms,
        error=step.error,
        has_stack_trace=step.stack_trace is not None,
    )


def _calculate_total_duration(trace: WorkflowTrace) -> Optional[int]:
    """Calculate total workflow duration in milliseconds."""
    if trace.start_time and trace.end_time:
        delta = trace.end_time - trace.start_time
        return int(delta.total_seconds() * 1000)
    return None


# ============================================================================
# Endpoints
# ============================================================================

@router.post(
    "/script-generation",
    response_model=DebugExecutionResponse,
    responses={
        400: {"description": "Invalid request parameters"},
        500: {"description": "Workflow execution failed"},
    },
)
async def debug_script_generation(request: DebugExecutionRequest):
    """Execute script generation workflow with full tracing.
    
    Returns trace data including:
    - Trace ID for LangSmith Studio examination
    - Step-by-step execution details
    - Timing information
    - Error details if any
    """
    tracer = get_tracer()
    session_id = None
    
    # Start session if name provided
    if request.session_name:
        session_id = tracer.start_trace_session(request.session_name)
    
    try:
        result, trace = await run_traced_workflow(
            knowledge_content=request.knowledge_content,
            prompt=request.prompt,
            model_name=request.model_name,
            session_id=session_id,
        )
        
        # Add trace to session if applicable
        if session_id:
            tracer.add_trace_to_session(session_id, trace.trace_id)
        
        # Build response
        steps = [_trace_step_to_response(s) for s in trace.steps]
        
        error_details = None
        if result.get("error"):
            error_details = {"message": result["error"]}
        
        # Build LangSmith URL
        settings = get_settings()
        langsmith_url = None
        if tracer.is_available():
            langsmith_url = f"https://smith.langchain.com/o/default/projects/p/{settings.langsmith_project}"
        
        return DebugExecutionResponse(
            trace_id=trace.trace_id,
            session_id=session_id,
            execution_status=trace.status,
            generated_script=result.get("generated_script"),
            error_details=error_details,
            steps=steps,
            total_duration_ms=_calculate_total_duration(trace),
            langsmith_url=langsmith_url,
        )
        
    except Exception as e:
        logger.error(f"Debug script generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/sessions",
    response_model=SessionListResponse,
)
async def list_sessions():
    """List all debug sessions."""
    tracer = get_tracer()
    sessions = tracer.list_sessions()
    
    session_responses = [
        SessionResponse(
            session_id=s.session_id,
            name=s.name,
            created_at=s.created_at,
            ended_at=s.ended_at,
            trace_count=len(s.trace_ids),
            status=s.status,
        )
        for s in sessions
    ]
    
    return SessionListResponse(
        sessions=session_responses,
        total_count=len(session_responses),
    )


@router.post(
    "/sessions",
    response_model=StartSessionResponse,
)
async def start_session(request: StartSessionRequest):
    """Start a new debug session."""
    tracer = get_tracer()
    session_id = tracer.start_trace_session(request.name)
    session = tracer.get_session(session_id)
    
    return StartSessionResponse(
        session_id=session_id,
        name=session.name,
        created_at=session.created_at,
    )


@router.get(
    "/sessions/{session_id}",
    response_model=SessionResponse,
    responses={404: {"description": "Session not found"}},
)
async def get_session(session_id: str):
    """Get a specific debug session."""
    tracer = get_tracer()
    session = tracer.get_session(session_id)
    
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionResponse(
        session_id=session.session_id,
        name=session.name,
        created_at=session.created_at,
        ended_at=session.ended_at,
        trace_count=len(session.trace_ids),
        status=session.status,
    )


@router.post(
    "/sessions/{session_id}/end",
    responses={404: {"description": "Session not found"}},
)
async def end_session(session_id: str):
    """End a debug session."""
    tracer = get_tracer()
    
    if tracer.get_session(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    metadata = tracer.end_trace_session(session_id)
    
    return {
        "session_id": metadata.session_id,
        "status": metadata.status,
        "trace_count": metadata.trace_count,
        "langsmith_url": metadata.langsmith_url,
    }


@router.get("/health")
async def debug_health():
    """Check debug service health and LangSmith availability."""
    tracer = get_tracer()
    settings = get_settings()
    
    return {
        "status": "healthy",
        "langsmith_configured": settings.is_langsmith_configured(),
        "langsmith_available": tracer.is_available(),
        "project": settings.langsmith_project,
        "trace_level": settings.langsmith_trace_level,
    }
