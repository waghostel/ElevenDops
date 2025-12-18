"""Data models for Streamlit frontend services."""

from dataclasses import dataclass
from datetime import datetime


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
