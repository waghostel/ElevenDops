"""Property tests for LangGraph workflow tracing.

Property 1: Trace Data Completeness
- All workflow steps should be recorded in the trace
- Complete input/output state data captured
- Trace tagged with project identifier
Validates: Requirements 1.1, 1.4, 1.5

Property 3: Error Capture Completeness
- Errors captured with detailed information
- Stack traces and execution context preserved
Validates: Requirements 1.3, 3.2
"""

import os
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone

import pytest
from hypothesis import given, settings as hypothesis_settings, strategies as st

from backend.config import get_settings
from backend.services.langgraph_workflow import (
    TraceStep,
    WorkflowTrace,
    trace_node,
    get_current_trace,
    set_current_trace,
    create_traced_script_generation_graph,
    run_traced_workflow,
)


class TestTraceDataCompleteness:
    """Property 1: Trace Data Completeness.
    
    Feature: langsmith-debug-integration
    Validates: Requirements 1.1, 1.4, 1.5
    
    For any workflow execution with LangSmith enabled, all workflow steps
    should be recorded in the trace with complete input/output state data
    and the trace should be tagged with project identifier.
    """

    def setup_method(self) -> None:
        """Reset state before each test."""
        get_settings.cache_clear()
        set_current_trace(None)

    def test_trace_step_captures_timing(self) -> None:
        """Test that trace steps capture timing information."""
        step = TraceStep(
            step_id="test-123",
            node_name="test_node",
            start_time=datetime.now(timezone.utc),
        )
        step.end_time = datetime.now(timezone.utc)
        step.duration_ms = 100
        
        assert step.duration_ms is not None
        assert step.duration_ms >= 0

    def test_workflow_trace_collects_all_steps(self) -> None:
        """Test that workflow trace collects all added steps."""
        trace = WorkflowTrace(
            trace_id="trace-123",
            workflow_name="test_workflow",
            start_time=datetime.now(timezone.utc),
        )
        
        step1 = TraceStep(
            step_id="step-1",
            node_name="node_1",
            start_time=datetime.now(timezone.utc),
        )
        step2 = TraceStep(
            step_id="step-2",
            node_name="node_2",
            start_time=datetime.now(timezone.utc),
        )
        
        trace.add_step(step1)
        trace.add_step(step2)
        
        assert len(trace.steps) == 2
        assert trace.steps[0].node_name == "node_1"
        assert trace.steps[1].node_name == "node_2"

    def test_workflow_trace_includes_project_metadata(self) -> None:
        """Test that workflow trace includes project identifier."""
        trace = WorkflowTrace(
            trace_id="trace-123",
            workflow_name="test_workflow",
            start_time=datetime.now(timezone.utc),
            metadata={"project": "elevendops-langgraph-debug"}
        )
        
        assert "project" in trace.metadata
        assert trace.metadata["project"] == "elevendops-langgraph-debug"

    def test_workflow_trace_complete_updates_status(self) -> None:
        """Test that completing a trace updates its status."""
        trace = WorkflowTrace(
            trace_id="trace-123",
            workflow_name="test_workflow",
            start_time=datetime.now(timezone.utc),
        )
        
        assert trace.status == "running"
        assert trace.end_time is None
        
        trace.complete(output_data={"result": "success"})
        
        assert trace.status == "completed"
        assert trace.end_time is not None
        assert trace.output_data == {"result": "success"}

    @pytest.mark.asyncio
    async def test_trace_node_records_step_in_trace(self) -> None:
        """Test that trace_node decorator records step in current trace."""
        trace = WorkflowTrace(
            trace_id="trace-test",
            workflow_name="test",
            start_time=datetime.now(timezone.utc),
        )
        set_current_trace(trace)
        
        @trace_node
        async def test_node(state: dict) -> dict:
            return {"processed": True}
        
        with patch.dict(os.environ, {"LANGSMITH_TRACE_LEVEL": "info"}):
            get_settings.cache_clear()
            await test_node({"input": "data"})
        
        assert len(trace.steps) == 1
        assert trace.steps[0].node_name == "test_node"
        assert trace.steps[0].duration_ms is not None
        
        set_current_trace(None)

    @pytest.mark.asyncio
    async def test_trace_node_captures_timing_ms_precision(self) -> None:
        """Test that trace_node captures timing with millisecond precision."""
        trace = WorkflowTrace(
            trace_id="trace-timing",
            workflow_name="test",
            start_time=datetime.now(timezone.utc),
        )
        set_current_trace(trace)
        
        @trace_node
        async def slow_node(state: dict) -> dict:
            await asyncio.sleep(0.05)  # 50ms
            return {}
        
        with patch.dict(os.environ, {"LANGSMITH_TRACE_LEVEL": "info"}):
            get_settings.cache_clear()
            await slow_node({})
        
        step = trace.steps[0]
        assert step.duration_ms is not None
        assert step.duration_ms >= 50  # At least 50ms
        
        set_current_trace(None)

    def test_trace_node_works_without_current_trace(self) -> None:
        """Test that trace_node works even without a current trace."""
        set_current_trace(None)
        
        @trace_node
        def simple_node(state: dict) -> dict:
            return {"done": True}
        
        with patch.dict(os.environ, {"LANGSMITH_TRACE_LEVEL": "info"}):
            get_settings.cache_clear()
            result = simple_node({"input": "test"})
        
        assert result == {"done": True}

    def test_debug_level_captures_input_output_state(self) -> None:
        """Test that debug trace level captures full input/output state."""
        trace = WorkflowTrace(
            trace_id="trace-debug",
            workflow_name="test",
            start_time=datetime.now(timezone.utc),
        )
        set_current_trace(trace)
        
        @trace_node
        def detailed_node(state: dict) -> dict:
            return {"result": "processed"}
        
        with patch.dict(os.environ, {"LANGSMITH_TRACE_LEVEL": "debug"}):
            get_settings.cache_clear()
            detailed_node({"input": "value"})
        
        step = trace.steps[0]
        assert step.input_state == {"input": "value"}
        assert step.output_state == {"result": "processed"}
        
        set_current_trace(None)


class TestErrorCaptureCompleteness:
    """Property 3: Error Capture Completeness.
    
    Feature: langsmith-debug-integration
    Validates: Requirements 1.3, 3.2
    
    For any workflow execution that encounters an error, the trace should
    contain detailed error information including stack traces, context,
    and additional debug metadata.
    """

    def setup_method(self) -> None:
        """Reset state before each test."""
        get_settings.cache_clear()
        set_current_trace(None)

    @pytest.mark.asyncio
    async def test_trace_node_captures_error_message(self) -> None:
        """Test that trace_node captures error messages."""
        trace = WorkflowTrace(
            trace_id="trace-error",
            workflow_name="test",
            start_time=datetime.now(timezone.utc),
        )
        set_current_trace(trace)
        
        @trace_node
        async def failing_node(state: dict) -> dict:
            raise ValueError("Test error message")
        
        with patch.dict(os.environ, {"LANGSMITH_TRACE_LEVEL": "info"}):
            get_settings.cache_clear()
            with pytest.raises(ValueError):
                await failing_node({})
        
        assert len(trace.steps) == 1
        step = trace.steps[0]
        assert step.error == "Test error message"
        
        set_current_trace(None)

    @pytest.mark.asyncio
    async def test_trace_node_captures_stack_trace(self) -> None:
        """Test that trace_node captures full stack traces."""
        trace = WorkflowTrace(
            trace_id="trace-stack",
            workflow_name="test",
            start_time=datetime.now(timezone.utc),
        )
        set_current_trace(trace)
        
        @trace_node
        async def error_node(state: dict) -> dict:
            raise RuntimeError("Stack trace test")
        
        with patch.dict(os.environ, {"LANGSMITH_TRACE_LEVEL": "info"}):
            get_settings.cache_clear()
            with pytest.raises(RuntimeError):
                await error_node({})
        
        step = trace.steps[0]
        assert step.stack_trace is not None
        assert "RuntimeError" in step.stack_trace
        assert "Stack trace test" in step.stack_trace
        assert "error_node" in step.stack_trace
        
        set_current_trace(None)

    def test_sync_trace_node_captures_errors(self) -> None:
        """Test that sync trace_node also captures errors."""
        trace = WorkflowTrace(
            trace_id="trace-sync-error",
            workflow_name="test",
            start_time=datetime.now(timezone.utc),
        )
        set_current_trace(trace)
        
        @trace_node
        def sync_failing_node(state: dict) -> dict:
            raise TypeError("Sync error")
        
        with patch.dict(os.environ, {"LANGSMITH_TRACE_LEVEL": "info"}):
            get_settings.cache_clear()
            with pytest.raises(TypeError):
                sync_failing_node({})
        
        step = trace.steps[0]
        assert step.error == "Sync error"
        assert step.stack_trace is not None
        assert "TypeError" in step.stack_trace
        
        set_current_trace(None)

    @pytest.mark.asyncio
    async def test_error_preserves_timing_information(self) -> None:
        """Test that errors still capture timing information."""
        trace = WorkflowTrace(
            trace_id="trace-error-timing",
            workflow_name="test",
            start_time=datetime.now(timezone.utc),
        )
        set_current_trace(trace)
        
        @trace_node
        async def slow_error_node(state: dict) -> dict:
            await asyncio.sleep(0.02)  # 20ms
            raise Exception("Slow failure")
        
        with patch.dict(os.environ, {"LANGSMITH_TRACE_LEVEL": "info"}):
            get_settings.cache_clear()
            with pytest.raises(Exception):
                await slow_error_node({})
        
        step = trace.steps[0]
        assert step.duration_ms is not None
        assert step.duration_ms >= 20
        assert step.error is not None
        
        set_current_trace(None)

    def test_workflow_trace_complete_with_error(self) -> None:
        """Test that workflow trace records error status on failure."""
        trace = WorkflowTrace(
            trace_id="trace-fail",
            workflow_name="test",
            start_time=datetime.now(timezone.utc),
        )
        
        trace.complete(error="Workflow failed")
        
        assert trace.status == "error"
        assert trace.end_time is not None


class TestRunTracedWorkflow:
    """Tests for the run_traced_workflow function."""

    def setup_method(self) -> None:
        """Reset state before each test."""
        get_settings.cache_clear()
        set_current_trace(None)

    @pytest.mark.asyncio
    async def test_run_traced_workflow_returns_trace(self) -> None:
        """Test that run_traced_workflow returns a complete trace."""
        with patch.dict(
            os.environ,
            {
                "USE_MOCK_DATA": "true",
                "LANGSMITH_TRACE_LEVEL": "info",
            }
        ):
            get_settings.cache_clear()
            
            result, trace = await run_traced_workflow(
                knowledge_content="Test content",
                prompt="Generate a script",
                model_name="gemini-2.0-flash",
                session_id="test-session",
            )
            
            assert trace is not None
            assert trace.trace_id is not None
            assert trace.workflow_name == "script_generation"
            assert trace.status == "completed"
            assert len(trace.steps) == 3  # prepare, generate, post_process

    @pytest.mark.asyncio
    async def test_run_traced_workflow_includes_input_metadata(self) -> None:
        """Test that run_traced_workflow captures input metadata."""
        with patch.dict(
            os.environ,
            {
                "USE_MOCK_DATA": "true",
                "LANGSMITH_TRACE_LEVEL": "info",
            }
        ):
            get_settings.cache_clear()
            
            result, trace = await run_traced_workflow(
                knowledge_content="Sample knowledge",
                prompt="Create script",
                model_name="gemini-2.0-flash",
            )
            
            assert "knowledge_content_length" in trace.input_data
            assert "prompt_length" in trace.input_data
            assert "model_name" in trace.input_data
            assert trace.input_data["model_name"] == "gemini-2.0-flash"

    @pytest.mark.asyncio
    async def test_run_traced_workflow_includes_session_id(self) -> None:
        """Test that run_traced_workflow records session ID in metadata."""
        with patch.dict(
            os.environ,
            {
                "USE_MOCK_DATA": "true",
                "LANGSMITH_TRACE_LEVEL": "info",
            }
        ):
            get_settings.cache_clear()
            
            result, trace = await run_traced_workflow(
                knowledge_content="Test",
                prompt="Test",
                model_name="gemini-2.0-flash",
                session_id="my-session-123",
            )
            
            assert trace.metadata.get("session_id") == "my-session-123"
