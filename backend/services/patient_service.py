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
    ConversationMessageSchema,
    ConversationDetailSchema,
)
from backend.services.data_service import get_data_service, DataServiceInterface
from backend.services.elevenlabs_service import get_elevenlabs_service, ElevenLabsServiceError
from backend.services.conversation_service import ConversationService
from backend.services.websocket_manager import get_connection_manager, WebSocketConnectionManager

class PatientService:
    """Service for managing patient conversation sessions."""

    def __init__(
        self,
        data_service: Optional[DataServiceInterface] = None,
        elevenlabs_service=None,
        conversation_service: Optional[ConversationService] = None,
        connection_manager: Optional[WebSocketConnectionManager] = None,
    ):
        """Initialize the service.
        
        Args:
            data_service: Optional data service injection for testing.
            elevenlabs_service: Optional ElevenLabs service injection.
            conversation_service: Optional conversation service injection.
            connection_manager: Optional WebSocket connection manager injection.
        """
        self.data_service = data_service or get_data_service()
        self.elevenlabs_service = elevenlabs_service or get_elevenlabs_service()
        self.conversation_service = conversation_service or ConversationService()
        self.connection_manager = connection_manager or get_connection_manager()

    async def create_session(self, request: PatientSessionCreate) -> PatientSessionResponse:
        """Create a new patient conversation session.

        Args:
            request: The session creation request.

        Returns:
            PatientSessionResponse: The created session details.
        """
        session_id = str(uuid.uuid4())
        
        # Look up the agent to get the ElevenLabs agent ID
        agent = await self.data_service.get_agent(request.agent_id)
        if not agent:
            raise ValueError(f"Agent with id {request.agent_id} not found")
        
        if not agent.elevenlabs_agent_id:
            raise ValueError(f"Agent {request.agent_id} has no ElevenLabs agent ID")
        
        # Get signed URL from ElevenLabs using the ElevenLabs agent ID
        try:
            signed_url = self.elevenlabs_service.get_signed_url(agent.elevenlabs_agent_id)
        except ElevenLabsServiceError as e:
            logging.error(f"Failed to get signed URL for session {session_id}: {e}")
            raise e

        # Create persistent WebSocket connection for this session
        try:
            await self.connection_manager.create_connection(
                session_id=session_id,
                signed_url=signed_url,
                agent_id=agent.elevenlabs_agent_id,
            )
            logging.info(f"WebSocket connection established for session {session_id}")
        except Exception as e:
            logging.error(f"Failed to create WebSocket connection for session {session_id}: {e}")
            # Continue without persistent connection - will fall back to one-shot mode

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
        self, session_id: str, message: str, chat_mode: bool = False
    ) -> PatientMessageResponse:
        """Send a message to the agent in the active session.

        Args:
            session_id: The session ID.
            message: The patient's message.
            chat_mode: Whether to use text-only mode.

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
        
        # Log patient message
        patient_msg_obj = ConversationMessageSchema(
            role="patient",
            content=message,
            timestamp=datetime.now()
        )
        await self.data_service.add_session_message(session_id, patient_msg_obj)
        
        # Look up the agent to get the ElevenLabs agent ID
        agent = await self.data_service.get_agent(session.agent_id)
        if not agent or not agent.elevenlabs_agent_id:
            raise ValueError(f"Agent {session.agent_id} not found or has no ElevenLabs ID")
        
        # Use persistent connection if available, otherwise fall back to one-shot
        try:
            has_conn = self.connection_manager.has_connection(session_id)
            if has_conn:
                # Use the persistent WebSocket connection
                logging.info(f"Using persistent connection for session {session_id}")
                response_text, audio_bytes = await self.connection_manager.send_message(
                    session_id, message, text_only=chat_mode
                )
            else:
                # Fallback to one-shot connection (legacy behavior)
                logging.warning(f"No persistent connection for session {session_id}, using one-shot")
                response_text, audio_bytes = await self.elevenlabs_service.send_text_message(
                    agent.elevenlabs_agent_id, message, text_only=chat_mode
                )
        except Exception as e:
            logging.error(f"Failed to get response from ElevenLabs for session {session_id}: {e}")
            # Graceful degradation: return text-only fallback
            response_text = (
                "I apologize, but I am currently experiencing technical difficulties "
                "and cannot generate a voice response. Please check the system status."
            )
            audio_bytes = None
        
        # Convert audio bytes to base64 if needed by Schema
        import base64
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8') if audio_bytes else None

        # Log agent message
        agent_msg_obj = ConversationMessageSchema(
            role="agent",
            content=response_text,
            timestamp=datetime.now(),
            audio_data=audio_b64
        )
        await self.data_service.add_session_message(session_id, agent_msg_obj)

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
        # Close WebSocket connection first
        await self.connection_manager.close_connection(session_id)
        logging.info(f"WebSocket connection closed for session {session_id}")
        
        session = await self.data_service.get_patient_session(session_id)
        if not session:
             # Idempotent success or error? 
             # Let's say false success for now or error.
             return SessionEndResponse(success=False, conversation_summary={"error": "Session not found"})

        # Perform any cleanup or final stats update
        # await self.data_service.update_patient_session(session_id, ended=True)
        
        messages = await self.data_service.get_session_messages(session_id)
        
        # Analyze conversation
        answered = []
        unanswered = []
        
        for i, msg in enumerate(messages):
            if msg.role == 'patient' and '?' in msg.content:
                # Check if next message is from agent
                if i + 1 < len(messages) and messages[i+1].role == 'agent':
                    answered.append(msg.content)
                    msg.is_answered = True
                else:
                    unanswered.append(msg.content)
                    msg.is_answered = False

        requires_attention = len(unanswered) > 0
        
        # Duration calculation
        duration = 0
        if messages:
            start = messages[0].timestamp
            end = messages[-1].timestamp
            duration = int((end - start).total_seconds())

        # Save conversation log
        if messages:
            detail = ConversationDetailSchema(
                conversation_id=session_id,
                patient_id=session.patient_id,
                agent_id=session.agent_id,
                agent_name="Medical Assistant",
                requires_attention=requires_attention,
                main_concerns=[],
                messages=messages,
                answered_questions=answered,
                unanswered_questions=unanswered,
                duration_seconds=duration,
                created_at=messages[0].timestamp
            )
            await self.conversation_service.save_conversation(detail)

        return SessionEndResponse(
            success=True,
            conversation_summary={
                "session_id": session_id,
                "patient_id": session.patient_id,
                "duration": f"{duration}s",
                "message_count": len(messages)
            }
        )
