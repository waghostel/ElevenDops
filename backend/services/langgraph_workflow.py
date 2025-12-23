from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import logging
from backend.config import get_settings

logger = logging.getLogger(__name__)

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

        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.7
        )
        
        # Determine strictness? For now simple prompt
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=f"Here is the knowledge document content:\n\n{content}")
        ]
        
        response = await llm.ainvoke(messages)
        return {"generated_script": response.content}
    except Exception as e:
        logger.error(f"Script generation failed: {e}")
        return {"error": str(e)}

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
    """Create the workflow graph."""
    workflow = StateGraph(ScriptGenerationState)
    
    workflow.add_node("prepare_context", prepare_context_node)
    workflow.add_node("generate_script", generate_script_node)
    workflow.add_node("post_process", post_process_node)
    
    workflow.set_entry_point("prepare_context")
    workflow.add_edge("prepare_context", "generate_script")
    workflow.add_edge("generate_script", "post_process")
    workflow.add_edge("post_process", END)
    
    return workflow.compile()
