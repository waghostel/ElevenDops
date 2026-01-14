"""Service for ElevenLabs Knowledge Base operations."""

import logging
from io import BytesIO
import uuid
from enum import Enum
from typing import Optional, List, Dict, Any

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


def _should_retry(exception: Exception) -> bool:
    """Determine if exception should trigger retry."""
    if isinstance(exception, ElevenLabsSyncError):
        return exception.is_retryable
    return False


def _should_retry_agent(exception: Exception) -> bool:
    """Determine if agent exception should trigger retry."""
    if isinstance(exception, ElevenLabsAgentError):
        return exception.is_retryable
    if isinstance(exception, APIConnectionError):
        return True
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
            # Use in-memory BytesIO instead of temp file for better Cloud Run performance
            file_bytes = BytesIO(text.encode('utf-8'))
            response = self.client.conversational_ai.knowledge_base.documents.create_from_file(
                file=(name, file_bytes, 'text/markdown')
            )
            logging.info(f"Successfully created document {name}. ID: {response.id}")
            return response.id

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

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all Knowledge Base documents.

        Returns:
            List[Dict[str, Any]]: List of document metadata.
        """
        if self.use_mock:
            logging.info("[MOCK] list_documents called")
            return []

        try:
            docs = self.client.conversational_ai.knowledge_base.list()
            # The SDK returns an object with a 'documents' attribute or a list
            doc_list = list(docs.documents) if hasattr(docs, 'documents') else list(docs)
            return [
                {
                    "id": getattr(d, "id", None) or getattr(d, "document_id", "unknown"),
                    "name": getattr(d, "name", "Unnamed"),
                    "created_at": getattr(d, "created_at", None),
                    "type": getattr(d, "type", "file")
                }
                for d in doc_list
            ]
        except Exception as e:
            logging.error(f"Failed to list ElevenLabs documents: {e}")
            return []

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

            self.client.conversational_ai.knowledge_base.documents.delete(document_id)
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
                model_id="eleven_v3"
            )
            
            # Consume the generator to get the full audio bytes
            audio_data = b"".join(chunk for chunk in audio_generator)
            return audio_data
            
        except Exception as e:
            logging.error(f"Failed to generate audio: {e}")
            raise ElevenLabsTTSError(f"Failed to generate audio: {str(e)}")

    def get_voices(self) -> List[Dict[str, Any]]:
        """
        Get available voices for agent creation.
        Returns a merged list of:
        1. Specialized 'Curated Voices' (Verified V2.5 Public Voices) - Always shown
        2. User's 'My Voices' (Private library)
        """
        # 1. Curated Voices (Verified Public Voices V2.5)
        # These are specific voices the user wants to use, verified for V2.5 compatibility.
        # We hardcode them here to ensure they appear even if not in the user's library.
        CURATED_VOICES = [
            {"voice_id": "UgBBYS2sOqTuMpoF3BR0", "name": "Mark - Casual and Conversational", "preview_url": None, "languages": ["en"]},
            {"voice_id": "NOpBlnGInO9m6vDvFkFC", "name": "Spuds Oxley - Wise and Approachable", "preview_url": None, "languages": ["en"]},
            {"voice_id": "56AoDkrOh6qfVPDXZ7Pt", "name": "Cassidy - Crisp, Direct and Clear", "preview_url": None, "languages": ["en"]},
            {"voice_id": "1SM7GgM6IMuvQlz2BwM3", "name": "Mark - Casual, Relaxed and Light", "preview_url": None, "languages": ["en"]},
            {"voice_id": "zT03pEAEi0VHKciJODfn", "name": "Raju - Clear, Natural and Warm", "preview_url": None, "languages": ["en"]},
            {"voice_id": "IvLWq57RKibBrqZGpQrC", "name": "Leo - Energetic, Inviting, and Round", "preview_url": None, "languages": ["en"]},
            {"voice_id": "DMyrgzQFny3JI1Y1paM5", "name": "Donovan - Articulate, Strong and Deep", "preview_url": None, "languages": ["en"]},
            {"voice_id": "Fahco4VZzobUeiPqni1S", "name": "Archer - Conversational", "preview_url": None, "languages": ["en"]},
            {"voice_id": "vBKc2FfBKJfcZNyEt1n6", "name": "Finn - Youthful, Eager and Energetic", "preview_url": None, "languages": ["en"]},
            {"voice_id": "g6xIsTj2HwM6VR4iXFCw", "name": "Jessica Anne Bogart - Chatty and Friendly", "preview_url": None, "languages": ["en"]},
        ]
        
        if self.use_mock:
            logging.info("[MOCK] get_voices called - returning curated voices")
            return CURATED_VOICES

        try:
            # Fetch actual available voices from User's Account (My Voices)
            response = self.client.voices.get_all()
            user_voices_map = {v.voice_id: v for v in response.voices}
            
            final_voices = []
            
            # 1. Add ALL Curated Voices (Priority)
            # We explicitly add them even if they are NOT in the library, 
            # because we verified they work with V2.5 (unless Agent API strictly forbids it).
            # If they ARE in the library, we update metadata.
            for cv in CURATED_VOICES:
                vid = cv["voice_id"]
                if vid in user_voices_map:
                    # Enriched with account data (like preview_url if available)
                    v_obj = user_voices_map[vid]
                    cv["name"] = v_obj.name # Use library name if desired, or keep curated
                    cv["preview_url"] = v_obj.preview_url
                    cv["in_library"] = True
                else:
                     cv["description"] = "Public Voice (Add to Library recommended)"
                     # We assume verified voices have at least 'en' support or we use standard
                     cv["in_library"] = False
                final_voices.append(cv)
            
            # 2. Add other User Voices (if not already in curated)
            # This ensures the user still sees their own voices
            curated_ids = set(cv["voice_id"] for cv in CURATED_VOICES)
            for vid, v in user_voices_map.items():
                if vid not in curated_ids:
                     final_voices.append({
                        "voice_id": v.voice_id,
                        "name": v.name,
                        "preview_url": v.preview_url,
                        "description": "My Library Voice",
                        "languages": ["en"] # Fallback
                     })
                     
            return final_voices

        except Exception as e:
            logging.error(f"Failed to fetch voices from API: {e}")
            # Fallback to just curated if API fails
            return CURATED_VOICES

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception(_should_retry_agent),
        reraise=True,
        before_sleep=lambda retry_state: logging.warning(
            f"Retrying ElevenLabs agent creation, attempt {retry_state.attempt_number}"
        )
    )
    def create_agent(
        self,
        name: str,
        system_prompt: str,
        knowledge_base: list[dict],
        voice_id: str,
        languages: list[str] = None,
    ) -> str:
        """Create a conversational AI agent in ElevenLabs.

        Args:
            name: Name of the agent.
            system_prompt: System prompt defining agent behavior.
            knowledge_base: List of knowledge base items, each with 'id', 'name', 'type'.
            voice_id: ID of the voice to use.
            languages: List of language codes (first is primary, others enable auto-detection).

        Returns:
            str: The created agent ID.

        Raises:
            ElevenLabsAgentError: If creation fails.
        """
        if not voice_id:
             raise ElevenLabsAgentError("Voice ID is required")
        
        # Default to English if no languages provided
        if not languages:
            languages = ["en"]

        if self.use_mock:
            mock_id = f"mock_agent_{uuid.uuid4()}"
            logging.info(f"[MOCK] create_agent called: {name}. ID: {mock_id}")
            return mock_id

        try:
            # Construct agent config
            primary_language = languages[0]
            agent_config = {
                "prompt": {
                    "prompt": system_prompt
                },
                "first_message": "Hello! I'm your medical assistant. How can I help you today?",
                "language": primary_language  # Primary language
            }
            
            # Add language_presets for multi-language support (auto-detection)
            if len(languages) > 1:
                language_presets = {}
                for lang in languages:
                    # Each language uses the same voice_id (curated voices support multiple languages)
                    language_presets[lang] = {"voice_id": voice_id}
                agent_config["language_presets"] = language_presets
            
            # Add KB if present (already in correct format with id, name, type)
            if knowledge_base:
                 agent_config["prompt"]["knowledge_base"] = knowledge_base
                 
            # Determine TTS model and Primary Language based on configuration
            # - English-only agents (language="en") use turbo_v2
            # - Multilingual agents use turbo_v2_5
            
            model_id = "eleven_turbo_v2_5" # Default to multilingual
            
            if len(languages) == 1 and languages[0] == "en":
                # Case 1: Pure English -> Use v2, keep 'en' as primary
                model_id = "eleven_turbo_v2"
                logging.info(f"Creating English-only agent with {model_id}")
            else:
                # Case 2: Multilingual or Non-English -> Use v2.5
                # Primary language is whatever the user specified first
                logging.info(f"Creating Multilingual agent with {model_id} (Primary: {primary_language})")

            # DEBUG LOGGING
            import json
            logging.info(f"[DEBUG] Final Agent Config: {json.dumps(agent_config, default=str)}")

            response = self.client.conversational_ai.agents.create(
                name=name,
                conversation_config={
                    "agent": agent_config,
                    "tts": {
                        "voice_id": voice_id,
                        "model_id": model_id
                    }
                }
            )
            
            return response.agent_id

        except Exception as e:
            error_type, is_retryable = self._classify_error(e)
            logging.error(f"Failed to create ElevenLabs agent: {e}")
            raise ElevenLabsAgentError(f"Failed to create agent: {str(e)}", error_type=error_type, original_error=e, is_retryable=is_retryable)

    def update_agent_knowledge_base(self, agent_id: str, knowledge_base: List[Dict[str, Any]]) -> bool:
        """Update an agent's knowledge base.

        Args:
            agent_id: The ID of the agent to update.
            knowledge_base: The new list of knowledge base items.

        Returns:
            bool: True if updated successfully.

        Raises:
            ElevenLabsAgentError: If update fails.
        """
        if self.use_mock:
            logging.info(f"[MOCK] update_agent_knowledge_base called for agent {agent_id}")
            return True

        try:
            self.client.conversational_ai.agents.update(
                agent_id=agent_id,
                conversation_config={
                    "agent": {
                        "prompt": {
                            "knowledge_base": knowledge_base
                        }
                    }
                }
            )
            logging.info(f"Successfully updated knowledge base for agent {agent_id}")
            return True
        except Exception as e:
            logging.error(f"Failed to update ElevenLabs agent {agent_id} knowledge base: {e}")
            raise ElevenLabsAgentError(f"Failed to update agent knowledge base: {str(e)}")

    def update_agent(
        self,
        agent_id: str,
        name: Optional[str] = None,
        knowledge_base: Optional[List[Dict[str, Any]]] = None,
        languages: Optional[List[str]] = None,
    ) -> bool:
        """Update an existing agent's settings.

        Args:
            agent_id: The ElevenLabs agent ID.
            name: New agent name (optional).
            knowledge_base: New knowledge base list (optional).
            languages: New language codes (optional).

        Returns:
            bool: True if updated successfully.

        Raises:
            ElevenLabsAgentError: If update fails.
        """
        if self.use_mock:
            logging.info(f"[MOCK] update_agent called for agent {agent_id}")
            return True

        try:
            # Build update payload - only include fields that are being updated
            update_kwargs = {"agent_id": agent_id}
            
            # Update name if provided
            if name is not None:
                update_kwargs["name"] = name
            
            # Build conversation_config for agent settings
            conversation_config = {}
            agent_config = {}
            prompt_config = {}
            
            # Update knowledge base if provided
            if knowledge_base is not None:
                prompt_config["knowledge_base"] = knowledge_base
            
            # Update languages if provided
            if languages is not None:
                primary_language = languages[0]
                
                # Determine TTS model based on languages
                if len(languages) == 1 and languages[0] == "en":
                    # English-only: use v2
                    model_id = "eleven_turbo_v2"
                else:
                    # Multilingual: use v2.5
                    model_id = "eleven_turbo_v2_5"
                    # If primary is English but we're multilingual, swap to first non-English
                    if primary_language == "en":
                        non_en_langs = [l for l in languages if l != "en"]
                        if non_en_langs:
                            primary_language = non_en_langs[0]
                            logging.warning(
                                f"Swapping primary language from 'en' to '{primary_language}' "
                                f"for {model_id} validation."
                            )
                
                agent_config["language"] = primary_language
                
                # Add language_presets for multi-language support
                if len(languages) > 1:
                    # Note: We don't have voice_id here, so we can't set language_presets.voice_id
                    # The API will preserve existing voice_id in presets
                    language_presets = {lang: {} for lang in languages}
                    agent_config["language_presets"] = language_presets
                
                # Update TTS model
                conversation_config["tts"] = {"model_id": model_id}
            
            # Assemble conversation_config
            if prompt_config:
                agent_config["prompt"] = prompt_config
            if agent_config:
                conversation_config["agent"] = agent_config
            if conversation_config:
                update_kwargs["conversation_config"] = conversation_config
            
            # Perform the update
            logging.info(f"Updating agent {agent_id} with: {update_kwargs}")
            self.client.conversational_ai.agents.update(**update_kwargs)
            logging.info(f"Successfully updated agent {agent_id}")
            return True
            
        except Exception as e:
            error_type, is_retryable = self._classify_error(e)
            logging.error(f"Failed to update ElevenLabs agent {agent_id}: {e}")
            raise ElevenLabsAgentError(
                f"Failed to update agent: {str(e)}",
                error_type=error_type,
                original_error=e,
                is_retryable=is_retryable
            )



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
            self.client.conversational_ai.agents.delete(agent_id=agent_id)
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
            response = self.client.conversational_ai.agents.get(agent_id=agent_id)
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
            response = self.client.conversational_ai.conversations.get_signed_url(agent_id=agent_id)
            return response.signed_url
        except Exception as e:
            logging.error(f"Failed to get signed URL: {e}")
            raise ElevenLabsAgentError(f"Failed to get signed URL: {str(e)}")

    async def send_text_message(self, agent_id: str, text: str, text_only: bool = False) -> tuple[str, bytes]:
        """Send a text message to the agent and get response.

        Args:
            agent_id: The agent ID.
            text: The user's message.
            text_only: If True, request text-only response (no audio synthesis).

        Returns:
            tuple[str, bytes]: (Response text, Audio data)

        Raises:
            ElevenLabsAgentError: If communication fails.
        """
        if self.use_mock:
            logging.info(f"[MOCK] send_text_message called: agent={agent_id}, text={text[:50]}..., text_only={text_only}")
            if text_only:
                return ("This is a mock text-only response.", b"")
            # Return a minimal valid MP3 frame (silence) to prevent frontend audio errors
            mock_audio = b'\xff\xfb\x90\x00' + b'\x00' * 417
            return ("This is a mock response from the AI assistant.", mock_audio)

        try:
            # Get signed URL
            signed_url = self.get_signed_url(agent_id)
            
            async with websockets.connect(signed_url) as websocket:
                # 1. Send text
                payload = {
                    "text": text,
                    "try_trigger_generation": not text_only
                }
                
                if text_only:
                     logging.info(f"Sending text-only message to agent {agent_id}")
                
                await websocket.send(json.dumps(payload))
                
                audio_chunks = []
                response_text_parts = []
                drain_deadline = None  # Timestamp when we must stop waiting
                
                # Listen for response with drain timeout strategy
                while True:
                    try:
                        # Calculate dynamic timeout
                        if drain_deadline:
                            # In drain mode: calculate time remaining until hard deadline
                            import time
                            time_left = drain_deadline - time.time()
                            if time_left <= 0:
                                # Deadline reached, stop collecting
                                logging.info("Drain timeout reached, ending message collection")
                                break
                            timeout = time_left
                        else:
                            # Normal mode: standard activity timeout
                            timeout = 10.0
                        
                        message = await asyncio.wait_for(websocket.recv(), timeout=timeout)
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
                            
                            # Text response received
                            # If text_only, we can stop immediately after full text (single turn assumption)
                            # or wait for a very short drain if needed.
                            # For now, we reuse drain logic but strict it for text-only.
                            
                            if not drain_deadline:
                                import time
                                if text_only:
                                    # In text-only mode, we don't expect audio, so we can stop faster
                                    # But sometimes multiple text events might come?
                                    # Usually it's one event or stream. 
                                    # We give a short drain just in case of multiple text parts.
                                    drain_deadline = time.time() + 0.5 
                                    logging.info("Text-only response received, entering short drain (0.5s)")
                                else:
                                    drain_deadline = time.time() + 2.0
                                    logging.info("Agent response received, entering drain mode (2s deadline)")
                        
                        # Ignore ping_event - it doesn't affect our drain deadline
                        
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
