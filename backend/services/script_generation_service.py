import logging
import datetime
from typing import TypedDict, Optional
from backend.services.langgraph_workflow import create_script_generation_graph

logger = logging.getLogger(__name__)

class ScriptGenerationResult(TypedDict):
    script: str
    model_used: str
    generated_at: datetime.datetime
    error: Optional[str]

class ScriptGenerationService:
    """Service for AI-powered script generation using LangGraph."""
    
    def __init__(self):
        self.workflow = create_script_generation_graph()

    async def generate_script(
        self,
        knowledge_content: str,
        model_name: str,
        prompt: str
    ) -> ScriptGenerationResult:
        """Generate voice-optimized script using LangGraph workflow.
        
        Args:
            knowledge_content: Raw content from knowledge document
            model_name: Gemini model to use
            prompt: System prompt for generation
            
        Returns:
            ScriptGenerationResult with script and metadata
            
        Raises:
            Exception: If generation fails
        """
        inputs = {
            "knowledge_content": knowledge_content,
            "prompt": prompt,
            "model_name": model_name,
            "generated_script": "",
            "error": None
        }
        
        try:
            # Execute the workflow
            result = await self.workflow.ainvoke(inputs)
            
            if result.get("error"):
                raise Exception(result["error"])
                
            return {
                "script": result.get("generated_script", ""),
                "model_used": model_name,
                "generated_at": datetime.datetime.now(datetime.timezone.utc),
                "error": None
            }
        except Exception as e:
            logger.error(f"Error in script generation service: {e}")
            raise e
