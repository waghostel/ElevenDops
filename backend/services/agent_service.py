"""Service for managing AI agents."""

import logging
from datetime import datetime
from typing import List, Optional
import uuid

from backend.models.schemas import (
    AgentCreateRequest,
    AgentResponse,
    AgentListResponse,
    AnswerStyle,
    SyncStatus,
)
from backend.services.elevenlabs_service import get_elevenlabs_service, ElevenLabsAgentError, ElevenLabsService
from backend.services.data_service import get_data_service, DataServiceInterface


SYSTEM_PROMPTS = {
    AnswerStyle.PROFESSIONAL: """# Personality

You are a professional medical assistant. You are accurate, objective, and solution-oriented.
You communicate with precision and maintain a formal yet approachable tone.

# Goal

Help patients understand their medical conditions by answering questions based on the provided knowledge base.

# Guardrails

Only answer questions that can be addressed using the provided knowledge base. This step is important.
Never provide diagnoses, prescribe medications, or give advice beyond the knowledge base scope.
If a question falls outside the knowledge base:
- For non-urgent questions: Politely advise the patient to ask their doctor during their next visit.
- For urgent symptoms (severe pain, difficulty breathing, chest pain, sudden vision loss, etc.): Immediately advise the patient to call 911, go to the emergency room, or contact their doctor right away. This step is important.

Acknowledge when you don't know an answer instead of guessing.

# Tone

Keep responses clear, concise, and professional. Avoid medical jargon when possible.
""",

    AnswerStyle.FRIENDLY: """# Personality

You are a warm and friendly medical assistant. You are empathetic, patient, and approachable.
You make patients feel comfortable and heard while providing helpful information.

# Goal

Help patients understand their medical conditions by answering questions based on the provided knowledge base in a caring and supportive manner.

# Guardrails

Only answer questions that can be addressed using the provided knowledge base. This step is important.
Never provide diagnoses, prescribe medications, or give advice beyond the knowledge base scope.
If a question falls outside the knowledge base:
- For non-urgent questions: Gently let the patient know this is a great question for their doctor at their next visit.
- For urgent symptoms (severe pain, difficulty breathing, chest pain, sudden vision loss, etc.): Calmly but firmly advise the patient to call 911, go to the emergency room, or contact their doctor immediately. This step is important.

Acknowledge when you don't know an answer instead of guessing.

# Tone

Speak in a warm, conversational manner. Use reassuring language and brief affirmations like "I understand" or "That's a great question."
""",

    AnswerStyle.EDUCATIONAL: """# Personality

You are a patient educator and health literacy specialist. You focus on teaching and ensuring understanding.
You explain medical concepts simply and check for comprehension.

# Goal

Help patients learn about their medical conditions by answering questions based on the provided knowledge base. Focus on education and building patient understanding.

# Guardrails

Only answer questions that can be addressed using the provided knowledge base. This step is important.
Never provide diagnoses, prescribe medications, or give advice beyond the knowledge base scope.
If a question falls outside the knowledge base:
- For non-urgent questions: Explain that this topic would be best discussed with their doctor, and encourage them to bring it up at their next visit.
- For urgent symptoms (severe pain, difficulty breathing, chest pain, sudden vision loss, etc.): Clearly explain the importance of immediate medical attention and advise the patient to call 911, go to the emergency room, or contact their doctor right away. This step is important.

Acknowledge when you don't know an answer instead of guessing.

# Tone

Use simple, clear language. Explain medical terms when necessary. Ask "Does that make sense?" after complex explanations.
""",
}


class AgentService:
    """Service for managing conversational AI agents."""

    def __init__(
        self,
        elevenlabs_service: Optional[ElevenLabsService] = None,
        data_service: Optional[DataServiceInterface] = None,
    ):
        """Initialize services with dependency injection."""
        self.elevenlabs = elevenlabs_service or get_elevenlabs_service()
        self.data_service = data_service or get_data_service()

    def _get_system_prompt(self, style: AnswerStyle) -> str:
        """Get structured English system prompt based on answer style."""
        return SYSTEM_PROMPTS.get(style, SYSTEM_PROMPTS[AnswerStyle.PROFESSIONAL])

    def get_system_prompts(self) -> dict:
        """Return all system prompts keyed by style value.
        
        Returns:
            dict: Mapping of style value (str) to system prompt (str).
        """
        return {style.value: prompt for style, prompt in SYSTEM_PROMPTS.items()}

    async def _get_synced_knowledge_base(self, knowledge_ids: List[str]) -> List[dict]:
        """Get synced knowledge base items with full metadata.
        
        Args:
            knowledge_ids: List of knowledge document IDs (local UUIDs).
            
        Returns:
            List of dicts with 'id', 'name', 'type' for ElevenLabs API.
        """
        if not knowledge_ids:
            return []
            
        kb_items = []
        for kid in knowledge_ids:
            # We must await the coroutine
            doc = await self.data_service.get_knowledge_document(kid)
            if doc and doc.sync_status == SyncStatus.COMPLETED and doc.elevenlabs_document_id:
                kb_items.append({
                    "id": doc.elevenlabs_document_id,
                    "name": doc.disease_name,  # Use disease_name as document name
                    "type": "file"  # Documents are uploaded as files
                })
        
        return kb_items 

    async def create_agent(self, request: AgentCreateRequest) -> AgentResponse:
        """Create a new agent.

        Args:
            request: Agent creation request.

        Returns:
            AgentResponse: Created agent details.
        
        Raises:
            Exception: If creation fails.
        """
        elevenlabs_agent_id = None
        try:
            # 1. Generate system prompt (use custom override if provided)
            if request.system_prompt_override:
                system_prompt = request.system_prompt_override
            else:
                system_prompt = self._get_system_prompt(request.answer_style)
            
            # 1.5 Filter knowledge base with full metadata
            synced_knowledge_base = await self._get_synced_knowledge_base(request.knowledge_ids)

            # 2. Create agent in ElevenLabs
            elevenlabs_agent_id = self.elevenlabs.create_agent(
                name=request.name,
                system_prompt=system_prompt,
                knowledge_base=synced_knowledge_base,
                voice_id=request.voice_id,
                languages=request.languages,
            )

            # 3. Create local agent record
            agent_id = str(uuid.uuid4())
            agent = AgentResponse(
                agent_id=agent_id,
                name=request.name,
                knowledge_ids=request.knowledge_ids, # Keep original local IDs
                voice_id=request.voice_id,
                answer_style=request.answer_style,
                languages=request.languages,
                elevenlabs_agent_id=elevenlabs_agent_id,
                doctor_id=request.doctor_id,
                created_at=datetime.utcnow(),
            )

            # 4. Save to DB
            await self.data_service.save_agent(agent)
            
            logging.info(f"Created agent {agent_id} (ElevenLabs ID: {elevenlabs_agent_id})")
            return agent

        except Exception as e:
            logging.error(f"Failed to create agent: {e}")
            
            # Rollback: If ElevenLabs creation succeeded but subsequent steps failed
            if elevenlabs_agent_id:
                try:
                    self.elevenlabs.delete_agent(elevenlabs_agent_id)
                    logging.info(f"Rolled back ElevenLabs agent {elevenlabs_agent_id}")
                except Exception as rollback_error:
                    logging.error(f"Failed to rollback ElevenLabs agent {elevenlabs_agent_id}: {rollback_error}")
            
            raise e

    async def get_agents(self, doctor_id: Optional[str] = None) -> AgentListResponse:
        """List all agents.
        
        Args:
            doctor_id: Optional doctor ID to filter by.

        Returns:
            AgentListResponse: List of agents.
        """
        agents = await self.data_service.get_agents(doctor_id)
        return AgentListResponse(agents=agents, total_count=len(agents))

    async def get_agent(self, agent_id: str) -> Optional[AgentResponse]:
        """Get single agent.
        
        Args:
            agent_id: ID of the agent to retrieve.
            
        Returns:
            AgentResponse or None.
        """
        return await self.data_service.get_agent(agent_id)

    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent.

        Args:
            agent_id: ID of the agent to delete.

        Returns:
            bool: True if deleted.
        """
        agent = await self.data_service.get_agent(agent_id)
        if not agent:
            return False
        
        try:
            # Delete from ElevenLabs
            self.elevenlabs.delete_agent(agent.elevenlabs_agent_id)
        except Exception as e:
            # We log but continue to delete local record to ensure consistency
            # or at least not block local cleanup.
            logging.warning(f"Failed to delete agent {agent.elevenlabs_agent_id} from ElevenLabs: {e}")

        # Delete from DB
        return await self.data_service.delete_agent(agent_id)


# Singleton instance
_service = AgentService()

def get_agent_service() -> AgentService:
    """Get the AgentService instance."""
    return _service
