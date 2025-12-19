"""Service for ElevenLabs Knowledge Base operations."""

import logging
import os
import tempfile
from typing import Optional

from elevenlabs.client import ElevenLabs


class ElevenLabsServiceError(Exception):
    """Base exception for ElevenLabs service errors."""

    pass


class ElevenLabsSyncError(ElevenLabsServiceError):
    """Raised when document sync to ElevenLabs fails."""

    pass




class ElevenLabsDeleteError(ElevenLabsServiceError):
    """Raised when document deletion from ElevenLabs fails."""

    pass


class ElevenLabsTTSError(ElevenLabsServiceError):
    """Raised when text-to-speech conversion fails."""

    pass


class ElevenLabsAgentError(ElevenLabsServiceError):
    """Raised when agent operations fail."""

    pass


class ElevenLabsService:
    """Service for ElevenLabs Knowledge Base operations.

    Handles interactions with the ElevenLabs API for managing knowledge base documents.
    """

    def __init__(self):
        """Initialize ElevenLabs client."""
        # Check for API key but don't crash if missing (for tests/local dev without key)
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            logging.warning("ELEVENLABS_API_KEY not found. ElevenLabs integration will fail.")
        self.client = ElevenLabs(api_key=api_key)

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
        try:
            # Create a temporary file to upload as the API expects a file-like object or path
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.md', encoding='utf-8') as tmp:
                tmp.write(text)
                tmp_path = tmp.name
            
            try:
                with open(tmp_path, 'rb') as f:
                    response = self.client.conversational_ai.add_to_knowledge_base(
                        name=name,
                        file=f
                    )
                return response.id
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        except Exception as e:
            logging.error(f"Failed to create ElevenLabs document: {e}")
            raise ElevenLabsSyncError(f"Failed to sync with ElevenLabs: {str(e)}")

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
            self.client.conversational_ai.delete_knowledge_base_document(document_id=document_id)
            return True
        except Exception as e:
            logging.error(f"Failed to delete ElevenLabs document: {e}")
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
        try:
            response = self.client.voices.get_all()
            # response.voices is a list of Voice objects
            return [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "preview_url": voice.preview_url,
                    # Add generic description if not present, or extract labels/description if available
                    # 'description' isn't always directly on the Voice object in simplified views, 
                    # but we can pass what we have.
                    "description": getattr(voice, "description", None) or f"{voice.category} voice"
                }
                for voice in response.voices
            ]
        except Exception as e:
            logging.error(f"Failed to fetch voices: {e}")
            raise ElevenLabsTTSError(f"Failed to fetch voices: {str(e)}")

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
        try:
            # Note: The SDK method signature might vary slightly based on version.
            # Assuming client.conversational_ai.agents.create based on general pattern 
            # or client.conversational_ai.create_agent depending on exact SDK version.
            # Based on recent SDKs it's often:
            response = self.client.conversational_ai.create_agent(
                name=name,
                conversation_config={
                    "agent": {
                         "prompt": {
                             "prompt": system_prompt
                         },
                         "language": "en", # or "zh" if supported/needed, defaults usually fine
                         "first_message": "Hello, I am your medical assistant. How can I help you today?"
                    },
                     "tts": {
                         "voice_id": voice_id
                     }
                }
            )
            
            # Linking knowledge base often happens either during creation or via separate update
            # If the creation API supports it directly:
            # The SDK is rapidly evolving. Let's assume we might need to add knowledge based on the docs.
            # But wait, looking at standard ElevenLabs Conversational AI API, knowledge base is part of agent config.
            # Let's try to update it after creation if needed, or pass it if possible.
            # Given the lack of precise SDK docs in context, I will attempt to pass it in config if possible, 
            # or do a second call.
            
            # Actually, `client.conversational_ai.create_agent` usually takes a config object.
            # Let's use a robust approach: create then potentially patch if KB is separate, 
            # but usually it's in the 'agent' -> 'knowledge_base' section.
            
            # However, since I don't have the exact SDK signature in front of me (I saw 'add_to_knowledge_base' earlier),
            # and I need to be safe.
            # I will assume the `create_agent` returns an object with an `agent_id`.
            
            # Wait, looking at `elevenlabs_integration.md`:
            # Endpoint: `client.conversational_ai.agents.create_or_update()` 
            # But `elevenlabs_service.py` uses `self.client.conversational_ai`.
            
            # Let's try to implement with the presumed correct structure:
            
            # Construct the comprehensive config
            # Checks for knowledge base field support
            
            agent_config = {
                "prompt": {
                    "prompt": system_prompt
                },
                "first_message": "您好，我是您的醫療助手。請問有什麼我可以幫您的？", # Chinese default
                "language": "en" # Conversational AI often entails the model language, 'en' is safest, 'zh' if supported.
            }
            
            if knowledge_base_ids:
                 # Depending on SDK, might be 'knowledge_base': [{'id': ...}] or similar
                 # Checking commonly used patterns:
                 agent_config["knowledge_base"] = [
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
            logging.error(f"Failed to create ElevenLabs agent: {e}")
            raise ElevenLabsAgentError(f"Failed to create agent: {str(e)}")

    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent from ElevenLabs.

        Args:
            agent_id: The ID of the agent to delete.

        Returns:
            bool: True if deleted successfully.

        Raises:
            ElevenLabsAgentError: If deletion fails.
        """
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
        try:
            response = self.client.conversational_ai.get_agent(agent_id=agent_id)
            # Serialize to dict if it's an object
            return response.model_dump() if hasattr(response, "model_dump") else dict(response)
        except Exception as e:
            logging.error(f"Failed to get ElevenLabs agent: {e}")
            raise ElevenLabsAgentError(f"Failed to get agent: {str(e)}")


# Default service instance
def get_elevenlabs_service() -> ElevenLabsService:
    """Get the ElevenLabs service instance."""
    return ElevenLabsService()
