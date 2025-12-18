"""Service for audio generation and management."""

import logging
import uuid
from datetime import datetime
from typing import List

from backend.models.schemas import AudioMetadata, VoiceOption
from backend.services.elevenlabs_service import ElevenLabsService, get_elevenlabs_service

# In-memory storage for MVP
_AUDIO_STORE: List[AudioMetadata] = []


class AudioService:
    """Service for handling audio operations."""

    def __init__(self, elevenlabs_service: ElevenLabsService = None):
        """Initialize audio service.
        
        Args:
            elevenlabs_service: Optional injected service for testing.
        """
        self.elevenlabs_service = elevenlabs_service or get_elevenlabs_service()

    def generate_script(self, knowledge_id: str) -> str:
        """Generate a script from a knowledge document.
        
        Args:
            knowledge_id: ID of the knowledge document.
            
        Returns:
            str: Generated script content.
        """
        # MVP: Placeholder implementation using simple template
        # In a real implementation, this would fetch the document content and call an LLM
        logging.info(f"Generating script for knowledge_id: {knowledge_id}")
        return f"This is a generated script based on knowledge document {knowledge_id}. It is optimized for patient education."

    def generate_audio(self, script: str, voice_id: str, knowledge_id: str) -> AudioMetadata:
        """Generate audio from a script.
        
        Args:
            script: The script content.
            voice_id: The ElevenLabs voice ID.
            knowledge_id: The source knowledge document ID.
            
        Returns:
            AudioMetadata: Metadata of the generated audio.
        """
        logging.info(f"Generating audio for knowledge_id: {knowledge_id} with voice: {voice_id}")
        
        # Call ElevenLabs to generate audio bytes
        # In a real app we would upload this to Cloud Storage/S3 and get a URL
        # For MVP, we'll simulate a URL or base64 data URL if needed
        # But since we just need metadata, we return dummy URL
        
        try:
            # We call the service to ensure the integration works, even if we discard the bytes for MVP storage
            # In a real test we mock this
            _ = self.elevenlabs_service.text_to_speech(text=script, voice_id=voice_id)
        except Exception as e:
            logging.error(f"Error calling ElevenLabs: {e}")
            raise e

        audio_id = str(uuid.uuid4())
        # Mock URL for MVP
        audio_url = f"https://storage.googleapis.com/elevendops-audio/{audio_id}.mp3"
        
        metadata = AudioMetadata(
            audio_id=audio_id,
            audio_url=audio_url,
            knowledge_id=knowledge_id,
            voice_id=voice_id,
            duration_seconds=None, # ElevenLabs doesn't return duration directly in simple API
            script=script,
            created_at=datetime.utcnow()
        )
        
        _AUDIO_STORE.append(metadata)
        return metadata

    def get_audio_files(self, knowledge_id: str) -> List[AudioMetadata]:
        """Get all audio files for a knowledge document.
        
        Args:
            knowledge_id: ID of the knowledge document.
            
        Returns:
            List[AudioMetadata]: List of audio files.
        """
        return [audio for audio in _AUDIO_STORE if audio.knowledge_id == knowledge_id]

    def get_available_voices(self) -> List[VoiceOption]:
        """Get available voices.
        
        Returns:
            List[VoiceOption]: List of available voices.
        """
        voices_data = self.elevenlabs_service.get_voices()
        return [
            VoiceOption(
                voice_id=v["voice_id"],
                name=v["name"],
                description=v.get("description"),
                preview_url=v.get("preview_url")
            )
            for v in voices_data
        ]


# Default service instance
def get_audio_service() -> AudioService:
    """Get the audio service instance."""
    return AudioService()
