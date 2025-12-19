"""Backend API client for Streamlit frontend.

This module provides the BackendAPIClient class for communicating
with the FastAPI backend without exposing API logic in the UI layer.
"""

import os
from datetime import datetime
from typing import List, Optional

import httpx

from streamlit_app.services.exceptions import (
    APIConnectionError,
    APIError,
    APITimeoutError,
)
from streamlit_app.services.models import (
    DashboardStats,
    KnowledgeDocument,
    ScriptResponse,
    AudioResponse,
    VoiceOption,
    AgentConfig,
)

# Default configuration
DEFAULT_BACKEND_URL = "http://localhost:8000"
DEFAULT_TIMEOUT = 10.0  # seconds


class BackendAPIClient:
    """Client for communicating with the ElevenDops backend API.

    This client handles all HTTP communication with the FastAPI backend,
    including error handling and response parsing.

    Attributes:
        base_url: The base URL of the backend API.
        timeout: Request timeout in seconds.
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the backend API client.

        Args:
            base_url: Backend API base URL. If not provided, uses
                BACKEND_API_URL environment variable or localhost default.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url or os.getenv("BACKEND_API_URL", DEFAULT_BACKEND_URL)
        self.timeout = timeout

    def _get_client(self) -> httpx.AsyncClient:
        """Create an async HTTP client with configured settings.

        Returns:
            Configured httpx.AsyncClient instance.
        """
        return httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout),
        )

    async def health_check(self) -> dict:
        """Check the health of the backend API.

        Returns:
            Dict containing status, timestamp, and version.

        Raises:
            APIConnectionError: If connection to backend fails.
            APITimeoutError: If request times out.
            APIError: For other API errors.
        """
        try:
            async with self._get_client() as client:
                response = await client.get("/api/health")
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.TimeoutException as e:
            raise APITimeoutError(f"Health check timed out: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Health check failed: {e.response.text}",
                status_code=e.response.status_code,
            ) from e

    async def get_dashboard_stats(self) -> DashboardStats:
        """Get dashboard statistics from the backend.

        Returns:
            DashboardStats dataclass with current statistics.

        Raises:
            APIConnectionError: If connection to backend fails.
            APITimeoutError: If request times out.
            APIError: For other API errors.
        """
        try:
            async with self._get_client() as client:
                response = await client.get("/api/dashboard/stats")
                response.raise_for_status()
                data = response.json()
                return DashboardStats(
                    document_count=data["document_count"],
                    agent_count=data["agent_count"],
                    audio_count=data["audio_count"],
                    last_activity=datetime.fromisoformat(data["last_activity"]),
                )
        except httpx.ConnectError as e:
            raise APIConnectionError(
                f"Failed to connect to backend: {e}"
            ) from e
        except httpx.TimeoutException as e:
            raise APITimeoutError(
                f"Dashboard stats request timed out: {e}"
            ) from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Failed to get dashboard stats: {e.response.text}",
                status_code=e.response.status_code,
            ) from e
        except (KeyError, ValueError) as e:
            raise APIError(
                message=f"Invalid response format: {e}",
                status_code=None,
            ) from e

    async def upload_knowledge(
        self, content: str, disease_name: str, document_type: str
    ) -> KnowledgeDocument:
        """Upload a knowledge document.
        
        Args:
            content: The document content.
            disease_name: Name of the disease.
            document_type: Type of document.

        Returns:
            KnowledgeDocument object.
        """
        try:
            payload = {
                "disease_name": disease_name,
                "document_type": document_type,
                "raw_content": content,
            }
            async with self._get_client() as client:
                response = await client.post("/api/knowledge", json=payload)
                response.raise_for_status()
                data = response.json()
                return KnowledgeDocument(
                    knowledge_id=data["knowledge_id"],
                    doctor_id=data["doctor_id"],
                    disease_name=data["disease_name"],
                    document_type=data["document_type"],
                    raw_content=data["raw_content"],
                    sync_status=data["sync_status"],
                    elevenlabs_document_id=data["elevenlabs_document_id"],
                    structured_sections=data.get("structured_sections"),
                    created_at=datetime.fromisoformat(data["created_at"]),
                )
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.TimeoutException as e:
            raise APITimeoutError(f"Upload timed out: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Upload failed: {e.response.text}",
                status_code=e.response.status_code,
            ) from e
    
    async def get_knowledge_documents(self) -> List[KnowledgeDocument]:
        """Get all knowledge documents.

        Returns:
            List of KnowledgeDocument objects.
        """
        try:
            async with self._get_client() as client:
                response = await client.get("/api/knowledge")
                response.raise_for_status()
                data = response.json()
                return [
                    KnowledgeDocument(
                        knowledge_id=d["knowledge_id"],
                        doctor_id=d["doctor_id"],
                        disease_name=d["disease_name"],
                        document_type=d["document_type"],
                        raw_content=d["raw_content"],
                        sync_status=d["sync_status"],
                        elevenlabs_document_id=d["elevenlabs_document_id"],
                        structured_sections=d.get("structured_sections"),
                        created_at=datetime.fromisoformat(d["created_at"]),
                    )
                    for d in data["documents"]
                ]
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Failed to get documents: {e.response.text}",
                status_code=e.response.status_code,
            ) from e

    async def delete_knowledge_document(self, knowledge_id: str) -> bool:
        """Delete a knowledge document.

        Returns:
            True if successful.
        """
        try:
            async with self._get_client() as client:
                response = await client.delete(f"/api/knowledge/{knowledge_id}")
                response.raise_for_status()
                return True
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Delete failed: {e.response.text}",
                status_code=e.response.status_code,
            ) from e

    async def retry_knowledge_sync(self, knowledge_id: str) -> KnowledgeDocument:
        """Retry syncing a knowledge document.

        Returns:
            Updated KnowledgeDocument object.
        """
        try:
            async with self._get_client() as client:
                response = await client.post(f"/api/knowledge/{knowledge_id}/retry-sync")
                response.raise_for_status()
                data = response.json()
                return KnowledgeDocument(
                    knowledge_id=data["knowledge_id"],
                    doctor_id=data["doctor_id"],
                    disease_name=data["disease_name"],
                    document_type=data["document_type"],
                    raw_content=data["raw_content"],
                    sync_status=data["sync_status"],
                    elevenlabs_document_id=data["elevenlabs_document_id"],
                    structured_sections=data.get("structured_sections"),
                    created_at=datetime.fromisoformat(data["created_at"]),
                )
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Retry sync failed: {e.response.text}",
                status_code=e.response.status_code,
            ) from e

    async def generate_script(self, knowledge_id: str) -> ScriptResponse:
        """Generate a script from a knowledge document.

        Args:
            knowledge_id: ID of the knowledge document.

        Returns:
            ScriptResponse object.
        """
        try:
            payload = {"knowledge_id": knowledge_id}
            async with self._get_client() as client:
                response = await client.post("/api/audio/generate-script", json=payload)
                response.raise_for_status()
                data = response.json()
                return ScriptResponse(
                    script=data["script"],
                    knowledge_id=data["knowledge_id"],
                    generated_at=datetime.fromisoformat(data["generated_at"]),
                )
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Script generation failed: {e.response.text}",
                status_code=e.response.status_code,
            ) from e

    async def generate_audio(self, knowledge_id: str, script: str, voice_id: str) -> AudioResponse:
        """Generate audio from a script.

        Args:
            knowledge_id: Source document ID.
            script: The script content.
            voice_id: The ElevenLabs voice ID.

        Returns:
            AudioResponse object.
        """
        try:
            payload = {
                "knowledge_id": knowledge_id,
                "script": script,
                "voice_id": voice_id,
            }
            async with self._get_client() as client:
                response = await client.post("/api/audio/generate", json=payload)
                response.raise_for_status()
                data = response.json()
                return AudioResponse(
                    audio_id=data["audio_id"],
                    audio_url=data["audio_url"],
                    knowledge_id=data["knowledge_id"],
                    voice_id=data["voice_id"],
                    duration_seconds=data.get("duration_seconds"),
                    script=data["script"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                )
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Audio generation failed: {e.response.text}",
                status_code=e.response.status_code,
            ) from e

    async def get_audio_files(self, knowledge_id: str) -> List[AudioResponse]:
        """Get audio files for a knowledge document.

        Args:
            knowledge_id: ID of the knowledge document.

        Returns:
            List of AudioResponse objects.
        """
        try:
            async with self._get_client() as client:
                response = await client.get(f"/api/audio/{knowledge_id}")
                response.raise_for_status()
                data = response.json()
                return [
                    AudioResponse(
                        audio_id=d["audio_id"],
                        audio_url=d["audio_url"],
                        knowledge_id=d["knowledge_id"],
                        voice_id=d["voice_id"],
                        duration_seconds=d.get("duration_seconds"),
                        script=d["script"],
                        created_at=datetime.fromisoformat(d["created_at"]),
                    )
                    for d in data["audio_files"]
                ]
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Failed to fetch audio history: {e.response.text}",
                status_code=e.response.status_code,
            ) from e

    async def get_available_voices(self) -> List[VoiceOption]:
        """Get available voices.

        Returns:
            List of VoiceOption objects.
        """
        try:
            async with self._get_client() as client:
                response = await client.get("/api/audio/voices/list")
                response.raise_for_status()
                data = response.json()
                return [
                    VoiceOption(
                        voice_id=v["voice_id"],
                        name=v["name"],
                        description=v.get("description"),
                        preview_url=v.get("preview_url"),
                    )
                    for v in data
                ]
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Failed to fetch voices: {e.response.text}",
                status_code=e.response.status_code,
            ) from e

    async def create_agent(
        self,
        name: str,
        knowledge_ids: List[str],
        voice_id: str,
        answer_style: str,
        doctor_id: str = "default_doctor",
    ) -> AgentConfig:
        """Create a new agent.

        Args:
            name: Agent name.
            knowledge_ids: List of linked knowledge document IDs.
            voice_id: Voice ID.
            answer_style: Answer style.
            doctor_id: Doctor ID.

        Returns:
            AgentConfig object.
        """
        try:
            payload = {
                "name": name,
                "knowledge_ids": knowledge_ids,
                "voice_id": voice_id,
                "answer_style": answer_style,
                "doctor_id": doctor_id,
            }
            async with self._get_client() as client:
                response = await client.post("/api/agent", json=payload)
                response.raise_for_status()
                data = response.json()
                return AgentConfig(
                    agent_id=data["agent_id"],
                    name=data["name"],
                    knowledge_ids=data["knowledge_ids"],
                    voice_id=data["voice_id"],
                    answer_style=data["answer_style"],
                    elevenlabs_agent_id=data["elevenlabs_agent_id"],
                    doctor_id=data["doctor_id"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                )
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Failed to create agent: {e.response.text}",
                status_code=e.response.status_code,
            ) from e

    async def get_agents(self) -> List[AgentConfig]:
        """Get all agents.

        Returns:
            List of AgentConfig objects.
        """
        try:
            async with self._get_client() as client:
                response = await client.get("/api/agent")
                response.raise_for_status()
                data = response.json()
                return [
                    AgentConfig(
                        agent_id=d["agent_id"],
                        name=d["name"],
                        knowledge_ids=d["knowledge_ids"],
                        voice_id=d["voice_id"],
                        answer_style=d["answer_style"],
                        elevenlabs_agent_id=d["elevenlabs_agent_id"],
                        doctor_id=d["doctor_id"],
                        created_at=datetime.fromisoformat(d["created_at"]),
                    )
                    for d in data["agents"]
                ]
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Failed to get agents: {e.response.text}",
                status_code=e.response.status_code,
            ) from e

    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent.

        Args:
            agent_id: ID of the agent to delete.

        Returns:
            True if successful.
        """
        try:
            async with self._get_client() as client:
                response = await client.delete(f"/api/agent/{agent_id}")
                response.raise_for_status()
                return True
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Failed to delete agent: {e.response.text}",
                status_code=e.response.status_code,
            ) from e


# Convenience function for getting a client instance
def get_backend_client() -> BackendAPIClient:
    """Get a configured backend API client.

    Returns:
        BackendAPIClient instance with default configuration.
    """
    return BackendAPIClient()
