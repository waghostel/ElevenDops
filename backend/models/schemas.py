"""Pydantic models and schemas for ElevenDops backend API."""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Literal

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
    retryable: bool = Field(default=False, description="Whether the operation is retryable")


# Default document tags for knowledge documents
DEFAULT_DOCUMENT_TAGS = [
    "before_visit",
    "diagnosis",
    "procedure",
    "post_care",
    "medication",
    "warning_signs",
    "faq",
]


class SyncStatus(str, Enum):
    """Synchronization status with ElevenLabs."""

    PENDING = "pending"
    SYNCING = "syncing"
    COMPLETED = "completed"
    FAILED = "failed"


class KnowledgeDocumentCreate(BaseModel):
    """Request model for creating a knowledge document."""

    disease_name: str = Field(..., min_length=1, max_length=100, description="Name of the disease")
    tags: List[str] = Field(default_factory=lambda: ["faq"], description="List of document tags")
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

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate that tags list is not empty."""
        if not v:
            raise ValueError("At least one tag is required")
        return v


class KnowledgeDocumentUpdate(BaseModel):
    """Request model for updating a knowledge document."""

    disease_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the disease")
    tags: Optional[List[str]] = Field(None, description="List of document tags")
    
    @field_validator("disease_name")
    @classmethod
    def validate_disease_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate that disease name is not empty or whitespace only."""
        if v is not None and not v.strip():
            raise ValueError("Disease name cannot be empty or whitespace only")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate that tags list is not empty if provided."""
        if v is not None and not v:
            raise ValueError("Tags list cannot be empty if provided")
        return v


class KnowledgeDocumentResponse(BaseModel):
    """Response model for knowledge document."""

    knowledge_id: str = Field(..., description="Unique document ID")
    doctor_id: str = Field(..., description="ID of the uploading doctor")
    disease_name: str = Field(..., description="Name of the disease")
    tags: List[str] = Field(..., description="List of document tags")
    raw_content: str = Field(..., description="Content of the document")
    sync_status: SyncStatus = Field(..., description="Sync status with ElevenLabs")
    elevenlabs_document_id: Optional[str] = Field(None, description="Document ID in ElevenLabs")
    structured_sections: Optional[dict] = Field(
        None, description="Structured sections of the document"
    )
    sync_error_message: Optional[str] = Field(None, description="Error message if sync failed")
    last_sync_attempt: Optional[datetime] = Field(None, description="Timestamp of last sync attempt")
    sync_retry_count: int = Field(default=0, description="Number of sync retry attempts")
    created_at: datetime = Field(..., description="Creation timestamp")
    modified_at: Optional[datetime] = Field(None, description="Last modification timestamp")


class KnowledgeDocumentListResponse(BaseModel):
    """Response model for listing knowledge documents."""

    documents: List[KnowledgeDocumentResponse] = Field(..., description="List of documents")
    total_count: int = Field(..., ge=0, description="Total number of documents")


class ScriptGenerateRequest(BaseModel):
    """Request model for script generation."""

    knowledge_id: str = Field(..., description="ID of the knowledge document")
    model_name: str = Field(default="gemini-2.5-flash", description="Gemini model to use")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt for generation")
    template_config: Optional["TemplateConfig"] = Field(
        None, description="Template configuration for prompt building"
    )


class TemplateConfig(BaseModel):
    """Configuration for prompt template selection."""

    template_ids: List[str] = Field(
        default=["pre_surgery"],
        description="List of template IDs in display order"
    )
    quick_instructions: Optional[str] = Field(
        None,
        max_length=2000,
        description="Additional instructions to inject into the prompt"
    )
    system_prompt_override: Optional[str] = Field(
        None,
        description="Custom base system prompt to use instead of default"
    )
    preferred_languages: List[str] = Field(
        default_factory=list,
        description="Preferred output languages for transcript generation (e.g., ['zh-TW', 'en'])"
    )
    speaker1_languages: List[str] = Field(
        default_factory=list,
        description="Languages for Speaker 1 (Doctor/Educator role)"
    )
    speaker2_languages: List[str] = Field(
        default_factory=list,
        description="Languages for Speaker 2 (Patient/Learner role)"
    )
    target_duration_minutes: Optional[int] = Field(
        default=None,
        description="Target speech duration in minutes (3, 5, 10, or 15)"
    )
    is_multi_speaker: bool = Field(
        default=True,
        description="Whether to use multi-speaker (Doctor-Patient) or single-speaker (Solo Doctor) format"
    )

    @field_validator("target_duration_minutes")
    @classmethod
    def validate_duration(cls, v: Optional[int]) -> Optional[int]:
        """Validate that duration is one of the allowed values."""
        if v is not None and v not in {3, 5, 10, 15}:
            raise ValueError("Duration must be 3, 5, 10, or 15 minutes")
        return v

    @field_validator("preferred_languages", "speaker1_languages", "speaker2_languages")
    @classmethod
    def validate_language_lists(cls, v: List[str]) -> List[str]:
        if not v:
            return v
        
        # All languages supported by ElevenLabs voices
        # Includes regional variants for Chinese (zh-TW/zh-CN) and Portuguese (pt-BR/pt-PT)
        valid_languages = {
            "ar", "bg", "cs", "da", "de", "el", "en", "es", "fi", "fil",
            "fr", "hi", "hr", "hu", "id", "it", "ja", "ko", "ms", "nl",
            "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sv", "ta", "tr", "uk", "zh",
            "zh-TW", "zh-CN"
        }
        for lang in v:
            if lang not in valid_languages:
                raise ValueError(
                    f"Invalid language code '{lang}'. Must be a valid ElevenLabs language code."
                )
        return v


class TemplateInfoResponse(BaseModel):
    """Template information response for API."""

    template_id: str = Field(..., description="Unique template identifier")
    display_name: str = Field(..., description="Human-readable display name")
    description: str = Field(..., description="Brief description of the template")
    category: str = Field(..., description="Template category (base, content_type, custom)")
    preview: str = Field(default="", description="First 200 characters of template content")


class CustomTemplateCreate(BaseModel):
    """Schema for creating a custom template."""

    display_name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)
    content: str = Field(..., min_length=10)


class CustomTemplateUpdate(BaseModel):
    """Schema for updating a custom template."""

    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = Field(None, min_length=10)


class CustomTemplateResponse(TemplateInfoResponse):
    """Response schema for custom templates including full content."""
    
    content: str = Field(..., description="Full template content")
    created_by: Optional[str] = Field(None, description="User ID who created the template")
    created_at: datetime = Field(..., description="Creation timestamp")
    category: str = Field(..., description="Template category: base, content_type, or custom")
    preview: str = Field(default="", description="First 200 chars of template content")


class PromptPreviewRequest(BaseModel):
    """Request body for prompt preview endpoint."""

    template_ids: List[str] = Field(..., description="List of template IDs in display order")
    quick_instructions: Optional[str] = Field(None, description="Additional instructions")


class ScriptGenerateResponse(BaseModel):
    """Response model for script generation."""

    script: str = Field(..., description="Generated script text")
    knowledge_id: str = Field(..., description="Source document ID")
    model_used: str = Field(default="legacy", description="Model used for generation")
    generated_at: datetime = Field(..., description="Generation timestamp")
    generation_error: Optional[str] = Field(
        None, description="Error message if AI generation failed and fallback was used"
    )


class AudioGenerateRequest(BaseModel):
    """Request model for audio generation."""

    knowledge_id: str = Field(..., description="Source document ID")
    script: str = Field(..., min_length=1, max_length=50000, description="Script to convert")
    voice_id: str = Field(..., description="ElevenLabs voice ID")
    doctor_id: str = Field(default="default_doctor", description="ID of the doctor generating audio")


class AudioGenerateResponse(BaseModel):
    """Response model for audio generation."""

    audio_id: str = Field(..., description="Unique audio file ID")
    audio_url: str = Field(..., description="URL to access the audio")
    knowledge_id: str = Field(..., description="Source document ID")
    voice_id: str = Field(..., description="Voice used for generation")
    duration_seconds: Optional[float] = Field(None, description="Audio duration")
    script: str = Field(..., description="Script used for generation")
    created_at: datetime = Field(..., description="Creation timestamp")
    doctor_id: str = Field(default="default_doctor", description="ID of the doctor who generated audio")


class AudioMetadata(BaseModel):
    """Metadata for an audio file."""

    audio_id: str
    audio_url: str
    knowledge_id: str
    voice_id: str
    duration_seconds: Optional[float]
    script: str
    created_at: datetime
    doctor_id: str = Field(default="default_doctor", description="ID of the doctor who generated audio")


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
    languages: List[str] = Field(default_factory=lambda: ["en"], description="Language codes for agent (first is primary)")
    doctor_id: str = Field(default="default_doctor", description="ID of the creating doctor")
    system_prompt_override: Optional[str] = Field(None, description="Custom system prompt to use instead of style-based default")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that agent name is not empty or whitespace only."""
        if not v.strip():
            raise ValueError("Agent name cannot be empty or whitespace only")
        return v
    
    @field_validator("languages")
    @classmethod
    def validate_languages(cls, v: List[str]) -> List[str]:
        """Validate that language codes are supported."""
        if not v:
            raise ValueError("At least one language is required")
        # Common ISO 639-1 codes supported by ElevenLabs
        supported_languages = {
            "zh", "en", "es", "fr", "de", "hi", "it", "ja", "ko", "nl", "pl", "pt", "ru", "tr",
            "ar", "cs", "da", "fi", "el", "he", "hu", "id", "ms", "no", "ro", "sk", "sv", "th", "uk", "vi", "zh-TW"
        }
        for lang in v:
            if lang not in supported_languages:
                raise ValueError(
                    f"Unsupported language code '{lang}'. Must be a valid ISO 639-1 code supported by ElevenLabs."
                )
        return v


class AgentResponse(BaseModel):
    """Response model for agent details."""

    agent_id: str = Field(..., description="Unique agent ID")
    name: str = Field(..., description="Name of the agent")
    knowledge_ids: List[str] = Field(..., description="IDs of linked knowledge documents")
    voice_id: str = Field(..., description="ID of the voice used")
    answer_style: AnswerStyle = Field(..., description="Style of the agent's answers")
    languages: List[str] = Field(default_factory=lambda: ["zh"], description="Language codes for agent (first is primary)")
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


class ConversationMessageSchema(BaseModel):
    """Schema for a conversation message."""

    role: Literal["patient", "agent"]
    content: str
    timestamp: datetime
    is_answered: Optional[bool] = None
    audio_data: Optional[str] = Field(None, description="Base64 encoded audio data (agent only)")


class ConversationSummarySchema(BaseModel):
    """Schema for conversation summary."""

    conversation_id: str
    patient_id: str
    agent_id: str
    agent_name: str
    requires_attention: bool = False
    main_concerns: List[str] = Field(default_factory=list)
    total_messages: int = 0
    answered_count: int = 0
    unanswered_count: int = 0
    duration_seconds: int = 0
    created_at: datetime


class ConversationDetailSchema(BaseModel):
    """Schema for detailed conversation view."""

    conversation_id: str
    patient_id: str
    agent_id: str
    agent_name: str
    requires_attention: bool = False
    main_concerns: List[str] = Field(default_factory=list)
    messages: List[ConversationMessageSchema] = Field(default_factory=list)
    answered_questions: List[str] = Field(default_factory=list)
    unanswered_questions: List[str] = Field(default_factory=list)
    duration_seconds: int = 0
    created_at: datetime


class ConversationLogsResponseSchema(BaseModel):
    """Schema for conversation logs response."""

    conversations: List[ConversationSummarySchema]
    total_count: int
    attention_required_count: int
    total_answered: int
    total_unanswered: int


class ConversationLogsQueryParams(BaseModel):
    """Query parameters for filtering conversation logs."""

    patient_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    requires_attention_only: bool = False
