"""Backend API client for Streamlit frontend.

This module provides the BackendAPIClient class for communicating
with the FastAPI backend without exposing API logic in the UI layer.
"""

import os
from datetime import datetime
from typing import List, Optional, AsyncGenerator
import json

import httpx
import streamlit as st

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
    PatientSession,
    PatientSession,
    ConversationResponse,
    ConversationSummary,
    ConversationDetail,
    ConversationMessage,
)

# Default configuration
DEFAULT_BACKEND_URL = "http://localhost:8000"
DEFAULT_TIMEOUT = 10.0  # seconds
LLM_TIMEOUT = 90.0  # Extended timeout for LLM generation (large documents can take 60+ seconds)


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
        # Use 'or' chain to handle None and empty string
        self.base_url = base_url or os.getenv("BACKEND_API_URL") or DEFAULT_BACKEND_URL
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

    def _get_llm_client(self) -> httpx.AsyncClient:
        """Create an async HTTP client with extended timeout for LLM operations.

        LLM operations can take much longer for large documents (60+ seconds),
        so we use a separate client with an extended timeout.

        Returns:
            Configured httpx.AsyncClient instance with LLM-appropriate timeout.
        """
        return httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(LLM_TIMEOUT),
        )

    def _parse_error_message(self, response: httpx.Response) -> str:
        """Parse error message from response.
        
        Args:
            response: The HTTP response.
            
        Returns:
            String error message, preferring 'detail' from JSON.
        """
        try:
            data = response.json()
            # If it's our structured error response, it has 'detail'
            if isinstance(data, dict) and "detail" in data:
                return data["detail"]
            return response.text
        except Exception:
            return response.text

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
                message=f"Health check failed: {self._parse_error_message(e.response)}",
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
                message=f"Failed to get dashboard stats: {self._parse_error_message(e.response)}",
                status_code=e.response.status_code,
            ) from e
        except (KeyError, ValueError) as e:
            raise APIError(
                message=f"Invalid response format: {e}",
                status_code=None,
            ) from e

    async def upload_knowledge(
        self, content: str, disease_name: str, tags: List[str]
    ) -> KnowledgeDocument:
        """Upload a knowledge document.
        
        Args:
            content: The document content.
            disease_name: Name of the disease.
            tags: List of document tags.

        Returns:
            KnowledgeDocument object.
        """
        try:
            payload = {
                "disease_name": disease_name,
                "tags": tags,
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
                    tags=data["tags"],
                    raw_content=data["raw_content"],
                    sync_status=data["sync_status"],
                    elevenlabs_document_id=data["elevenlabs_document_id"],
                    structured_sections=data.get("structured_sections"),
                    created_at=datetime.fromisoformat(data["created_at"]),
                    sync_error_message=data.get("sync_error_message"),
                    last_sync_attempt=datetime.fromisoformat(data["last_sync_attempt"]) if data.get("last_sync_attempt") else None,
                    sync_retry_count=data.get("sync_retry_count", 0),
                    modified_at=datetime.fromisoformat(data["modified_at"]) if data.get("modified_at") else None,
                )
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.TimeoutException as e:
            raise APITimeoutError(f"Upload timed out: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Upload failed: {self._parse_error_message(e.response)}",
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
                        tags=d["tags"],
                        raw_content=d["raw_content"],
                        sync_status=d["sync_status"],
                        elevenlabs_document_id=d["elevenlabs_document_id"],
                        structured_sections=d.get("structured_sections"),
                        created_at=datetime.fromisoformat(d["created_at"]),
                        sync_error_message=d.get("sync_error_message"),
                        last_sync_attempt=datetime.fromisoformat(d["last_sync_attempt"]) if d.get("last_sync_attempt") else None,
                        sync_retry_count=d.get("sync_retry_count", 0),
                        modified_at=datetime.fromisoformat(d["modified_at"]) if d.get("modified_at") else None,
                    )
                    for d in data["documents"]
                ]
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Failed to get documents: {self._parse_error_message(e.response)}",
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
                message=f"Delete failed: {self._parse_error_message(e.response)}",
                status_code=e.response.status_code,
            ) from e

    async def update_knowledge_document(
        self, knowledge_id: str, disease_name: Optional[str] = None, tags: Optional[List[str]] = None
    ) -> KnowledgeDocument:
        """Update a knowledge document.
        
        Args:
            knowledge_id: ID of the document.
            disease_name: New disease name (optional).
            tags: New document tags (optional).
            
        Returns:
            Updated KnowledgeDocument object.
        """
        try:
            payload = {}
            if disease_name is not None:
                payload["disease_name"] = disease_name
            if tags is not None:
                payload["tags"] = tags
                
            async with self._get_client() as client:
                response = await client.put(f"/api/knowledge/{knowledge_id}", json=payload)
                response.raise_for_status()
                data = response.json()
                return KnowledgeDocument(
                    knowledge_id=data["knowledge_id"],
                    doctor_id=data["doctor_id"],
                    disease_name=data["disease_name"],
                    tags=data["tags"],
                    raw_content=data["raw_content"],
                    sync_status=data["sync_status"],
                    elevenlabs_document_id=data["elevenlabs_document_id"],
                    structured_sections=data.get("structured_sections"),
                    created_at=datetime.fromisoformat(data["created_at"]),
                    sync_error_message=data.get("sync_error_message"),
                    last_sync_attempt=datetime.fromisoformat(data["last_sync_attempt"]) if data.get("last_sync_attempt") else None,
                    sync_retry_count=data.get("sync_retry_count", 0),
                    modified_at=datetime.fromisoformat(data["modified_at"]) if data.get("modified_at") else None,
                )
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Update failed: {self._parse_error_message(e.response)}",
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
                    tags=data["tags"],
                    raw_content=data["raw_content"],
                    sync_status=data["sync_status"],
                    elevenlabs_document_id=data["elevenlabs_document_id"],
                    structured_sections=data.get("structured_sections"),
                    created_at=datetime.fromisoformat(data["created_at"]),
                    sync_error_message=data.get("sync_error_message"),
                    last_sync_attempt=datetime.fromisoformat(data["last_sync_attempt"]) if data.get("last_sync_attempt") else None,
                    sync_retry_count=data.get("sync_retry_count", 0),
                    modified_at=datetime.fromisoformat(data["modified_at"]) if data.get("modified_at") else None,
                )
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Retry sync failed: {self._parse_error_message(e.response)}",
                status_code=e.response.status_code,
            ) from e

    async def generate_script(
        self, 
        knowledge_id: str,
        model_name: str = "gemini-2.5-flash",
        custom_prompt: Optional[str] = None
    ) -> ScriptResponse:
        """Generate a script from a knowledge document.

        Args:
            knowledge_id: ID of the knowledge document.
            model_name: Gemini model to use.
            custom_prompt: Optional custom prompt.

        Returns:
            ScriptResponse object.
        """
        try:
            payload = {
                "knowledge_id": knowledge_id,
                "model_name": model_name,
                "custom_prompt": custom_prompt
            }
            # Use extended timeout client for LLM operations
            async with self._get_llm_client() as client:
                response = await client.post("/api/audio/generate-script", json=payload)
                response.raise_for_status()
                data = response.json()
                return ScriptResponse(
                    script=data["script"],
                    knowledge_id=data["knowledge_id"],
                    generated_at=datetime.fromisoformat(data["generated_at"]),
                    model_used=data.get("model_used", "legacy"),
                    generation_error=data.get("generation_error")
                )
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.TimeoutException as e:
            raise APITimeoutError(
                f"Script generation timed out after {LLM_TIMEOUT}s. "
                "The document may be too large. Try using a smaller document or a faster model."
            ) from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Script generation failed: {self._parse_error_message(e.response)}",
                status_code=e.response.status_code,
            ) from e

    async def generate_script_stream(
        self,
        knowledge_id: str,
        model_name: str = "gemini-2.5-flash",
        custom_prompt: Optional[str] = None
    ) -> AsyncGenerator[dict, None]:
        """Stream script generation with Server-Sent Events.
        
        This method streams tokens as they are generated, keeping the
        connection alive and providing real-time feedback. This avoids
        timeout issues with large documents.
        
        Args:
            knowledge_id: ID of the knowledge document.
            model_name: Gemini model to use.
            custom_prompt: Optional custom prompt.
            
        Yields:
            dict events with type: 'token', 'complete', or 'error'
        """
        payload = {
            "knowledge_id": knowledge_id,
            "model_name": model_name,
            "custom_prompt": custom_prompt
        }
        
        try:
            async with self._get_llm_client() as client:
                async with client.stream(
                    "POST",
                    "/api/audio/generate-script-stream",
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        # Parse SSE format: "data: {...}"
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                yield data
                            except json.JSONDecodeError:
                                continue
        except httpx.ConnectError as e:
            yield {"type": "error", "message": f"Connection failed: {e}"}
        except httpx.TimeoutException as e:
            yield {"type": "error", "message": f"Request timed out: {e}"}
        except httpx.HTTPStatusError as e:
            yield {"type": "error", "message": f"HTTP error: {self._parse_error_message(e.response)}"}

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
                message=f"Audio generation failed: {self._parse_error_message(e.response)}",
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
                message=f"Failed to fetch audio history: {self._parse_error_message(e.response)}",
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
                message=f"Failed to fetch voices: {self._parse_error_message(e.response)}",
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
                message=f"Failed to create agent: {self._parse_error_message(e.response)}",
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
                message=f"Failed to get agents: {self._parse_error_message(e.response)}",
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
                message=f"Failed to delete agent: {self._parse_error_message(e.response)}",
                status_code=e.response.status_code,
            ) from e

    async def create_patient_session(self, patient_id: str, agent_id: str) -> PatientSession:
        """Create a new patient conversation session.

        Args:
            patient_id: Patient ID.
            agent_id: Valid Agent ID.

        Returns:
            PatientSession object with signed URL.
        """
        try:
            payload = {"patient_id": patient_id, "agent_id": agent_id}
            async with self._get_client() as client:
                response = await client.post("/api/patient/session", json=payload)
                response.raise_for_status()
                data = response.json()
                return PatientSession(
                    session_id=data["session_id"],
                    patient_id=data["patient_id"],
                    agent_id=data["agent_id"],
                    signed_url=data["signed_url"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                )
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Failed to create session: {self._parse_error_message(e.response)}",
                status_code=e.response.status_code,
            ) from e

    async def send_patient_message(
        self, session_id: str, message: str
    ) -> ConversationResponse:
        """Send a message to the agent.

        Args:
            session_id: Active session ID.
            message: Message content.

        Returns:
            ConversationResponse with text and audio.
        """
        try:
            payload = {"message": message}
            async with self._get_client() as client:
                response = await client.post(
                    f"/api/patient/session/{session_id}/message", json=payload
                )
                response.raise_for_status()
                data = response.json()
                return ConversationResponse(
                    response_text=data["response_text"],
                    audio_data=data.get("audio_data"),
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                )
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Failed to send message: {self._parse_error_message(e.response)}",
                status_code=e.response.status_code,
            ) from e

    async def end_patient_session(self, session_id: str) -> bool:
        """End a patient session.

        Args:
            session_id: Session ID to end.

        Returns:
            True if successful.
        """
        try:
            async with self._get_client() as client:
                response = await client.post(f"/api/patient/session/{session_id}/end")
                response.raise_for_status()
                return response.json()["success"]
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Failed to end session: {self._parse_error_message(e.response)}",
                status_code=e.response.status_code,
            ) from e

    async def get_conversation_logs(
        self,
        patient_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        requires_attention_only: bool = False,
    ) -> List[ConversationSummary]:
        """Get conversation logs with filters.

        Args:
            patient_id: Optional patient ID filter.
            start_date: Optional start date filter.
            end_date: Optional end date filter.
            requires_attention_only: Filter for attention required property.

        Returns:
            List of ConversationSummary objects.
        """
        try:
            params = {}
            if patient_id:
                params["patient_id"] = patient_id
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()
            if requires_attention_only:
                params["requires_attention_only"] = str(requires_attention_only).lower()

            async with self._get_client() as client:
                response = await client.get("/api/conversations", params=params)
                response.raise_for_status()
                data = response.json()
                
                # Based on Schema: response is ConversationLogsResponseSchema { conversations: [...], stats: ... }
                # We return the list of summaries for now, maybe in future we return the full response object
                # But requirement says "List of ConversationSummary"
                
                conversations = []
                for d in data["conversations"]:
                    conversations.append(ConversationSummary(
                        conversation_id=d["conversation_id"],
                        patient_id=d["patient_id"],
                        agent_id=d["agent_id"],
                        agent_name=d["agent_name"],
                        requires_attention=d["requires_attention"],
                        main_concerns=d["main_concerns"],
                        total_messages=d["total_messages"],
                        answered_count=d["answered_count"],
                        unanswered_count=d["unanswered_count"],
                        duration_seconds=d["duration_seconds"],
                        created_at=datetime.fromisoformat(d["created_at"])
                    ))
                return conversations
                
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Failed to get conversation logs: {self._parse_error_message(e.response)}",
                status_code=e.response.status_code,
            ) from e

    async def get_conversation_detail(self, conversation_id: str) -> ConversationDetail:
        """Get conversation details.

        Args:
            conversation_id: ID of the conversation.

        Returns:
            ConversationDetail object.
        """
        try:
            async with self._get_client() as client:
                response = await client.get(f"/api/conversations/{conversation_id}")
                response.raise_for_status()
                d = response.json()
                
                messages = [
                    ConversationMessage(
                        role=m["role"],
                        content=m["content"],
                        timestamp=datetime.fromisoformat(m["timestamp"]), 
                        # is_answered is not in ConversationMessage dataclass yet?
                        # backend Schema has it. frontend generic dataclass ConversationMessage 
                        # currently only has role, content, timestamp, audio_data.
                        # We might need to map it or extend frontend dataclass if needed.
                        # For now, map compatible fields.
                    ) for m in d["messages"]
                ]
                
                return ConversationDetail(
                    conversation_id=d["conversation_id"],
                    patient_id=d["patient_id"],
                    agent_id=d["agent_id"],
                    agent_name=d["agent_name"],
                    requires_attention=d["requires_attention"],
                    main_concerns=d["main_concerns"],
                    total_messages=d["total_messages"],
                    answered_count=d["answered_count"],
                    unanswered_count=d["unanswered_count"],
                    duration_seconds=d["duration_seconds"],
                    created_at=datetime.fromisoformat(d["created_at"]),
                    messages=messages,
                    answered_questions=d["answered_questions"],
                    unanswered_questions=d["unanswered_questions"]
                )
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Failed to get conversation detail: {self._parse_error_message(e.response)}",
                status_code=e.response.status_code,
            ) from e

    async def get_conversation_statistics(self) -> dict:
        """Get conversation statistics.

        Returns:
             Dictionary with conversation statistics.
        """
        try:
            async with self._get_client() as client:
                response = await client.get("/api/conversations/statistics")
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to backend: {e}") from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"Failed to get statistics: {self._parse_error_message(e.response)}",
                status_code=e.response.status_code,
            ) from e


# Convenience function for getting a client instance
def get_backend_client() -> BackendAPIClient:
    """Get a configured backend API client.

    Returns:
        BackendAPIClient instance with default configuration.
    """
    return BackendAPIClient()
