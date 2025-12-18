"""Pydantic models and schemas for ElevenDops backend API."""

from datetime import datetime

from pydantic import BaseModel, Field


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
