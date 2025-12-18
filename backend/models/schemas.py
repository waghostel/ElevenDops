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
