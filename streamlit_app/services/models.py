"""Data models for Streamlit frontend services."""

from dataclasses import dataclass
from datetime import datetime
from datetime import datetime
from typing import Optional, Dict, List


@dataclass
class DashboardStats:
    """Dashboard statistics data class.

    This dataclass represents the dashboard statistics returned
    by the backend API.

    Attributes:
        document_count: Number of uploaded documents.
        agent_count: Number of active agents.
        audio_count: Number of generated audio files.
        last_activity: Timestamp of last activity.
    """

    document_count: int
    agent_count: int
    audio_count: int
    last_activity: datetime


@dataclass
class KnowledgeDocument:
    """Knowledge document data class.
    
    Attributes:
        knowledge_id: Unique document ID.
        doctor_id: ID of the uploading doctor.
        disease_name: Name of the disease.
        document_type: Type of the document.
        raw_content: Content of the document.
        sync_status: Sync status with ElevenLabs.
        elevenlabs_document_id: Document ID in ElevenLabs.
        structured_sections: Optional structured sections of the document.
        created_at: Creation timestamp.
    """
    
    knowledge_id: str
    doctor_id: str
    disease_name: str
    document_type: str
    raw_content: str
    sync_status: str
    elevenlabs_document_id: Optional[str]
    structured_sections: Optional[Dict[str, str]]
    created_at: datetime
    sync_error_message: Optional[str] = None
    last_sync_attempt: Optional[datetime] = None
    sync_retry_count: int = 0
    modified_at: Optional[datetime] = None


@dataclass
class ScriptResponse:
    """Script generation response data class."""

    script: str
    knowledge_id: str
    generated_at: datetime


@dataclass
class AudioResponse:
    """Audio generation response data class."""

    audio_id: str
    audio_url: str
    knowledge_id: str
    voice_id: str
    duration_seconds: Optional[float]
    script: str
    created_at: datetime


@dataclass
class VoiceOption:
    """Voice option data class."""

    voice_id: str
    name: str
    description: Optional[str] = None
    preview_url: Optional[str] = None


@dataclass
class AgentConfig:
    """Agent configuration data class.

    Attributes:
        agent_id: Unique agent ID.
        name: Name of the agent.
        knowledge_ids: IDs of linked knowledge documents.
        voice_id: ID of the voice used.
        answer_style: Style of the agent's answers.
        elevenlabs_agent_id: ID of the agent in ElevenLabs.
        doctor_id: ID of the creating doctor.
        created_at: Creation timestamp.
    """

    agent_id: str
    name: str
    knowledge_ids: list[str]
    voice_id: str
    answer_style: str
    elevenlabs_agent_id: str
    doctor_id: str
    created_at: datetime


@dataclass
class PatientSession:
    """Patient session data class."""

    session_id: str
    patient_id: str
    agent_id: str
    signed_url: str
    created_at: datetime


@dataclass
class ConversationMessage:
    """Conversation message data class."""

    role: str  # 'patient' or 'agent'
    content: str
    timestamp: datetime
    audio_data: Optional[str] = None  # Base64 encoded audio for agent responses


@dataclass
class ConversationResponse:
    """Conversation response data class."""

    response_text: str
    audio_data: Optional[str]
    timestamp: datetime


@dataclass
class ConversationSummary:
    """Summary of a conversation log."""
    
    conversation_id: str
    patient_id: str
    agent_id: str
    agent_name: str
    requires_attention: bool
    main_concerns: List[str]
    total_messages: int
    answered_count: int
    unanswered_count: int
    duration_seconds: int
    created_at: datetime


@dataclass
class ConversationDetail(ConversationSummary):
    """Detailed view of a conversation log."""
    
    messages: List[ConversationMessage]
    answered_questions: List[str]
    unanswered_questions: List[str]
