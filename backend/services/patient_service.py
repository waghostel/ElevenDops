"""Service for managing patient conversation sessions."""

import logging
import uuid
from datetime import datetime
from typing import Optional

from backend.models.schemas import (
    PatientSessionCreate,
    PatientSessionResponse,
    PatientMessageResponse,
    SessionEndResponse,
)
from backend.services.data_service import get_data_service
from backend.services.elevenlabs_service import get_elevenlabs_service, ElevenLabsServiceError
from backend.services.data_service import DataServiceProtocol

class PatientService:
    """Service for managing patient conversation sessions."""

    def __init__(
        self,
        data_service: Optional[DataServiceProtocol] = None,
        elevenlabs_service=None
    ):
        """Initialize the service.
        
        Args:
            data_service: Optional data service injection for testing.
            elevenlabs_service: Optional ElevenLabs service injection.
        """
        self.data_service = data_service or get_data_service()
        self.elevenlabs_service = elevenlabs_service or get_elevenlabs_service()

    async def create_session(self, request: PatientSessionCreate) -> PatientSessionResponse:
        """Create a new patient conversation session.

        Args:
            request: The session creation request.

        Returns:
            PatientSessionResponse: The created session details.
        """
        session_id = str(uuid.uuid4())
        
        # Get signed URL from ElevenLabs
        try:
            signed_url = self.elevenlabs_service.get_signed_url(request.agent_id)
        except ElevenLabsServiceError as e:
            logging.error(f"Failed to get signed URL for session {session_id}: {e}")
            # Depending on requirements, we might fail or return a session with empty URL
            # but Requirement 4.1 implies successful session needs it.
            # We re-raise or handle. Let's re-raise to bubble up to API.
            raise e

        # Create session object
        session = PatientSessionResponse(
            session_id=session_id,
            patient_id=request.patient_id,
            agent_id=request.agent_id,
            signed_url=signed_url,
            created_at=datetime.now()
        )

        # Persist session
        await self.data_service.create_patient_session(session)
        
        return session

    async def send_message(
        self, session_id: str, message: str
    ) -> PatientMessageResponse:
        """Send a message to the agent in the active session.

        Args:
            session_id: The session ID.
            message: The patient's message.

        Returns:
            PatientMessageResponse: The agent's response.
            
        Raises:
            ValueError: If session not found.
        """
        # Verify session exists
        session = await self.data_service.get_patient_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Send to ElevenLabs (or simulated agent)
        response_text, audio_bytes = self.elevenlabs_service.send_text_message(
            session.agent_id, message
        )
        
        # Convert audio bytes to base64 if needed by Schema?
        # Schema says `audio_data: Optional[str] = Field(None, description="Base64 encoded audio data")`
        # simulate base64 encoding if it's bytes
        import base64
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8') if audio_bytes else None

        # Log conversation (Feature for future Task: logging history to DB)
        # For now, just return the response
        
        return PatientMessageResponse(
            response_text=response_text,
            audio_data=audio_b64,
            timestamp=datetime.now()
        )

    async def end_session(self, session_id: str) -> SessionEndResponse:
        """End a patient session.

        Args:
            session_id: The session ID.

        Returns:
            SessionEndResponse: The end session result.
        """
        session = await self.data_service.get_patient_session(session_id)
        if not session:
             # Idempotent success or error? 
             # Let's say false success for now or error.
             return SessionEndResponse(success=False, conversation_summary={"error": "Session not found"})

        # Perform any cleanup or final stats update
        # await self.data_service.update_patient_session(session_id, ended=True)
        
        return SessionEndResponse(
            success=True,
            conversation_summary={
                "session_id": session_id,
                "patient_id": session.patient_id,
                "duration": "N/A", # Placeholder
                "message_count": 0 # Placeholder
            }
        )
