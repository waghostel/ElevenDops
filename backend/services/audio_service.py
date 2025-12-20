"""Service for audio generation and management."""

import logging
import uuid
from datetime import datetime
from typing import List, Optional

from backend.models.schemas import AudioMetadata, VoiceOption
from backend.services.elevenlabs_service import ElevenLabsService, get_elevenlabs_service
from backend.services.storage_service import StorageService, get_storage_service
from backend.services.firestore_data_service import FirestoreDataService

# In-memory storage is removed in favor of FirestoreDataService

class AudioService:
    """Service for handling audio operations."""

    def __init__(
        self, 
        elevenlabs_service: Optional[ElevenLabsService] = None,
        storage_service: Optional[StorageService] = None,
        data_service: Optional[FirestoreDataService] = None
    ):
        """Initialize audio service.
        
        Args:
            elevenlabs_service: Optional injected service for testing.
            storage_service: Optional injected service for storage operations.
            data_service: Optional injected service for data persistence.
        """
        self.elevenlabs_service = elevenlabs_service or get_elevenlabs_service()
        self.storage_service = storage_service or get_storage_service()
        # FirestoreDataService is a singleton class, so we can instantiate it directly if not provided
        self.data_service = data_service or FirestoreDataService()

    async def generate_script(self, knowledge_id: str) -> str:
        """Generate a script from a knowledge document.
        
        Args:
            knowledge_id: ID of the knowledge document.
            
        Returns:
            str: Generated script content.
            
        Raises:
            ValueError: If knowledge document not found.
        """
        logging.info(f"Generating script for knowledge_id: {knowledge_id}")
        
        doc = await self.data_service.get_knowledge_document(knowledge_id)
        if not doc:
            logging.warning(f"Knowledge document not found: {knowledge_id}")
            raise ValueError(f"Knowledge document {knowledge_id} not found")
            
        # MVP: Generate template-based script using the document content
        # We take the disease name and raw content to create a simple script
        script_content = f"Patient Education Script for {doc.disease_name}:\n\n"
        
        # Add intro if available in structured sections, else first 500 chars
        if doc.structured_sections and "Introduction" in doc.structured_sections:
            script_content += f"{doc.structured_sections['Introduction']}\n\n"
        else:
            # Fallback to raw content truncation
            limit = 1000
            content_snippet = doc.raw_content[:limit]
            if len(doc.raw_content) > limit:
                content_snippet += "..."
            script_content += content_snippet
            
        return script_content

    async def generate_audio(self, script: str, voice_id: str, knowledge_id: str) -> AudioMetadata:
        """Generate audio from a script.
        
        Args:
            script: The script content.
            voice_id: The ElevenLabs voice ID.
            knowledge_id: The source knowledge document ID.
            
        Returns:
            AudioMetadata: Metadata of the generated audio.
            
        Raises:
            Exception: If audio generation or upload fails.
        """
        logging.info(f"Generating audio for knowledge_id: {knowledge_id} with voice: {voice_id}")
        
        try:
            # 1. Calls ElevenLabs to generate audio bytes
            audio_bytes = self.elevenlabs_service.text_to_speech(text=script, voice_id=voice_id)
            
            # 2. Upload to Storage
            audio_id = str(uuid.uuid4())
            filename = f"{audio_id}.mp3"
            audio_url = self.storage_service.upload_audio(audio_bytes, filename)
            
            # 3. Save Metadata
            metadata = AudioMetadata(
                audio_id=audio_id,
                audio_url=audio_url,
                knowledge_id=knowledge_id,
                voice_id=voice_id,
                duration_seconds=None, # ElevenLabs simple API doesn't return duration
                script=script,
                created_at=datetime.utcnow()
            )
            
            await self.data_service.save_audio_metadata(metadata)
            
            return metadata
            
        except Exception as e:
            logging.error(f"Error in audio generation workflow: {e}")
            raise e

    async def get_audio_files(self, knowledge_id: str) -> List[AudioMetadata]:
        """Get all audio files for a knowledge document.
        
        Args:
            knowledge_id: ID of the knowledge document.
            
        Returns:
            List[AudioMetadata]: List of audio files.
        """
        return await self.data_service.get_audio_files(knowledge_id)

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
