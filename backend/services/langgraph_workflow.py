from typing import TypedDict, Optional, Any, Callable, AsyncGenerator
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import logging
import os
import time
import traceback
import functools
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from backend.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class TraceStep:
    """Represents a single step in a workflow trace."""
    step_id: str
    node_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    input_state: dict = field(default_factory=dict)
    output_state: Optional[dict] = None
    error: Optional[str] = None
    stack_trace: Optional[str] = None
    duration_ms: Optional[int] = None


@dataclass
class WorkflowTrace:
    """Collects trace data for a complete workflow execution."""
    trace_id: str
    workflow_name: str
    start_time: datetime
    steps: list[TraceStep] = field(default_factory=list)
    end_time: Optional[datetime] = None
    status: str = "running"
    input_data: dict = field(default_factory=dict)
    output_data: Optional[dict] = None
    metadata: dict = field(default_factory=dict)
    
    def add_step(self, step: TraceStep) -> None:
        """Add a trace step to this workflow trace."""
        self.steps.append(step)
    
    def complete(self, output_data: Optional[dict] = None, error: Optional[str] = None) -> None:
        """Mark the workflow as complete."""
        self.end_time = datetime.now(timezone.utc)
        self.output_data = output_data
        if error:
            self.status = "error"
        else:
            self.status = "completed"


# Global trace storage for the current execution
_current_trace: Optional[WorkflowTrace] = None


def get_current_trace() -> Optional[WorkflowTrace]:
    """Get the current workflow trace."""
    return _current_trace


def set_current_trace(trace: Optional[WorkflowTrace]) -> None:
    """Set the current workflow trace."""
    global _current_trace
    _current_trace = trace


def trace_node(func: Callable) -> Callable:
    """Decorator that wraps a workflow node with tracing capabilities.
    
    Captures:
    - Node entry/exit timing (millisecond precision)
    - Input/output state
    - Errors with full stack traces
    
    Works whether LangSmith is configured or not (graceful degradation).
    
    Args:
        func: The node function to wrap.
        
    Returns:
        Wrapped function with tracing.
    """
    @functools.wraps(func)
    async def async_wrapper(state: dict) -> dict:
        step_id = str(uuid.uuid4())
        node_name = func.__name__
        start_time = datetime.now(timezone.utc)
        start_perf = time.perf_counter()
        
        settings = get_settings()
        trace_level = settings.langsmith_trace_level
        
        # Create trace step
        step = TraceStep(
            step_id=step_id,
            node_name=node_name,
            start_time=start_time,
            input_state=dict(state) if trace_level == "debug" else {},
        )
        
        # Log entry if debug level
        if trace_level == "debug":
            logger.debug(f"[TRACE] Entering node: {node_name}")
        
        try:
            # Execute the node
            result = await func(state)
            
            # Capture timing
            end_perf = time.perf_counter()
            step.end_time = datetime.now(timezone.utc)
            step.duration_ms = int((end_perf - start_perf) * 1000)
            step.output_state = dict(result) if trace_level == "debug" else {}
            
            # Log exit
            if trace_level in ("debug", "info"):
                logger.info(
                    f"[TRACE] Node {node_name} completed in {step.duration_ms}ms"
                )
            
            # Add to current trace if available
            current = get_current_trace()
            if current:
                current.add_step(step)
            
            return result
            
        except Exception as e:
            # Capture error with stack trace
            end_perf = time.perf_counter()
            step.end_time = datetime.now(timezone.utc)
            step.duration_ms = int((end_perf - start_perf) * 1000)
            step.error = str(e)
            step.stack_trace = traceback.format_exc()
            
            logger.error(
                f"[TRACE] Node {node_name} failed after {step.duration_ms}ms: {e}"
            )
            
            # Add to current trace if available
            current = get_current_trace()
            if current:
                current.add_step(step)
            
            raise
    
    @functools.wraps(func)
    def sync_wrapper(state: dict) -> dict:
        step_id = str(uuid.uuid4())
        node_name = func.__name__
        start_time = datetime.now(timezone.utc)
        start_perf = time.perf_counter()
        
        settings = get_settings()
        trace_level = settings.langsmith_trace_level
        
        step = TraceStep(
            step_id=step_id,
            node_name=node_name,
            start_time=start_time,
            input_state=dict(state) if trace_level == "debug" else {},
        )
        
        if trace_level == "debug":
            logger.debug(f"[TRACE] Entering node: {node_name}")
        
        try:
            result = func(state)
            
            end_perf = time.perf_counter()
            step.end_time = datetime.now(timezone.utc)
            step.duration_ms = int((end_perf - start_perf) * 1000)
            step.output_state = dict(result) if trace_level == "debug" else {}
            
            if trace_level in ("debug", "info"):
                logger.info(
                    f"[TRACE] Node {node_name} completed in {step.duration_ms}ms"
                )
            
            current = get_current_trace()
            if current:
                current.add_step(step)
            
            return result
            
        except Exception as e:
            end_perf = time.perf_counter()
            step.end_time = datetime.now(timezone.utc)
            step.duration_ms = int((end_perf - start_perf) * 1000)
            step.error = str(e)
            step.stack_trace = traceback.format_exc()
            
            logger.error(
                f"[TRACE] Node {node_name} failed after {step.duration_ms}ms: {e}"
            )
            
            current = get_current_trace()
            if current:
                current.add_step(step)
            
            raise
    
    # Return appropriate wrapper based on function type
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


class ScriptGenerationState(TypedDict):
    """State for LangGraph script generation workflow."""
    knowledge_content: str
    prompt: str
    model_name: str
    generated_script: str
    error: Optional[str]


async def prepare_context_node(state: ScriptGenerationState) -> dict:
    """Prepare context for generation."""
    # Placeholder for any preprocessing (e.g. text cleaning, truncation)
    return {}


async def generate_script_node(state: ScriptGenerationState) -> dict:
    """Generate script using Google Gemini."""
    try:
        model_name = state["model_name"]
        prompt = state["prompt"]
        content = state["knowledge_content"]
        
        settings = get_settings()
        api_key = settings.google_api_key
        
        # When testing or without API key, we should handle gracefully or mock
        if not api_key:
             # If we are mocking data, return a mock response
             if settings.use_mock_data:
                 return {"generated_script": f"Mock script generated for model {model_name}"}
             return {"error": "Google API key not configured"}

        # Debug: Log key status (masked)
        masked_key = f"{api_key[:4]}...{api_key[-4:]}" if api_key else "None"
        logger.info(f"Initiating ChatGoogleGenerativeAI with model: {model_name}, Key: {masked_key}")
        
        # Explicitly set env var as fallback for the library
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key

        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.7,
            timeout=30,  # 30 second timeout for API calls
            max_retries=2,  # Retry on transient failures
        )
        
        # Determine strictness? For now simple prompt
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=f"Here is the knowledge document content:\n\n{content}")
        ]
        
        # Use asyncio timeout as additional protection
        import asyncio
        try:
            response = await asyncio.wait_for(
                llm.ainvoke(messages),
                timeout=35.0  # Slightly longer than LLM timeout to let it handle retries
            )
        except asyncio.TimeoutError:
            logger.error(f"Gemini API timeout after 35s for model {model_name}")
            return {
                "error": f"API timeout: Model '{model_name}' did not respond within 35 seconds. "
                         "Please verify your API key or try a different model."
            }
        return {"generated_script": response.content}
    except Exception as e:
        # Improved error handling with detailed logging and meaningful error messages
        error_type = type(e).__name__
        error_msg = str(e)
        error_repr = repr(e)
        
        # Log full traceback for server-side debugging
        logger.error(f"Script generation failed with {error_type}: {error_msg}", exc_info=True)
        
        # Return meaningful error message
        if error_msg:
            return {"error": f"{error_type}: {error_msg}"}
        elif error_repr:
            return {"error": f"{error_type}: {error_repr}"}
        else:
            return {"error": f"Unknown error of type {error_type}. Check server logs for details."}


def post_process_node(state: ScriptGenerationState) -> dict:
    """Post-process the generated script."""
    if state.get("error"):
        return {}
        
    script = state.get("generated_script", "")
    # Remove markdown code blocks if present
    if script.startswith("```"):
        script = script.split("\n", 1)[1]
        if script.endswith("```"):
            script = script.rsplit("\n", 1)[0]
            
    return {"generated_script": script.strip()}


def create_script_generation_graph():
    """Create the workflow graph (original, untraced version)."""
    workflow = StateGraph(ScriptGenerationState)
    
    workflow.add_node("prepare_context", prepare_context_node)
    workflow.add_node("generate_script", generate_script_node)
    workflow.add_node("post_process", post_process_node)
    
    workflow.set_entry_point("prepare_context")
    workflow.add_edge("prepare_context", "generate_script")
    workflow.add_edge("generate_script", "post_process")
    workflow.add_edge("post_process", END)
    
    return workflow.compile()


def create_traced_script_generation_graph():
    """Create the workflow graph with tracing enabled.
    
    Wraps all nodes with the trace_node decorator for:
    - Timing information
    - State transition logging
    - Error capture with stack traces
    
    Returns:
        Compiled LangGraph workflow with tracing.
    """
    workflow = StateGraph(ScriptGenerationState)
    
    # Wrap nodes with tracing
    workflow.add_node("prepare_context", trace_node(prepare_context_node))
    workflow.add_node("generate_script", trace_node(generate_script_node))
    workflow.add_node("post_process", trace_node(post_process_node))
    
    workflow.set_entry_point("prepare_context")
    workflow.add_edge("prepare_context", "generate_script")
    workflow.add_edge("generate_script", "post_process")
    workflow.add_edge("post_process", END)
    
    return workflow.compile()


async def run_traced_workflow(
    knowledge_content: str,
    prompt: str,
    model_name: str,
    session_id: Optional[str] = None,
) -> tuple[dict, WorkflowTrace]:
    """Run the script generation workflow with full tracing.
    
    Args:
        knowledge_content: The knowledge document content.
        prompt: The generation prompt.
        model_name: The Gemini model to use.
        session_id: Optional session ID to associate the trace with.
        
    Returns:
        Tuple of (final_state, workflow_trace)
    """
    trace_id = str(uuid.uuid4())
    trace = WorkflowTrace(
        trace_id=trace_id,
        workflow_name="script_generation",
        start_time=datetime.now(timezone.utc),
        input_data={
            "knowledge_content_length": len(knowledge_content),
            "prompt_length": len(prompt),
            "model_name": model_name,
        },
        metadata={
            "session_id": session_id,
            "project": get_settings().langsmith_project,
        }
    )
    
    # Set current trace for nodes to use
    set_current_trace(trace)
    
    try:
        graph = create_traced_script_generation_graph()
        
        initial_state: ScriptGenerationState = {
            "knowledge_content": knowledge_content,
            "prompt": prompt,
            "model_name": model_name,
            "generated_script": "",
            "error": None,
        }
        
        result = await graph.ainvoke(initial_state)
        
        trace.complete(output_data={
            "has_script": bool(result.get("generated_script")),
            "has_error": bool(result.get("error")),
        })
        
        return result, trace
        
    except Exception as e:
        trace.complete(error=str(e))
        raise
        
    finally:
        set_current_trace(None)


def post_process_script(script: str) -> str:
    """Post-process a generated script by removing markdown code blocks.
    
    Args:
        script: Raw script content from LLM.
        
    Returns:
        Cleaned script content.
    """
    if script.startswith("```"):
        script = script.split("\n", 1)[1] if "\n" in script else script[3:]
        if script.endswith("```"):
            script = script.rsplit("\n", 1)[0] if "\n" in script else script[:-3]
    return script.strip()


async def generate_script_stream(
    knowledge_content: str,
    prompt: str,
    model_name: str,
) -> AsyncGenerator[dict, None]:
    """Stream script generation tokens from the LLM.
    
    This function streams tokens as they are generated, keeping the connection
    alive and providing real-time feedback. This avoids timeout issues with
    large documents that may take 60+ seconds to process.
    
    Args:
        knowledge_content: The knowledge document content to process.
        prompt: The system prompt for script generation.
        model_name: The Gemini model to use.
        
    Yields:
        dict events with one of these types:
        - {"type": "token", "content": "..."} - Partial content chunk
        - {"type": "complete", "script": "...", "model_used": "..."} - Final result
        - {"type": "error", "message": "..."} - Error occurred
    """
    settings = get_settings()
    api_key = settings.google_api_key
    
    # Handle missing API key
    if not api_key:
        if settings.use_mock_data:
            # Mock streaming for testing
            mock_script = f"Mock streaming script generated for model {model_name}"
            for word in mock_script.split():
                yield {"type": "token", "content": word + " "}
            yield {"type": "complete", "script": mock_script, "model_used": model_name}
            return
        yield {"type": "error", "message": "Google API key not configured"}
        return
    
    # Log masked key for debugging
    masked_key = f"{api_key[:4]}...{api_key[-4:]}" if api_key else "None"
    logger.info(f"Starting streaming generation with model: {model_name}, Key: {masked_key}")
    
    # Set env var as fallback for the library
    os.environ["GOOGLE_API_KEY"] = api_key
    
    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.7,
            streaming=True,  # Enable streaming mode
        )
        
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=f"Here is the knowledge document content:\n\n{knowledge_content}")
        ]
        
        full_content = ""
        chunk_count = 0
        
        async for chunk in llm.astream(messages):
            if chunk.content:
                full_content += chunk.content
                chunk_count += 1
                yield {"type": "token", "content": chunk.content}
        
        logger.info(f"Streaming complete: {chunk_count} chunks, {len(full_content)} chars total")
        
        # Post-process and yield final result
        processed_script = post_process_script(full_content)
        yield {
            "type": "complete",
            "script": processed_script,
            "model_used": model_name
        }
        
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e) if str(e) else repr(e)
        logger.error(f"Streaming generation failed: {error_type}: {error_msg}", exc_info=True)
        yield {"type": "error", "message": f"{error_type}: {error_msg}"}
