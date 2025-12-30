"""Property tests for trace level configuration and performance timing.

Property 8: Performance Timing Collection
- Timing information captured for each workflow step
- Millisecond precision timing
Validates: Requirements 5.3

Property 9: Trace Level Configuration
- Different trace levels capture appropriate data
- Debug level captures most detail, error level captures least
Validates: Requirements 4.4
"""

import os
import asyncio
from unittest.mock import patch
from datetime import datetime, timezone

import pytest
from hypothesis import given, settings as hypothesis_settings, strategies as st

from backend.config import get_settings
from backend.services.langgraph_workflow import (
    trace_node,
    TraceStep,
    WorkflowTrace,
    get_current_trace,
    set_current_trace,
)


class TestPerformanceTimingCollection:
    """Property 8: Performance Timing Collection.
    
    Feature: langsmith-debug-integration
    Validates: Requirements 5.3
    
    For any workflow execution, timing information should be captured
    for each workflow step with millisecond precision.
    """

    def setup_method(self) -> None:
        """Reset state before each test."""
        get_settings.cache_clear()
        set_current_trace(None)

    @pytest.mark.asyncio
    async def test_timing_captured_with_ms_precision(self) -> None:
        """Test that timing is captured with millisecond precision."""
        trace = WorkflowTrace(
            trace_id="timing-test",
            workflow_name="test",
            start_time=datetime.now(timezone.utc),
        )
        set_current_trace(trace)
        
        @trace_node
        async def timed_node(state: dict) -> dict:
            await asyncio.sleep(0.025)  # 25ms
            return {"done": True}
        
        with patch.dict(os.environ, {"LANGSMITH_TRACE_LEVEL": "info"}):
            get_settings.cache_clear()
            await timed_node({})
        
        step = trace.steps[0]
        assert step.duration_ms is not None
        # Should be at least 25ms (with some tolerance)
        assert step.duration_ms >= 20
        # Should be an integer (milliseconds)
        assert isinstance(step.duration_ms, int)
        
        set_current_trace(None)

    def test_sync_timing_captured(self) -> None:
        """Test that sync node timing is also captured."""
        trace = WorkflowTrace(
            trace_id="sync-timing",
            workflow_name="test",
            start_time=datetime.now(timezone.utc),
        )
        set_current_trace(trace)
        
        @trace_node
        def sync_node(state: dict) -> dict:
            import time
            time.sleep(0.015)  # 15ms
            return {"result": True}
        
        with patch.dict(os.environ, {"LANGSMITH_TRACE_LEVEL": "info"}):
            get_settings.cache_clear()
            sync_node({})
        
        step = trace.steps[0]
        assert step.duration_ms is not None
        assert step.duration_ms >= 10
        
        set_current_trace(None)

    @pytest.mark.asyncio
    async def test_timing_includes_start_and_end_time(self) -> None:
        """Test that steps include start and end timestamps."""
        trace = WorkflowTrace(
            trace_id="timestamps",
            workflow_name="test",
            start_time=datetime.now(timezone.utc),
        )
        set_current_trace(trace)
        
        @trace_node
        async def quick_node(state: dict) -> dict:
            return {}
        
        with patch.dict(os.environ, {"LANGSMITH_TRACE_LEVEL": "info"}):
            get_settings.cache_clear()
            await quick_node({})
        
        step = trace.steps[0]
        assert step.start_time is not None
        assert step.end_time is not None
        assert step.end_time >= step.start_time
        
        set_current_trace(None)

    @pytest.mark.asyncio
    async def test_multiple_steps_have_sequential_times(self) -> None:
        """Test that multiple steps have logical sequential timing."""
        trace = WorkflowTrace(
            trace_id="sequential",
            workflow_name="test",
            start_time=datetime.now(timezone.utc),
        )
        set_current_trace(trace)
        
        @trace_node
        async def step_1(state: dict) -> dict:
            await asyncio.sleep(0.01)
            return {"step": 1}
        
        @trace_node
        async def step_2(state: dict) -> dict:
            await asyncio.sleep(0.01)
            return {"step": 2}
        
        with patch.dict(os.environ, {"LANGSMITH_TRACE_LEVEL": "info"}):
            get_settings.cache_clear()
            await step_1({})
            await step_2({})
        
        assert len(trace.steps) == 2
        step1 = trace.steps[0]
        step2 = trace.steps[1]
        
        # Step 2 should start after step 1 ends
        assert step2.start_time >= step1.end_time
        
        set_current_trace(None)


class TestTraceLevelConfiguration:
    """Property 9: Trace Level Configuration.
    
    Feature: langsmith-debug-integration
    Validates: Requirements 4.4
    
    For any configured trace level (debug, info, error), the system
    should capture trace data appropriate to that level, with debug
    level capturing the most detail.
    """

    def setup_method(self) -> None:
        """Reset state before each test."""
        get_settings.cache_clear()
        set_current_trace(None)

    def test_debug_level_captures_input_state(self) -> None:
        """Test that debug level captures full input state."""
        trace = WorkflowTrace(
            trace_id="debug-input",
            workflow_name="test",
            start_time=datetime.now(timezone.utc),
        )
        set_current_trace(trace)
        
        @trace_node
        def node(state: dict) -> dict:
            return {"output": "value"}
        
        with patch.dict(os.environ, {"LANGSMITH_TRACE_LEVEL": "debug"}):
            get_settings.cache_clear()
            node({"input": "test", "data": 123})
        
        step = trace.steps[0]
        assert step.input_state == {"input": "test", "data": 123}
        
        set_current_trace(None)

    def test_debug_level_captures_output_state(self) -> None:
        """Test that debug level captures full output state."""
        trace = WorkflowTrace(
            trace_id="debug-output",
            workflow_name="test",
            start_time=datetime.now(timezone.utc),
        )
        set_current_trace(trace)
        
        @trace_node
        def node(state: dict) -> dict:
            return {"result": "success", "count": 42}
        
        with patch.dict(os.environ, {"LANGSMITH_TRACE_LEVEL": "debug"}):
            get_settings.cache_clear()
            node({})
        
        step = trace.steps[0]
        assert step.output_state == {"result": "success", "count": 42}
        
        set_current_trace(None)

    def test_info_level_does_not_capture_state(self) -> None:
        """Test that info level does not capture full state."""
        trace = WorkflowTrace(
            trace_id="info-no-state",
            workflow_name="test",
            start_time=datetime.now(timezone.utc),
        )
        set_current_trace(trace)
        
        @trace_node
        def node(state: dict) -> dict:
            return {"result": "value"}
        
        with patch.dict(os.environ, {"LANGSMITH_TRACE_LEVEL": "info"}):
            get_settings.cache_clear()
            node({"input": "data"})
        
        step = trace.steps[0]
        assert step.input_state == {}  # Empty at info level
        assert step.output_state == {}  # Empty at info level
        
        set_current_trace(None)

    def test_error_level_still_captures_errors(self) -> None:
        """Test that error level still captures error information."""
        trace = WorkflowTrace(
            trace_id="error-capture",
            workflow_name="test",
            start_time=datetime.now(timezone.utc),
        )
        set_current_trace(trace)
        
        @trace_node
        def failing_node(state: dict) -> dict:
            raise ValueError("Test error")
        
        with patch.dict(os.environ, {"LANGSMITH_TRACE_LEVEL": "error"}):
            get_settings.cache_clear()
            with pytest.raises(ValueError):
                failing_node({})
        
        step = trace.steps[0]
        assert step.error == "Test error"
        assert step.stack_trace is not None
        
        set_current_trace(None)

    def test_all_levels_capture_timing(self) -> None:
        """Test that all trace levels capture timing information."""
        for level in ["debug", "info", "error"]:
            trace = WorkflowTrace(
                trace_id=f"timing-{level}",
                workflow_name="test",
                start_time=datetime.now(timezone.utc),
            )
            set_current_trace(trace)
            
            @trace_node
            def timed_node(state: dict) -> dict:
                return {}
            
            with patch.dict(os.environ, {"LANGSMITH_TRACE_LEVEL": level}):
                get_settings.cache_clear()
                timed_node({})
            
            step = trace.steps[0]
            assert step.duration_ms is not None, f"Level {level} should capture timing"
            
            set_current_trace(None)

    @given(level=st.sampled_from(["debug", "info", "error"]))

    def test_any_valid_level_records_steps(self, level: str) -> None:
        """Property: Any valid trace level records workflow steps."""
        get_settings.cache_clear()
        
        trace = WorkflowTrace(
            trace_id=f"level-{level}",
            workflow_name="test",
            start_time=datetime.now(timezone.utc),
        )
        set_current_trace(trace)
        
        @trace_node
        def simple_node(state: dict) -> dict:
            return {}
        
        with patch.dict(os.environ, {"LANGSMITH_TRACE_LEVEL": level}):
            get_settings.cache_clear()
            simple_node({})
        
        assert len(trace.steps) == 1
        assert trace.steps[0].node_name == "simple_node"
        
        set_current_trace(None)
