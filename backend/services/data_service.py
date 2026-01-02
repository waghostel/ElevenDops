"""Data service layer for ElevenDops backend.

This module provides a mock data service that can be easily replaced
with a Firestore client for production use.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
import uuid
import re

from backend.config import get_settings
from backend.models.schemas import (
    DashboardStatsResponse,
    KnowledgeDocumentCreate,
    KnowledgeDocumentUpdate,
    KnowledgeDocumentResponse,
    PatientSessionResponse,
    SyncStatus,
    ConversationSummarySchema,
    ConversationDetailSchema,
    ConversationMessageSchema,
    AudioMetadata,
    AgentResponse,
    AnswerStyle,
    CustomTemplateCreate,
    CustomTemplateUpdate,
    CustomTemplateResponse,
)


class DataServiceInterface(ABC):
    """Abstract interface for data service implementations."""

    # ==================== Dashboard ====================
    @abstractmethod
    async def get_dashboard_stats(self) -> DashboardStatsResponse:
        """Get dashboard statistics."""
        pass

    # ==================== Knowledge Documents ====================
    @abstractmethod
    async def create_knowledge_document(
        self, doc: KnowledgeDocumentCreate
    ) -> KnowledgeDocumentResponse:
        """Create a new knowledge document."""
        pass

    @abstractmethod
    async def update_knowledge_document(
        self, knowledge_id: str, update_data: KnowledgeDocumentUpdate
    ) -> Optional[KnowledgeDocumentResponse]:
        """Update a knowledge document."""
        pass

    @abstractmethod
    async def get_knowledge_documents(
        self, doctor_id: Optional[str] = None
    ) -> List[KnowledgeDocumentResponse]:
        """Get all knowledge documents, optionally filtered by doctor."""
        pass

    @abstractmethod
    async def get_knowledge_document(
        self, knowledge_id: str
    ) -> Optional[KnowledgeDocumentResponse]:
        """Get a specific knowledge document by ID."""
        pass

    @abstractmethod
    async def update_knowledge_sync_status(
        self, 
        knowledge_id: str, 
        status: SyncStatus, 
        elevenlabs_id: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Update the sync status of a knowledge document."""
        pass

    @abstractmethod
    async def delete_knowledge_document(self, knowledge_id: str) -> bool:
        """Delete a knowledge document."""
        pass

    # ==================== Audio Files ====================
    @abstractmethod
    async def save_audio_metadata(self, audio: AudioMetadata) -> AudioMetadata:
        """Save audio file metadata."""
        pass

    @abstractmethod
    async def get_audio_files(
        self, knowledge_id: Optional[str] = None, doctor_id: Optional[str] = None
    ) -> List[AudioMetadata]:
        """Get audio files, optionally filtered by knowledge_id and/or doctor_id."""
        pass

    @abstractmethod
    async def get_audio_file(self, audio_id: str) -> Optional[AudioMetadata]:
        """Get a specific audio file by ID."""
        pass

    @abstractmethod
    async def delete_audio_file(self, audio_id: str) -> bool:
        """Delete an audio file metadata."""
        pass

    # ==================== Agents ====================
    @abstractmethod
    async def save_agent(self, agent: AgentResponse) -> AgentResponse:
        """Save an agent."""
        pass

    @abstractmethod
    async def get_agents(
        self, doctor_id: Optional[str] = None
    ) -> List[AgentResponse]:
        """Get all agents, optionally filtered by doctor."""
        pass

    @abstractmethod
    async def get_agent(self, agent_id: str) -> Optional[AgentResponse]:
        """Get a specific agent by ID."""
        pass

    @abstractmethod
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent."""
        pass

    # ==================== Patient Sessions ====================
    @abstractmethod
    async def create_patient_session(
        self, session: PatientSessionResponse
    ) -> PatientSessionResponse:
        """Create a new patient session."""
        pass

    @abstractmethod
    async def get_patient_session(
        self, session_id: str
    ) -> Optional[PatientSessionResponse]:
        """Get a patient session by ID."""
        pass

    @abstractmethod
    async def add_session_message(
        self, session_id: str, message: ConversationMessageSchema
    ) -> None:
        """Add a message to a session."""
        pass

    @abstractmethod
    async def get_session_messages(
        self, session_id: str
    ) -> List[ConversationMessageSchema]:
        """Get messages for a session."""
        pass

    # ==================== Conversations ====================
    @abstractmethod
    async def save_conversation(
        self, conversation: ConversationDetailSchema
    ) -> ConversationDetailSchema:
        """Save a conversation."""
        pass

    @abstractmethod
    async def get_conversation_logs(
        self,
        patient_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        requires_attention_only: bool = False,
    ) -> List[ConversationSummarySchema]:
        """Get conversation logs with filters."""
        pass

    @abstractmethod
    async def get_conversation_detail(
        self, conversation_id: str
    ) -> Optional[ConversationDetailSchema]:
        """Get a specific conversation by ID."""
        pass

    @abstractmethod
    async def get_conversation_count(self) -> int:
        """Get total number of conversations."""
        pass

    @abstractmethod
    async def get_average_duration(self) -> float:
        """Get average conversation duration in seconds."""
        pass

    @abstractmethod
    async def get_attention_percentage(self) -> float:
        """Get percentage of conversations requiring attention."""
        pass

    # ==================== Custom Templates ====================
    @abstractmethod
    async def create_custom_template(
        self, template: CustomTemplateCreate, user_id: str = "default_user"
    ) -> CustomTemplateResponse:
        """Create a new custom template."""
        pass

    @abstractmethod
    async def get_custom_templates(
        self, user_id: Optional[str] = None
    ) -> List[CustomTemplateResponse]:
        """Get all custom templates, optionally filtered by user."""
        pass

    @abstractmethod
    async def get_custom_template(
        self, template_id: str
    ) -> Optional[CustomTemplateResponse]:
        """Get a specific custom template by ID."""
        pass

    @abstractmethod
    async def update_custom_template(
        self, template_id: str, update_data: CustomTemplateUpdate
    ) -> Optional[CustomTemplateResponse]:
        """Update a custom template."""
        pass

    @abstractmethod
    async def delete_custom_template(self, template_id: str) -> bool:
        """Delete a custom template."""
        pass


class MockDataService(DataServiceInterface):
    """Mock data service for development and testing.

    This service returns mock data and stores state in memory.
    """

    def __init__(self):
        """Initialize with empty in-memory storage."""
        self._documents: dict[str, KnowledgeDocumentResponse] = {}
        self._sessions: dict[str, PatientSessionResponse] = {}
        self._conversation_details: dict[str, ConversationDetailSchema] = {}
        self._session_messages: dict[str, List[ConversationMessageSchema]] = {}
        self._audio_files: dict[str, AudioMetadata] = {}
        self._agents: dict[str, AgentResponse] = {}
        self._custom_templates: dict[str, CustomTemplateResponse] = {}

    def _parse_structured_sections(self, content: str) -> dict:
        """Parse markdown content into structured sections based on headers.
        
        Args:
            content: Raw markdown content.
            
        Returns:
            Dict mapping headers to section content.
        """
        sections = {}
        matches = list(re.finditer(r'(^|\n)(?P<level>\s*#{1,6})\s(?P<title>.*)', content))
        if not matches:
             if content.strip():
                 sections["content"] = content
             return sections

        for i, match in enumerate(matches):
            current_start = match.start()
            
            # If this is the first match, capture intro text before it
            if i == 0:
                intro = content[0:current_start].strip()
                if intro:
                    sections["Introduction"] = intro

            header_title = match.group("title").strip()
            match_end = match.end()
            
            if i + 1 < len(matches):
                next_start = matches[i+1].start()
                section_content = content[match_end:next_start].strip()
            else:
                section_content = content[match_end:].strip()
            
            if section_content:
                sections[header_title] = section_content
        
        return sections

    async def get_dashboard_stats(self) -> DashboardStatsResponse:
        """Get mock dashboard statistics."""
        return DashboardStatsResponse(
            document_count=len(self._documents),
            agent_count=len(self._agents),
            audio_count=len(self._audio_files),
            last_activity=datetime.now(),
        )

    async def create_knowledge_document(
        self, doc: KnowledgeDocumentCreate
    ) -> KnowledgeDocumentResponse:
        """Create a new knowledge document in memory."""
        knowledge_id = str(uuid.uuid4())
        now = datetime.now()
        
        structured = self._parse_structured_sections(doc.raw_content)
        
        new_doc = KnowledgeDocumentResponse(
            knowledge_id=knowledge_id,
            doctor_id=doc.doctor_id,
            disease_name=doc.disease_name,
            tags=doc.tags,
            raw_content=doc.raw_content,
            sync_status=SyncStatus.PENDING,
            elevenlabs_document_id=None,
            structured_sections=structured,
            created_at=now,
        )
        
        self._documents[knowledge_id] = new_doc
        return new_doc

    async def update_knowledge_document(
        self, knowledge_id: str, update_data: KnowledgeDocumentUpdate
    ) -> Optional[KnowledgeDocumentResponse]:
        """Update a knowledge document in memory."""
        if knowledge_id not in self._documents:
            return None
            
        doc = self._documents[knowledge_id]
        
        # Create a copy with updated fields
        updated_fields = update_data.model_dump(exclude_unset=True)
        if not updated_fields:
            return doc
            
        # Create new instance with updated values
        updated_doc = doc.model_copy(update=updated_fields)
        updated_doc.modified_at = datetime.now()
        
        self._documents[knowledge_id] = updated_doc
        return updated_doc

    async def get_knowledge_documents(
        self, doctor_id: Optional[str] = None
    ) -> List[KnowledgeDocumentResponse]:
        """Get all knowledge documents from memory."""
        docs = list(self._documents.values())
        if doctor_id:
            docs = [d for d in docs if d.doctor_id == doctor_id]
        return docs

    async def get_knowledge_document(
        self, knowledge_id: str
    ) -> Optional[KnowledgeDocumentResponse]:
        """Get a specific knowledge document by ID."""
        return self._documents.get(knowledge_id)

    async def update_knowledge_sync_status(
        self, knowledge_id: str, status: SyncStatus, elevenlabs_id: Optional[str] = None, error_message: Optional[str] = None
    ) -> bool:
        """Update the sync status of a knowledge document."""
        if knowledge_id not in self._documents:
            return False
        
        doc = self._documents[knowledge_id]
        
        # Calculate new retry count based on status (matching Firestore logic)
        new_retry_count = doc.sync_retry_count
        if status == SyncStatus.SYNCING:
            new_retry_count = doc.sync_retry_count + 1
        elif status == SyncStatus.PENDING:
            new_retry_count = 0
        
        # Determine error message (matching Firestore logic)
        new_error_message = None
        if error_message:
            new_error_message = error_message
        elif status == SyncStatus.COMPLETED or status == SyncStatus.PENDING:
            new_error_message = None
        elif status == SyncStatus.FAILED:
            new_error_message = doc.sync_error_message  # Keep existing if not provided
        
        updated_doc = KnowledgeDocumentResponse(
            knowledge_id=doc.knowledge_id,
            doctor_id=doc.doctor_id,
            disease_name=doc.disease_name,
            tags=doc.tags,
            raw_content=doc.raw_content,
            sync_status=status,
            elevenlabs_document_id=elevenlabs_id if elevenlabs_id is not None else doc.elevenlabs_document_id,
            structured_sections=doc.structured_sections,
            sync_error_message=new_error_message,
            last_sync_attempt=datetime.now(),
            sync_retry_count=new_retry_count,
            created_at=doc.created_at,
        )
        
        self._documents[knowledge_id] = updated_doc
        return True

    async def delete_knowledge_document(self, knowledge_id: str) -> bool:
        """Delete a knowledge document from memory."""
        if knowledge_id in self._documents:
            del self._documents[knowledge_id]
            return True
        return False

    # ==================== Audio Files Implementation ====================
    async def save_audio_metadata(self, audio: AudioMetadata) -> AudioMetadata:
        """Save audio file metadata."""
        self._audio_files[audio.audio_id] = audio
        return audio

    async def get_audio_files(
        self, knowledge_id: Optional[str] = None, doctor_id: Optional[str] = None
    ) -> List[AudioMetadata]:
        """Get audio files, optionally filtered by knowledge_id and/or doctor_id."""
        audios = list(self._audio_files.values())
        if knowledge_id:
            audios = [a for a in audios if a.knowledge_id == knowledge_id]
        if doctor_id:
            audios = [a for a in audios if a.doctor_id == doctor_id]
        return audios

    async def get_audio_file(self, audio_id: str) -> Optional[AudioMetadata]:
        """Get a specific audio file by ID."""
        return self._audio_files.get(audio_id)

    async def delete_audio_file(self, audio_id: str) -> bool:
        """Delete an audio file metadata."""
        if audio_id in self._audio_files:
            del self._audio_files[audio_id]
            return True
        return False

    # ==================== Agents Implementation ====================
    async def save_agent(self, agent: AgentResponse) -> AgentResponse:
        """Save an agent."""
        self._agents[agent.agent_id] = agent
        return agent

    async def get_agents(
        self, doctor_id: Optional[str] = None
    ) -> List[AgentResponse]:
        """Get all agents, optionally filtered by doctor."""
        agents = list(self._agents.values())
        if doctor_id:
            agents = [a for a in agents if a.doctor_id == doctor_id]
        return agents

    async def get_agent(self, agent_id: str) -> Optional[AgentResponse]:
        """Get a specific agent by ID."""
        return self._agents.get(agent_id)

    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent."""
        if agent_id in self._agents:
            del self._agents[agent_id]
            return True
        return False

    # ==================== Patient Sessions Implementation ====================
    async def create_patient_session(
        self, session: PatientSessionResponse
    ) -> PatientSessionResponse:
        """Create a new patient session in memory."""
        self._sessions[session.session_id] = session
        return session

    async def get_patient_session(
        self, session_id: str
    ) -> Optional[PatientSessionResponse]:
        """Get a patient session by ID."""
        return self._sessions.get(session_id)

    async def add_session_message(
        self, session_id: str, message: ConversationMessageSchema
    ) -> None:
        """Add a message to a session in memory."""
        if session_id not in self._session_messages:
            self._session_messages[session_id] = []
        self._session_messages[session_id].append(message)

    async def get_session_messages(
        self, session_id: str
    ) -> List[ConversationMessageSchema]:
        """Get messages for a session from memory."""
        return self._session_messages.get(session_id, [])

    # ==================== Conversations Implementation ====================
    async def save_conversation(
        self, conversation: ConversationDetailSchema
    ) -> ConversationDetailSchema:
        """Save a conversation in memory."""
        self._conversation_details[conversation.conversation_id] = conversation
        return conversation

    async def get_conversation_logs(
        self,
        patient_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        requires_attention_only: bool = False,
    ) -> List[ConversationSummarySchema]:
        """Get conversation logs from memory with filters."""
        results = []
        for conv in self._conversation_details.values():
            # Filters
            if patient_id and patient_id.lower() not in conv.patient_id.lower():
                continue
            
            if start_date and conv.created_at < start_date:
                continue
            if end_date and conv.created_at > end_date:
                continue
                
            if requires_attention_only and not conv.requires_attention:
                continue

            summary = ConversationSummarySchema(
                conversation_id=conv.conversation_id,
                patient_id=conv.patient_id,
                agent_id=conv.agent_id,
                agent_name=conv.agent_name,
                requires_attention=conv.requires_attention,
                main_concerns=conv.main_concerns,
                total_messages=len(conv.messages),
                answered_count=len(conv.answered_questions),
                unanswered_count=len(conv.unanswered_questions),
                duration_seconds=conv.duration_seconds,
                created_at=conv.created_at,
            )
            results.append(summary)
            
        # Sort by created_at descending
        results.sort(key=lambda x: x.created_at, reverse=True)
        return results

    async def get_conversation_detail(
        self, conversation_id: str
    ) -> Optional[ConversationDetailSchema]:
        """Get a specific conversation by ID."""
        return self._conversation_details.get(conversation_id)

    async def get_conversation_count(self) -> int:
        """Get total number of conversations."""
        return len(self._conversation_details)

    async def get_average_duration(self) -> float:
        """Get average conversation duration in seconds."""
        conversations = [
            c for c in self._conversation_details.values() 
            if c.duration_seconds > 0
        ]
        if not conversations:
            return 0.0
        
        total_duration = sum(c.duration_seconds for c in conversations)
        return total_duration / len(conversations)

    async def get_attention_percentage(self) -> float:
        """Get percentage of conversations requiring attention."""
        conversations = list(self._conversation_details.values())
        if not conversations:
            return 0.0
            
        attention_count = sum(1 for c in conversations if c.requires_attention)
        return (attention_count / len(conversations)) * 100.0

    # ==================== Custom Templates ====================
    async def create_custom_template(
        self, template: CustomTemplateCreate, user_id: str = "default_user"
    ) -> CustomTemplateResponse:
        """Create a new custom template."""
        import uuid
        template_id = str(uuid.uuid4())
        now = datetime.now()
        
        response = CustomTemplateResponse(
            template_id=template_id,
            display_name=template.display_name,
            description=template.description,
            category="custom",
            preview=template.content[:200],
            content=template.content,
            created_by=user_id,
            created_at=now,
        )
        self._custom_templates[template_id] = response
        return response

    async def get_custom_templates(
        self, user_id: Optional[str] = None
    ) -> List[CustomTemplateResponse]:
        """Get all custom templates, optionally filtered by user."""
        templates = list(self._custom_templates.values())
        if user_id:
            templates = [t for t in templates if t.created_by == user_id]
        templates.sort(key=lambda x: x.created_at, reverse=True)
        return templates

    async def get_custom_template(
        self, template_id: str
    ) -> Optional[CustomTemplateResponse]:
        """Get a specific custom template by ID."""
        return self._custom_templates.get(template_id)

    async def update_custom_template(
        self, template_id: str, update_data: CustomTemplateUpdate
    ) -> Optional[CustomTemplateResponse]:
        """Update a custom template."""
        if template_id not in self._custom_templates:
            return None
        
        existing = self._custom_templates[template_id]
        update_fields = update_data.model_dump(exclude_unset=True)
        
        if not update_fields:
            return existing
        
        # Update preview if content changed
        if "content" in update_fields:
            update_fields["preview"] = update_fields["content"][:200]
        
        updated = existing.model_copy(update=update_fields)
        self._custom_templates[template_id] = updated
        return updated

    async def delete_custom_template(self, template_id: str) -> bool:
        """Delete a custom template."""
        if template_id in self._custom_templates:
            del self._custom_templates[template_id]
            return True
        return False


# Singleton instances
_mock_instance = None
_firestore_instance = None


def get_data_service() -> DataServiceInterface:
    """Factory function - returns appropriate service based on config.
    
    Returns FirestoreDataService when:
    - USE_FIRESTORE_EMULATOR is true (local development with emulator)
    - USE_MOCK_DATA is false (production mode)
    
    Returns MockDataService when:
    - USE_MOCK_DATA is true AND USE_FIRESTORE_EMULATOR is false
    """
    global _mock_instance, _firestore_instance
    
    settings = get_settings()
    
    # Use Firestore if emulator is enabled OR if not using mock data
    # Note: firestore_emulator defaults to True in local dev, so we check it explicitly.
    # If explicit mock data is requested, we should probably favor it if emulator is FALSE.
    # But if emulator is TRUE, we should probably prefer that because it's "better" mock.
    # The logic in design doc was:
    # use_firestore = settings.use_firestore_emulator or not getattr(settings, 'use_mock_data', True)
    # Wait, if use_mock_data is default False (from config update), then 'not False' is True.
    # So by default 'use_firestore' is True.
    
    use_firestore = settings.use_firestore_emulator or not settings.use_mock_data
    
    # However, if use_firestore_emulator is False AND use_mock_data is False, what happens?
    # Then use_firestore becomes True. But that assumes production firestore?
    # Yes, typically if not mocking, we use real/emulator firestore.
    
    if use_firestore:
        if _firestore_instance is None:
            # Lazy import to avoid circular imports or import errors if dependencies missing
            from backend.services.firestore_data_service import FirestoreDataService
            _firestore_instance = FirestoreDataService()
        return _firestore_instance
    else:
        if _mock_instance is None:
            _mock_instance = MockDataService()
        return _mock_instance
