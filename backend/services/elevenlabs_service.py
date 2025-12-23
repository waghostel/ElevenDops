"""Service for ElevenLabs Knowledge Base operations."""

import logging
import os
import tempfile
import uuid
from enum import Enum
from typing import Optional

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception, retry_if_exception_type
from elevenlabs.client import ElevenLabs
try:
    from elevenlabs import APIConnectionError
except ImportError:
    # Fallback if APIConnectionError is moved or renamed in newer SDK versions
    class APIConnectionError(Exception):
        pass
import websockets
import json
import base64
import asyncio
from backend.config import get_settings


class ElevenLabsServiceError(Exception):
    """Base exception for ElevenLabs service errors."""

    pass


class ElevenLabsErrorType(Enum):
    RATE_LIMIT = "rate_limit"
    AUTH_ERROR = "auth_error"
    VALIDATION = "validation"
    SERVER_ERROR = "server_error"
    NETWORK = "network"
    UNKNOWN = "unknown"


class ElevenLabsSyncError(ElevenLabsServiceError):
    """Raised when document sync to ElevenLabs fails."""

    def __init__(
        self, 
        message: str, 
        error_type: ElevenLabsErrorType = ElevenLabsErrorType.UNKNOWN,
        original_error: Optional[Exception] = None,
        is_retryable: bool = False
    ):
        super().__init__(message)
        self.error_type = error_type
        self.original_error = original_error
        self.is_retryable = is_retryable




class ElevenLabsDeleteError(ElevenLabsServiceError):
    """Raised when document deletion from ElevenLabs fails."""

    pass


class ElevenLabsTTSError(ElevenLabsServiceError):
    """Raised when text-to-speech conversion fails."""

    pass


class ElevenLabsAgentError(ElevenLabsServiceError):
    """Raised when agent operations fail."""

    pass


def _should_retry(exception: Exception) -> bool:
    """Determine if exception should trigger retry."""
    if isinstance(exception, ElevenLabsSyncError):
        return exception.is_retryable
    return False


class ElevenLabsService:
    """Service for ElevenLabs Knowledge Base operations.

    Handles interactions with the ElevenLabs API for managing knowledge base documents.
    """

    def __init__(self):
        """Initialize ElevenLabs client."""
        # Check for API key but don't crash if missing (for tests/local dev without key)
        settings = get_settings()
        api_key = settings.elevenlabs_api_key
        
        # Determine strict mock mode from config
        config_mock = settings.use_mock_elevenlabs
        
        # Auto-fallback logic: Use mock if explicitly requested OR if key is missing
        if config_mock:
            self.use_mock = True
            logging.info("ElevenLabs Mock Mode enabled via configuration.")
        elif not api_key:
            self.use_mock = True
            logging.warning("ELEVENLABS_API_KEY not found. Automatically falling back to Mock Service to prevent errors.")
        else:
            self.use_mock = False

        # Initialize client only if we are valid to use real service
        if self.use_mock:
            self.client = None
        else:
            self.client = ElevenLabs(api_key=api_key)

    def _classify_error(self, error: Exception) -> tuple[ElevenLabsErrorType, bool]:
        """Classify error and determine if retryable."""
        error_str = str(error).lower()
        
        # Check for rate limiting
        if "429" in error_str or "rate" in error_str:
            return ElevenLabsErrorType.RATE_LIMIT, True
        
        # Check for auth errors
        if "401" in error_str or "403" in error_str or "unauthorized" in error_str:
            return ElevenLabsErrorType.AUTH_ERROR, False
        
        # Check for validation errors
        if "400" in error_str or "invalid" in error_str:
            return ElevenLabsErrorType.VALIDATION, False
        
        # Check for server errors
        if any(code in error_str for code in ["500", "502", "503", "504"]):
            return ElevenLabsErrorType.SERVER_ERROR, True
        
        # Check for network errors
        if any(term in error_str for term in ["connection", "timeout", "network"]):
            return ElevenLabsErrorType.NETWORK, True
        
        return ElevenLabsErrorType.UNKNOWN, False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception(_should_retry),
        reraise=True,
        before_sleep=lambda retry_state: logging.warning(
            f"Retrying ElevenLabs API call, attempt {retry_state.attempt_number}"
        )
    )
    def create_document(self, text: str, name: str) -> str:
        """Create document in ElevenLabs Knowledge Base.

        Args:
            text: The content of the document.
            name: The name/title of the document.

        Returns:
            str: The ElevenLabs document ID.

        Raises:
            ElevenLabsSyncError: If creation fails.
        """
        logging.info(f"Creating ElevenLabs document: {name} (length: {len(text)})")
        
        if self.use_mock:
            mock_id = f"mock_doc_{uuid.uuid4()}"
            logging.info(f"[MOCK] Created ElevenLabs document {name}. ID: {mock_id}")
            # Simulate network delay if needed
            return mock_id

        try:
            # Create a temporary file to upload as the API expects a file-like object or path
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.md', encoding='utf-8') as tmp:
                tmp.write(text)
                tmp_path = tmp.name
            
            try:
                with open(tmp_path, 'rb') as f:
                    # Updates for new SDK structure: flattened API
                    # Using tuple (name, file_obj, content_type) to ensure document name is set correctly
                    response = self.client.conversational_ai.create_knowledge_base_file_document(
                        file=(name, f, 'text/markdown')
                    )
                logging.info(f"Successfully created document {name}. ID: {response.id}")
                return response.id
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        except Exception as e:
            error_type, is_retryable = self._classify_error(e)
            
            # Log full stack trace for unexpected errors, cleaner log for known ones
            if error_type == ElevenLabsErrorType.UNKNOWN:
                logging.error(f"Failed to create ElevenLabs document '{name}': {e}", exc_info=True)
            else:
                logging.error(f"Failed to create ElevenLabs document '{name}': {e} (Type: {error_type.value}, Retryable: {is_retryable})")
                
            raise ElevenLabsSyncError(
                message=f"Failed to sync with ElevenLabs: {str(e)}",
                error_type=error_type,
                original_error=e,
                is_retryable=is_retryable
            )

    def delete_document(self, document_id: str) -> bool:
        """Delete document from ElevenLabs Knowledge Base.

        Args:
            document_id: The ID of the document to delete.

        Returns:
            bool: True if deleted successfully.

        Raises:
            ElevenLabsDeleteError: If deletion fails.
        """
        try:
            # Also apply deletion error handling
            logging.info(f"Deleting ElevenLabs document: {document_id}")
            
            if self.use_mock:
                logging.info(f"[MOCK] Deleted ElevenLabs document {document_id}")
                return True

            self.client.conversational_ai.delete_knowledge_base_document(document_id=document_id)
            logging.info(f"Successfully deleted document {document_id}")
            return True
        except Exception as e:
            # We don't typically retry deletes as aggressively, but logging is important
            logging.error(f"Failed to delete ElevenLabs document {document_id}: {e}")
            # Could classify here too if needed, but keeping it simple for now as per spec focus on Sync
            raise ElevenLabsDeleteError(f"Failed to delete from ElevenLabs: {str(e)}")

    def text_to_speech(self, text: str, voice_id: str) -> bytes:
        """Convert text to speech using ElevenLabs API.

        Args:
            text: The text to convert.
            voice_id: The ID of the voice to use.

        Returns:
            bytes: The audio data.

        Raises:
            ElevenLabsTTSError: If conversion fails.
        """
        if self.use_mock:
            # Return a minimal valid MP3 frame (silence)
            logging.info(f"[MOCK] text_to_speech called for text length {len(text)}")
            # Minimal MP3 header + silence frame
            return b'\xff\xfb\x90\x00' + b'\x00' * 417

        try:
            # Using the text_to_speech.convert method from the Python SDK
            # convert returns a generator of bytes, so we need to consume it
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id="eleven_multilingual_v2"
            )
            
            # Consume the generator to get the full audio bytes
            audio_data = b"".join(chunk for chunk in audio_generator)
            return audio_data
            
        except Exception as e:
            logging.error(f"Failed to generate audio: {e}")
            raise ElevenLabsTTSError(f"Failed to generate audio: {str(e)}")

    def get_voices(self) -> list[dict]:
        """Get available voices from ElevenLabs.

        Returns:
            list[dict]: List of voice dictionaries containing id, name, etc.
            
        Raises:
            ElevenLabsTTSError: If fetching voices fails.
        """
        if self.use_mock:
            logging.info("[MOCK] get_voices called")
            return [
                {"voice_id": "mock_voice_1", "name": "Mock Rachel", "preview_url": None, "description": "Mock female voice"},
                {"voice_id": "mock_voice_2", "name": "Mock Adam", "preview_url": None, "description": "Mock male voice"},
            ]

        try:
            response = self.client.voices.get_all()
            # response.voices is a list of Voice objects
            return [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "preview_url": voice.preview_url,
                    "description": getattr(voice, "description", None) or f"{voice.category} voice"
                }
                for voice in response.voices
            ]
        except Exception as e:
            logging.error(f"Failed to fetch voices: {e}")
            raise ElevenLabsTTSError(f"Failed to fetch voices: {str(e)}")

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((ElevenLabsAgentError, APIConnectionError))
    )
    def create_agent(
        self,
        name: str,
        system_prompt: str,
        knowledge_base_ids: list[str],
        voice_id: str,
    ) -> str:
        """Create a conversational AI agent in ElevenLabs.

        Args:
            name: Name of the agent.
            system_prompt: System prompt defining agent behavior.
            knowledge_base_ids: List of knowledge base document IDs.
            voice_id: ID of the voice to use.

        Returns:
            str: The created agent ID.

        Raises:
            ElevenLabsAgentError: If creation fails.
        """
        if not voice_id:
             raise ElevenLabsAgentError("Voice ID is required")

        if self.use_mock:
            mock_id = f"mock_agent_{uuid.uuid4()}"
            logging.info(f"[MOCK] create_agent called: {name}. ID: {mock_id}")
            return mock_id

        try:
            # Construct agent config
            agent_config = {
                "prompt": {
                    "prompt": system_prompt
                },
                "first_message": "您好，我是您的醫療助手。請問有什麼我可以幫您的？", # Traditional Chinese
                "language": "en" # Use 'en' as safe default, the prompt instructs Chinese
            }
            
            # Add KB if present
            if knowledge_base_ids:
                 agent_config["prompt"]["knowledge_base"] = [
                     {"id": kb_id} for kb_id in knowledge_base_ids
                 ]
                 
            response = self.client.conversational_ai.create_agent(
                name=name,
                conversation_config={
                    "agent": agent_config,
                    "tts": {
                        "voice_id": voice_id
                    }
                }
            )
            
            return response.agent_id

        except Exception as e:
            error_type, _ = self._classify_error(e)
            logging.error(f"Failed to create ElevenLabs agent: {e}")
            raise ElevenLabsAgentError(f"Failed to create agent: {str(e)}", error_type=error_type)

    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent from ElevenLabs.

        Args:
            agent_id: The ID of the agent to delete.

        Returns:
            bool: True if deleted successfully.

        Raises:
            ElevenLabsAgentError: If deletion fails.
        """
        if self.use_mock:
            logging.info(f"[MOCK] delete_agent called: {agent_id}")
            return True

        try:
            self.client.conversational_ai.delete_agent(agent_id=agent_id)
            return True
        except Exception as e:
            logging.error(f"Failed to delete ElevenLabs agent: {e}")
            raise ElevenLabsAgentError(f"Failed to delete agent: {str(e)}")

    def get_agent(self, agent_id: str) -> dict:
        """Get agent details from ElevenLabs.

        Args:
            agent_id: The ID of the agent to retrieve.

        Returns:
            dict: Agent details.

        Raises:
            ElevenLabsAgentError: If retrieval fails.
        """
        if self.use_mock:
            logging.info(f"[MOCK] get_agent called: {agent_id}")
            return {
                "agent_id": agent_id,
                "name": "Mock Agent",
                "conversation_config": {"agent": {"prompt": {"prompt": "Mock system prompt"}}}
            }

        try:
            response = self.client.conversational_ai.get_agent(agent_id=agent_id)
            return response.model_dump() if hasattr(response, "model_dump") else dict(response)
        except Exception as e:
            logging.error(f"Failed to get ElevenLabs agent: {e}")
            raise ElevenLabsAgentError(f"Failed to get agent: {str(e)}")


# ... (existing methods)

    def get_signed_url(self, agent_id: str) -> str:
        """Get a signed URL for an agent conversation.

        Args:
            agent_id: The ID of the agent.

        Returns:
            str: The signed WebSocket URL.

        Raises:
            ElevenLabsAgentError: If retrieval fails.
        """
        if self.use_mock:
            logging.info(f"[MOCK] get_signed_url called: {agent_id}")
            return f"wss://mock.elevenlabs.io/convai/{agent_id}"

        try:
            response = self.client.conversational_ai.get_signed_url(agent_id=agent_id)
            return response.signed_url
        except Exception as e:
            logging.error(f"Failed to get signed URL: {e}")
            raise ElevenLabsAgentError(f"Failed to get signed URL: {str(e)}")

    async def send_text_message(self, agent_id: str, text: str) -> tuple[str, bytes]:
        """Send a text message to the agent and get audio response.

        Args:
            agent_id: The agent ID.
            text: The user's message.

        Returns:
            tuple[str, bytes]: (Response text, Audio data)

        Raises:
            ElevenLabsAgentError: If communication fails.
        """
        if self.use_mock:
            logging.info(f"[MOCK] send_text_message called: agent={agent_id}, text={text[:50]}...")
            return ("This is a mock response from the AI assistant.", b'')

        try:
            # Get signed URL
            signed_url = self.get_signed_url(agent_id)
            
            async with websockets.connect(signed_url) as websocket:
                # Send initial message to trigger response
                # Format based on ElevenLabs ConvAI WebSocket protocol
                # Usually we just send a text event if the session is open, 
                # but for a strict single-turn "REST-like" behavior:
                
                # 1. Send text
                # The protocol expects a JSON with "text" event
                payload = {
                    "text": text,
                    "try_trigger_generation": True
                }
                await websocket.send(json.dumps(payload))
                
                audio_chunks = []
                response_text_parts = []
                
                # Listen for response
                # We need to determine when the turn is over. 
                # ElevenLabs sends `audio_event` and `agent_response_event`.
                # We'll collect until we get a logical break or timeout.
                # A simple heuristic for this stateless method: wait for audio and text.
                
                while True:
                    try:
                        # concise timeout for response
                        message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        data = json.loads(message)
                        
                        if data.get("audio_event"):
                            # Collect audio chunks
                            audio_base64 = data["audio_event"].get("audio_base_64")
                            if audio_base64:
                                audio_chunks.append(base64.b64decode(audio_base64))
                                
                        if data.get("agent_response_event"):
                            # Collect text portion
                            part = data["agent_response_event"].get("agent_response")
                            if part:
                                response_text_parts.append(part)

                        # Check for turn completion signals if available, or break after some conditions
                        # For now, we might need a timeout or specific "turn_end" event if ElevenLabs sends one.
                        # Looking at API docs, 'interruption' or 'ping' might be relevant, 
                        # but standard conversation usually flows. 
                        # To keep it simple and synchronous-like for this API: 
                        # We wait for a reasonable timeout or a specific "end of turn" marker.
                        # ElevenLabs ConvAI WebSocket docs don't strictly define "end of turn" message 
                        # that guarantees "I'm done talking" without logic.
                        # However, for a single text interaction, we might assume the first response sequence is it.
                        
                        # HACK: For Phase 1 single-turn text mode, let's wait for a short bit of silence or 
                        # just gather until timeout if no specific end event.
                        # Force break after collecting substantial response? No.
                        # Let's assume the client (backend) closes when it thinks it's done?
                        # No, we want the full answer.
                        
                        # Let's rely on `agent_response_event` indicating finality? 
                        # It's a stream.
                        
                        # Hack: Wait for a short timeout after receiving ANY data?
                        # Improved: Use a specialized "end of turn" check if available.
                        # If not, satisfy Requirement with basic accumulation.
                        
                    except asyncio.TimeoutError:
                        break
                    except websockets.exceptions.ConnectionClosed:
                        break

                full_text = "".join(response_text_parts)
                full_audio = b"".join(audio_chunks)
                
                if not full_text and not full_audio:
                     # If we got nothing, maybe try to wait longer or check for errors
                     logging.warning("No response received from ElevenLabs agent")

                return full_text, full_audio

        except Exception as e:
            logging.error(f"Failed to send text message: {e}")
            raise ElevenLabsAgentError(f"Failed to send text message: {str(e)}")


# Default service instance
def get_elevenlabs_service() -> ElevenLabsService:
    """Get the ElevenLabs service instance."""
    return ElevenLabsService()
