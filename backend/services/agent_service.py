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
)
from backend.services.elevenlabs_service import get_elevenlabs_service, ElevenLabsAgentError
# Assuming data_service exists or we need to mock it for now
# from backend.services.data_service import get_data_service


class AgentService:
    """Service for managing conversational AI agents."""

    def __init__(self):
        """Initialize services."""
        self.elevenlabs = get_elevenlabs_service()
        # self.db = get_data_service() # TBD
        # Temporary in-memory storage until Firestore is integrated
        self._agents = {} 

    def _get_system_prompt(self, style: AnswerStyle) -> str:
        """Get system prompt based on answer style."""
        prompts = {
            AnswerStyle.PROFESSIONAL: (
                "You are a professional medical assistant. "
                "Provide accurate, objective, and formal responses. "
                "Do not use slang or overly casual language. "
                "Prioritize medical accuracy and clear communication."
            ),
            AnswerStyle.FRIENDLY: (
                "You are a warm and friendly medical assistant. "
                "Be approachable, empathetic, and easy to understand. "
                "Use simple language and a comforting tone. "
                "Make the patient feel heard and cared for."
            ),
            AnswerStyle.EDUCATIONAL: (
                "You are an educational medical assistant. "
                "Focus on teaching the patient about their condition. "
                "Explain medical terms simply and verify understanding. "
                "Use analogies where appropriate."
            ),
        }
        return prompts.get(style, prompts[AnswerStyle.PROFESSIONAL])

    async def create_agent(self, request: AgentCreateRequest) -> AgentResponse:
        """Create a new agent.

        Args:
            request: Agent creation request.

        Returns:
            AgentResponse: Created agent details.
        
        Raises:
            Exception: If creation fails.
        """
        try:
            # 1. Generate system prompt
            system_prompt = self._get_system_prompt(request.answer_style)

            # 2. Create agent in ElevenLabs
            elevenlabs_agent_id = self.elevenlabs.create_agent(
                name=request.name,
                system_prompt=system_prompt,
                knowledge_base_ids=request.knowledge_ids,
                voice_id=request.voice_id,
            )

            # 3. Create local agent record
            agent_id = str(uuid.uuid4())
            agent = AgentResponse(
                agent_id=agent_id,
                name=request.name,
                knowledge_ids=request.knowledge_ids,
                voice_id=request.voice_id,
                answer_style=request.answer_style,
                elevenlabs_agent_id=elevenlabs_agent_id,
                doctor_id=request.doctor_id,
                created_at=datetime.utcnow(),
            )

            # 4. Save to DB (mocked for now)
            self._agents[agent_id] = agent
            
            logging.info(f"Created agent {agent_id} (ElevenLabs ID: {elevenlabs_agent_id})")
            return agent

        except Exception as e:
            logging.error(f"Failed to create agent: {e}")
            # If ElevenLabs creation succeeded but DB failed, we should rollback ElevenLabs
            # But for MVP we just raise
            raise e

    async def get_agents(self) -> AgentListResponse:
        """List all agents.

        Returns:
            AgentListResponse: List of agents.
        """
        agents_list = list(self._agents.values())
        return AgentListResponse(agents=agents_list, total_count=len(agents_list))

    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent.

        Args:
            agent_id: ID of the agent to delete.

        Returns:
            bool: True if deleted.
        """
        if agent_id not in self._agents:
            return False
            
        agent = self._agents[agent_id]
        
        try:
            # Delete from ElevenLabs
            self.elevenlabs.delete_agent(agent.elevenlabs_agent_id)
        except ElevenLabsAgentError:
            logging.warning(f"Failed to delete agent {agent.elevenlabs_agent_id} from ElevenLabs, continuing local delete")

        # Delete from DB
        del self._agents[agent_id]
        return True


# Singleton instance
_service = AgentService()

def get_agent_service() -> AgentService:
    """Get the AgentService instance."""
    return _service
