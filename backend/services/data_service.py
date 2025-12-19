"""Data service layer for ElevenDops backend.

This module provides a mock data service that can be easily replaced
with a Firestore client for production use.
"""

from datetime import datetime
from typing import List, Optional, Protocol
import uuid
import re

from backend.models.schemas import (
    DashboardStatsResponse,
    KnowledgeDocumentCreate,
    KnowledgeDocumentResponse,
    PatientSessionCreate,
    PatientSessionResponse,
    SyncStatus,
    DocumentType,
    ConversationSummarySchema,
    ConversationDetailSchema,
    ConversationMessageSchema,
)


class DataServiceProtocol(Protocol):
    """Protocol defining the data service interface."""

    async def get_dashboard_stats(self) -> DashboardStatsResponse:
        """Get dashboard statistics."""
        ...

    async def create_knowledge_document(
        self, doc: KnowledgeDocumentCreate
    ) -> KnowledgeDocumentResponse:
        """Create a new knowledge document."""
        ...

    async def get_knowledge_documents(self) -> List[KnowledgeDocumentResponse]:
        """Get all knowledge documents."""
        ...

    async def get_knowledge_document(
        self, knowledge_id: str
    ) -> Optional[KnowledgeDocumentResponse]:
        """Get a specific knowledge document by ID."""
        ...

    async def update_knowledge_sync_status(
        self, knowledge_id: str, status: SyncStatus, elevenlabs_id: Optional[str] = None
    ) -> bool:
        """Update the sync status of a knowledge document."""
        ...

    async def delete_knowledge_document(self, knowledge_id: str) -> bool:
        """Delete a knowledge document."""
        ...

    async def create_patient_session(
        self, session: PatientSessionResponse
    ) -> PatientSessionResponse:
        """Create a new patient session."""
        ...

    async def get_patient_session(
        self, session_id: str
    ) -> Optional[PatientSessionResponse]:
        """Get a patient session by ID."""
        ...

    async def add_session_message(
        self, session_id: str, message: ConversationMessageSchema
    ) -> None:
        """Add a message to a session."""
        ...

    async def get_session_messages(
        self, session_id: str
    ) -> List[ConversationMessageSchema]:
        """Get messages for a session."""
        ...

    async def save_conversation(
        self, conversation: ConversationDetailSchema
    ) -> ConversationDetailSchema:
        """Save a conversation."""
        ...

    async def get_conversation_logs(
        self,
        patient_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        requires_attention_only: bool = False,
    ) -> List[ConversationSummarySchema]:
        """Get conversation logs with filters."""
        ...

    async def get_conversation_detail(
        self, conversation_id: str
    ) -> Optional[ConversationDetailSchema]:
        """Get a specific conversation by ID."""
        ...

    # Optional: Update session if we need to store state (e.g. ended status)
    # For now, maybe just 'end_session'? 
    # Let's keep it simple.



class MockDataService:
    """Mock data service for development and testing.

    This service returns mock data and stores state in memory.
    """

    def __init__(self):
        """Initialize with empty in-memory storage."""
        self._documents: dict[str, KnowledgeDocumentResponse] = {}
        self._sessions: dict[str, PatientSessionResponse] = {}
        self._conversation_details: dict[str, ConversationDetailSchema] = {}
        self._session_messages: dict[str, List[ConversationMessageSchema]] = {}

    def _parse_structured_sections(self, content: str) -> dict:
        """Parse markdown content into structured sections based on headers.
        
        Args:
            content: Raw markdown content.
            
        Returns:
            Dict mapping headers to section content.
        """
        sections = {}
        # improved regex to capture headers and content
        # splitting by headers (# or ##, etc)
        # simplistic MVP parser
        headers = re.split(r'(^|\n)(#{1,6}\s.*)', content)
        
        if not headers:
            return {"raw": content}

        current_header = "Introduction"
        # First chunk is usually content before first header
        if headers[0].strip():
            sections[current_header] = headers[0].strip()

        # Iterate through captured groups
        # split output structure: [text, newline, header, text, newline, header, text...]
        # We need to process from index 1 safely
        
        # Simpler approach: find all occurrences, allowing for indentation
        matches = list(re.finditer(r'(^|\n)(?P<level>\s*#{1,6})\s(?P<title>.*)', content))
        if not matches:
             # Just put everything under Introduction if no headers found? Or "raw"?
             # Let's keep existing logic or just return raw content as 'content'
             if content.strip():
                 sections["content"] = content
             return sections

        last_pos = 0
        for i, match in enumerate(matches):
            current_start = match.start()  # This might include the newline
            
            # If this is the first match, capture intro text before it
            if i == 0:
                intro = content[0:current_start].strip()
                if intro:
                    sections["Introduction"] = intro

            header_title = match.group("title").strip()
            
            # Content starts after this match
            match_end = match.end()
            
            # Content ends at start of next match or EOF
            if i + 1 < len(matches):
                next_start = matches[i+1].start()
                section_content = content[match_end:next_start].strip()
            else:
                section_content = content[match_end:].strip()
            
            if section_content:
                sections[header_title] = section_content
        
        return sections

    async def get_dashboard_stats(self) -> DashboardStatsResponse:
        """Get mock dashboard statistics.

        Returns stats based on in-memory data for documents.
        """
        doc_count = len(self._documents)
        return DashboardStatsResponse(
            document_count=doc_count,
            agent_count=2,  # Mock constant
            audio_count=10,  # Mock constant
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
            document_type=doc.document_type,
            raw_content=doc.raw_content,
            sync_status=SyncStatus.PENDING,
            elevenlabs_document_id=None,
            structured_sections=structured,
            created_at=now,
        )
        
        self._documents[knowledge_id] = new_doc
        return new_doc

    async def get_knowledge_documents(self) -> List[KnowledgeDocumentResponse]:
        """Get all knowledge documents from memory."""
        return list(self._documents.values())

    async def get_knowledge_document(
        self, knowledge_id: str
    ) -> Optional[KnowledgeDocumentResponse]:
        """Get a specific knowledge document by ID."""
        return self._documents.get(knowledge_id)

    async def update_knowledge_sync_status(
        self, knowledge_id: str, status: SyncStatus, elevenlabs_id: Optional[str] = None
    ) -> bool:
        """Update the sync status of a knowledge document."""
        if knowledge_id not in self._documents:
            return False
        
        doc = self._documents[knowledge_id]
        
        updated_doc = KnowledgeDocumentResponse(
            knowledge_id=doc.knowledge_id,
            doctor_id=doc.doctor_id,
            disease_name=doc.disease_name,
            document_type=doc.document_type,
            raw_content=doc.raw_content,
            sync_status=status,
            elevenlabs_document_id=elevenlabs_id if elevenlabs_id is not None else doc.elevenlabs_document_id,
            structured_sections=doc.structured_sections,
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
            
            # Date filtering
            # Assuming created_at is aware if start_date/end_date are, or both naive.
            # Usually we might need to be careful with timezone mixed types.
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


# Singleton instance to persist state across requests in mock mode
_mock_instance = MockDataService()

def get_data_service() -> MockDataService:
    """Get the data service instance."""
    return _mock_instance
