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
    AnswerStyle.PROFESSIONAL: (
        "你是一位專業的醫療助理。請以準確、客觀的方式回答病患問題。"
        "請使用正式的語言，避免使用俚語或過於隨意的表達。"
        "優先考慮醫療準確性和清晰的溝通。請使用繁體中文回答。"
    ),
    AnswerStyle.FRIENDLY: (
        "你是一位親切友善的醫療助理。請以溫暖、易懂的方式協助病患。"
        "使用簡單的語言和令人安心的語調。"
        "讓病患感到被傾聽和關心。請使用繁體中文回答。"
    ),
    AnswerStyle.EDUCATIONAL: (
        "你是一位衛教專員。請專注於教導病患了解他們的健康狀況。"
        "用簡單的方式解釋醫學術語，並確認病患的理解。"
        "適當時使用類比來幫助說明。請使用繁體中文回答。"
    ),
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
        """Get Traditional Chinese system prompt based on answer style."""
        return SYSTEM_PROMPTS.get(style, SYSTEM_PROMPTS[AnswerStyle.PROFESSIONAL])

    async def _get_synced_knowledge_ids(self, knowledge_ids: List[str]) -> List[str]:
        """Filter knowledge IDs to only include synced documents.
        
        Args:
            knowledge_ids: List of knowledge document IDs (local UUIDs).
            
        Returns:
            List of ElevenLabs document IDs that are synced.
        """
        if not knowledge_ids:
            return []
            
        synced_ids = []
        for kid in knowledge_ids:
            # We must await the coroutine
            doc = await self.data_service.get_knowledge_document(kid)
            if doc and doc.sync_status == SyncStatus.COMPLETED and doc.elevenlabs_document_id:
                synced_ids.append(doc.elevenlabs_document_id)
        
        return synced_ids 

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
            # 1. Generate system prompt
            system_prompt = self._get_system_prompt(request.answer_style)
            
            # 1.5 Filter knowledge base IDs
            synced_knowledge_ids = await self._get_synced_knowledge_ids(request.knowledge_ids)

            # 2. Create agent in ElevenLabs
            elevenlabs_agent_id = self.elevenlabs.create_agent(
                name=request.name,
                system_prompt=system_prompt,
                knowledge_base_ids=synced_knowledge_ids,
                voice_id=request.voice_id,
            )

            # 3. Create local agent record
            agent_id = str(uuid.uuid4())
            agent = AgentResponse(
                agent_id=agent_id,
                name=request.name,
                knowledge_ids=request.knowledge_ids, # Keep original local IDs
                voice_id=request.voice_id,
                answer_style=request.answer_style,
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
