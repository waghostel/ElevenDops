"""Data models for Streamlit frontend services."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict


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
