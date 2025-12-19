"""Pydantic models and schemas for ElevenDops backend API."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Health status (e.g., 'healthy')")
    timestamp: datetime = Field(..., description="Current server timestamp")
    version: str = Field(..., description="API version")


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response model."""

    document_count: int = Field(..., ge=0, description="Number of uploaded documents")
    agent_count: int = Field(..., ge=0, description="Number of active agents")
    audio_count: int = Field(..., ge=0, description="Number of generated audio files")
    last_activity: datetime = Field(..., description="Timestamp of last activity")


class ErrorResponse(BaseModel):
    """Error response model for API errors."""

    detail: str = Field(..., description="Error message detail")
    error_code: str = Field(..., description="Error code identifier")


class DocumentType(str, Enum):
    """Type of knowledge document."""

    FAQ = "faq"
    POST_CARE = "post_care"
    PRECAUTIONS = "precautions"


class SyncStatus(str, Enum):
    """Synchronization status with ElevenLabs."""

    PENDING = "pending"
    SYNCING = "syncing"
    COMPLETED = "completed"
    FAILED = "failed"


class KnowledgeDocumentCreate(BaseModel):
    """Request model for creating a knowledge document."""

    disease_name: str = Field(..., min_length=1, max_length=100, description="Name of the disease")
    document_type: DocumentType = Field(..., description="Type of the document")
    raw_content: str = Field(
        ..., min_length=1, max_length=300000, description="Content of the document (~300KB limit)"
    )
    doctor_id: str = Field(default="default_doctor", description="ID of the uploading doctor")

    @field_validator("disease_name")
    @classmethod
    def validate_disease_name(cls, v: str) -> str:
        """Validate that disease name is not empty or whitespace only."""
        if not v.strip():
            raise ValueError("Disease name cannot be empty or whitespace only")
        return v


class KnowledgeDocumentResponse(BaseModel):
    """Response model for knowledge document."""

    knowledge_id: str = Field(..., description="Unique document ID")
    doctor_id: str = Field(..., description="ID of the uploading doctor")
    disease_name: str = Field(..., description="Name of the disease")
    document_type: DocumentType = Field(..., description="Type of the document")
    raw_content: str = Field(..., description="Content of the document")
    sync_status: SyncStatus = Field(..., description="Sync status with ElevenLabs")
    elevenlabs_document_id: Optional[str] = Field(None, description="Document ID in ElevenLabs")
    structured_sections: Optional[dict] = Field(
        None, description="Structured sections of the document"
    )
    created_at: datetime = Field(..., description="Creation timestamp")


class KnowledgeDocumentListResponse(BaseModel):
    """Response model for listing knowledge documents."""

    documents: List[KnowledgeDocumentResponse] = Field(..., description="List of documents")
    total_count: int = Field(..., ge=0, description="Total number of documents")


class ScriptGenerateRequest(BaseModel):
    """Request model for script generation."""

    knowledge_id: str = Field(..., description="ID of the knowledge document")


class ScriptGenerateResponse(BaseModel):
    """Response model for script generation."""

    script: str = Field(..., description="Generated script text")
    knowledge_id: str = Field(..., description="Source document ID")
    generated_at: datetime = Field(..., description="Generation timestamp")


class AudioGenerateRequest(BaseModel):
    """Request model for audio generation."""

    knowledge_id: str = Field(..., description="Source document ID")
    script: str = Field(..., min_length=1, max_length=50000, description="Script to convert")
    voice_id: str = Field(..., description="ElevenLabs voice ID")


class AudioGenerateResponse(BaseModel):
    """Response model for audio generation."""

    audio_id: str = Field(..., description="Unique audio file ID")
    audio_url: str = Field(..., description="URL to access the audio")
    knowledge_id: str = Field(..., description="Source document ID")
    voice_id: str = Field(..., description="Voice used for generation")
    duration_seconds: Optional[float] = Field(None, description="Audio duration")
    script: str = Field(..., description="Script used for generation")
    created_at: datetime = Field(..., description="Creation timestamp")


class AudioMetadata(BaseModel):
    """Metadata for an audio file."""

    audio_id: str
    audio_url: str
    knowledge_id: str
    voice_id: str
    duration_seconds: Optional[float]
    script: str
    created_at: datetime


class AudioListResponse(BaseModel):
    """Response model for listing audio files."""

    audio_files: List[AudioMetadata]
    total_count: int


class VoiceOption(BaseModel):
    """Model for a voice option."""

    voice_id: str = Field(..., description="ElevenLabs voice ID")
    name: str = Field(..., description="Display name")
    description: Optional[str] = Field(None, description="Voice description")
    preview_url: Optional[str] = Field(None, description="Voice preview audio URL")


class AnswerStyle(str, Enum):
    """Style of the agent's answers."""

    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    EDUCATIONAL = "educational"


class AgentCreateRequest(BaseModel):
    """Request model for creating an agent."""

    name: str = Field(..., min_length=1, max_length=100, description="Name of the agent")
    knowledge_ids: List[str] = Field(default_factory=list, description="IDs of linked knowledge documents")
    voice_id: str = Field(..., description="ID of the voice to use")
    answer_style: AnswerStyle = Field(..., description="Style of the agent's answers")
    doctor_id: str = Field(default="default_doctor", description="ID of the creating doctor")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that agent name is not empty or whitespace only."""
        if not v.strip():
            raise ValueError("Agent name cannot be empty or whitespace only")
        return v


class AgentResponse(BaseModel):
    """Response model for agent details."""

    agent_id: str = Field(..., description="Unique agent ID")
    name: str = Field(..., description="Name of the agent")
    knowledge_ids: List[str] = Field(..., description="IDs of linked knowledge documents")
    voice_id: str = Field(..., description="ID of the voice used")
    answer_style: AnswerStyle = Field(..., description="Style of the agent's answers")
    elevenlabs_agent_id: str = Field(..., description="ID of the agent in ElevenLabs")
    doctor_id: str = Field(..., description="ID of the creating doctor")
    created_at: datetime = Field(..., description="Creation timestamp")


class AgentListResponse(BaseModel):
    """Response model for listing agents."""

    agents: List[AgentResponse] = Field(..., description="List of agents")
    total_count: int = Field(..., ge=0, description="Total number of agents")


class PatientSessionCreate(BaseModel):
    """Request to create a patient session."""

    patient_id: str = Field(..., pattern=r'^[a-zA-Z0-9]+$', description="Patient ID (alphanumeric only)")
    agent_id: str = Field(..., description="ID of the agent to converse with")


class PatientSessionResponse(BaseModel):
    """Response after creating a session."""

    session_id: str = Field(..., description="Unique session ID")
    patient_id: str = Field(..., description="Patient ID")
    agent_id: str = Field(..., description="Agent ID")
    signed_url: str = Field(..., description="Signed URL for WebSocket connection")
    created_at: datetime = Field(..., description="Creation timestamp")


class PatientMessageRequest(BaseModel):
    """Request to send a message."""

    message: str = Field(..., min_length=1, max_length=2000, description="Message content")


class PatientMessageResponse(BaseModel):
    """Response after sending a message."""

    response_text: str = Field(..., description="Text response from agent")
    audio_data: Optional[str] = Field(None, description="Base64 encoded audio data")
    timestamp: datetime = Field(..., description="Response timestamp")


class SessionEndResponse(BaseModel):
    """Response after ending a session."""

    success: bool = Field(..., description="Whether the session ended successfully")
    conversation_summary: Optional[dict] = Field(None, description="Summary of the conversation")
