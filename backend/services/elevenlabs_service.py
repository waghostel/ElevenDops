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


# Default service instance
def get_elevenlabs_service() -> ElevenLabsService:
    """Get the ElevenLabs service instance."""
    return ElevenLabsService()
