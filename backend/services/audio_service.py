"""Service for audio generation and management."""

import logging
import uuid
from datetime import datetime
from typing import List, Optional, AsyncGenerator

from backend.models.schemas import AudioMetadata, VoiceOption
from backend.services.elevenlabs_service import ElevenLabsService, get_elevenlabs_service
from backend.services.storage_service import StorageService, get_storage_service, get_signed_url
from backend.services.data_service import get_data_service, DataServiceInterface

from backend.services.script_generation_service import ScriptGenerationService
from backend.services.prompt_template_service import get_prompt_template_service
from backend.config import get_default_script_prompt, GEMINI_MODELS
from backend.models.schemas import TemplateConfig

# In-memory storage is removed in favor of FirestoreDataService

class AudioService:
    """Service for handling audio operations."""

    def __init__(
        self, 
        elevenlabs_service: Optional[ElevenLabsService] = None,
        storage_service: Optional[StorageService] = None,
        data_service: Optional[DataServiceInterface] = None,
        script_service: Optional[ScriptGenerationService] = None
    ):
        """Initialize audio service.
        
        Args:
            elevenlabs_service: Optional injected service for testing.
            storage_service: Optional injected service for storage operations.
            data_service: Optional injected service for data persistence.
        """
        self.elevenlabs_service = elevenlabs_service or get_elevenlabs_service()
        self.storage_service = storage_service or get_storage_service()
        # Use get_data_service() to respect environment variables (mock vs real DB)
        self.data_service = data_service or get_data_service()
        self.script_service = script_service or ScriptGenerationService()

    async def generate_script(
        self, 
        knowledge_id: str, 
        model_name: str = "gemini-2.5-flash",
        custom_prompt: Optional[str] = None,
        template_config: Optional[TemplateConfig] = None
    ) -> dict:
        """Generate a script from a knowledge document.
        
        Args:
            knowledge_id: ID of the knowledge document.
            model_name: Gemini model to use.
            custom_prompt: Optional custom prompt (legacy support).
            template_config: Optional template configuration for building prompt.
            
        Returns:
            dict: {"script": str, "model_used": str}
            
        Raises:
            ValueError: If knowledge document not found.
        """
        logging.info(f"Generating script for knowledge_id: {knowledge_id}")
        
        doc = await self.data_service.get_knowledge_document(knowledge_id)
        if not doc:
            logging.warning(f"Knowledge document not found: {knowledge_id}")
            raise ValueError(f"Knowledge document {knowledge_id} not found")
        
        # Build prompt: prefer template_config > custom_prompt > default
        if template_config:
            template_service = get_prompt_template_service()
            prompt = await template_service.build_prompt(
                template_ids=template_config.template_ids,
                quick_instructions=template_config.quick_instructions,
                preferred_languages=template_config.preferred_languages,
                speaker1_languages=template_config.speaker1_languages,
                speaker2_languages=template_config.speaker2_languages,
                target_duration_minutes=template_config.target_duration_minutes,
                is_multi_speaker=template_config.is_multi_speaker,
            )
            logging.info(f"Using template config with {len(template_config.template_ids)} templates, multi_speaker={template_config.is_multi_speaker}")
        else:
            prompt = custom_prompt or get_default_script_prompt()
        
        # Map friendly name to API model name
        api_model_name = GEMINI_MODELS.get(model_name, model_name)
        
        try:
            result = await self.script_service.generate_script(
                knowledge_content=doc.raw_content,
                model_name=api_model_name, 
                prompt=prompt
            )
            return {
                "script": result["script"],
                "model_used": result["model_used"]
            }
        except Exception as e:
            # Capture detailed error info for user feedback
            error_type = type(e).__name__
            error_msg = str(e) if str(e) else repr(e)
            generation_error = f"{error_type}: {error_msg}" if error_msg else error_type
            
            logging.error(f"AI generation failed, falling back to legacy template. Error: {generation_error}")
            
            # Fallback logic (legacy)
            script_content = f"Patient Education Script for {doc.disease_name}:\n\n"
            if doc.structured_sections and "Introduction" in doc.structured_sections:
                script_content += f"{doc.structured_sections['Introduction']}\n\n"
            else:
                limit = 5000
                content_snippet = doc.raw_content[:limit]
                if len(doc.raw_content) > limit:
                    content_snippet += "..."
                script_content += content_snippet
            
            return {
                "script": script_content,
                "model_used": "legacy_fallback",
                "generation_error": generation_error
            }

    async def generate_script_stream(
        self, 
        knowledge_id: str, 
        model_name: str = "gemini-2.5-flash",
        custom_prompt: Optional[str] = None,
        template_config: Optional[TemplateConfig] = None
    ) -> AsyncGenerator[dict, None]:
        """Stream script generation with real-time token feedback.
        
        Args:
            knowledge_id: ID of the knowledge document.
            model_name: Gemini model to use.
            custom_prompt: Optional custom prompt (legacy support).
            template_config: Optional template configuration for building prompt.
            
        Yields:
            dict events: {"type": "token", "content": "..."} 
                         {"type": "complete", "script": "...", "model_used": "..."}
                         {"type": "error", "message": "..."}
        """
        logging.info(f"Streaming script generation for knowledge_id: {knowledge_id}")
        
        # Fetch knowledge document
        doc = await self.data_service.get_knowledge_document(knowledge_id)
        if not doc:
            logging.warning(f"Knowledge document not found: {knowledge_id}")
            yield {"type": "error", "message": f"Knowledge document {knowledge_id} not found"}
            return
        
        # Build prompt: prefer template_config > custom_prompt > default
        if template_config:
            template_service = get_prompt_template_service()
            prompt = await template_service.build_prompt(
                template_ids=template_config.template_ids,
                quick_instructions=template_config.quick_instructions,
                preferred_languages=template_config.preferred_languages,
                speaker1_languages=template_config.speaker1_languages,
                speaker2_languages=template_config.speaker2_languages,
                target_duration_minutes=template_config.target_duration_minutes,
                is_multi_speaker=template_config.is_multi_speaker,
            )
            logging.info(f"Using template config with {len(template_config.template_ids)} templates, multi_speaker={template_config.is_multi_speaker}")
        else:
            prompt = custom_prompt or get_default_script_prompt()
        
        # Map friendly name to API model name
        api_model_name = GEMINI_MODELS.get(model_name, model_name)
        
        # Delegate to script service streaming
        async for event in self.script_service.generate_script_stream(
            knowledge_content=doc.raw_content,
            model_name=api_model_name,
            prompt=prompt
        ):
            yield event

    def stream_audio(self, audio_id: str):
        """Stream audio file content.
        
        This is a sync function because it returns a sync generator from
        storage_service.get_file_stream(). FastAPI's StreamingResponse
        handles sync generators efficiently via thread pool.
        
        Args:
            audio_id: ID of the audio file to stream.
            
        Yields:
             Bytes chunks of the audio file.
        """
        filename = f"{audio_id}.mp3"
        storage_path = f"audio/{filename}"
        
        return self.storage_service.get_file_stream(storage_path)

    async def generate_audio(
        self, 
        script: str, 
        voice_id: str, 
        knowledge_id: str, 
        doctor_id: str = "default_doctor",
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> AudioMetadata:
        """Generate audio from a script.
        
        Args:
            script: The script content.
            voice_id: The ElevenLabs voice ID.
            knowledge_id: The source knowledge document ID.
            doctor_id: ID of the doctor generating the audio.
            name: Optional user-friendly name. If None, auto-generate from document.
            description: Optional description of the audio content.
            
        Returns:
            AudioMetadata: Metadata of the generated audio with signed URL.
            
        Raises:
            Exception: If audio generation or upload fails.
        """
        logging.info(f"Generating audio for knowledge_id: {knowledge_id} with voice: {voice_id}")
        
        try:
            # 1. Calls ElevenLabs to generate audio bytes
            audio_bytes = self.elevenlabs_service.text_to_speech(text=script, voice_id=voice_id)
            
            # 2. Upload to Storage (returns storage path for production, URL for emulator)
            audio_id = str(uuid.uuid4())
            filename = f"{audio_id}.mp3"
            storage_path_or_url = self.storage_service.upload_audio(audio_bytes, filename)
            
            # 3. Auto-generate name if not provided
            if not name:
                doc = await self.data_service.get_knowledge_document(knowledge_id)
                timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
                name = f"{doc.disease_name if doc else 'Audio'} - {timestamp}"
            
            # 4. Save Metadata with storage path (not the signed URL)
            metadata = AudioMetadata(
                audio_id=audio_id,
                audio_url=storage_path_or_url,  # Store path for production, URL for emulator
                knowledge_id=knowledge_id,
                voice_id=voice_id,
                duration_seconds=None,  # ElevenLabs simple API doesn't return duration
                script=script,
                created_at=datetime.utcnow(),
                doctor_id=doctor_id,
                name=name,
                description=description or ""
            )
            
            await self.data_service.save_audio_metadata(metadata)
            
            # 5. Return metadata with signed URL for immediate playback
            # If storage path is already a full URL (mock/emulator), use it.
            # If it's a relative path (production), generate a signed URL.
            playback_url = storage_path_or_url
            if not storage_path_or_url.startswith("http"):
                # It's a storage path like "audio/uuid.mp3", generate signed URL
                playback_url = get_signed_url(storage_path_or_url)

            return AudioMetadata(
                audio_id=metadata.audio_id,
                audio_url=playback_url,
                knowledge_id=metadata.knowledge_id,
                voice_id=metadata.voice_id,
                duration_seconds=metadata.duration_seconds,
                script=metadata.script,
                created_at=metadata.created_at,
                doctor_id=metadata.doctor_id,
                name=metadata.name,
                description=metadata.description
            )
            
        except Exception as e:
            logging.error(f"Error in audio generation workflow: {e}")
            raise e

    async def get_audio_files(
        self, 
        knowledge_id: Optional[str] = None, 
        doctor_id: Optional[str] = None
    ) -> List[AudioMetadata]:
        """Get audio files filtered by knowledge_id and/or doctor_id.
        
        Audio URLs are signed on retrieval for secure, temporary access.
        
        Args:
            knowledge_id: Optional filter by knowledge document ID.
            doctor_id: Optional filter by doctor ID.
            
        Returns:
            List[AudioMetadata]: List of audio files with signed URLs.
        """
        audio_files = await self.data_service.get_audio_files(
            knowledge_id=knowledge_id, doctor_id=doctor_id
        )
        
        # Sign URLs for each audio file
        # Signed GCS URLs are accessible directly by browsers without going through our backend
        signed_audio_files = []
        for audio in audio_files:
            signed_url = get_signed_url(audio.audio_url)
            signed_audio_files.append(AudioMetadata(
                audio_id=audio.audio_id,
                audio_url=signed_url,
                knowledge_id=audio.knowledge_id,
                voice_id=audio.voice_id,
                duration_seconds=audio.duration_seconds,
                script=audio.script,
                created_at=audio.created_at,
                doctor_id=audio.doctor_id,
                name=audio.name,
                description=audio.description
            ))
        
        return signed_audio_files

    async def delete_audio(self, audio_id: str) -> bool:
        """Delete an audio file.
        
        Removes both the audio file from storage and its metadata from the database.
        
        Args:
            audio_id: ID of the audio file to delete.
            
        Returns:
            bool: True if deletion successful, False if audio not found.
        """
        logging.info(f"Deleting audio: {audio_id}")
        
        try:
            # 1. Get audio metadata to find storage path
            audio_files = await self.data_service.get_audio_files()
            audio_to_delete = None
            for audio in audio_files:
                if audio.audio_id == audio_id:
                    audio_to_delete = audio
                    break
            
            if not audio_to_delete:
                logging.warning(f"Audio {audio_id} not found in database")
                return False
            
            # 2. Delete from storage
            filename = f"{audio_id}.mp3"
            
            try:
                self.storage_service.delete_audio(filename)
                logging.info(f"Deleted audio file from storage: {filename}")
            except Exception as e:
                logging.warning(f"Failed to delete audio file from storage: {e}")
                # Continue with database deletion even if storage deletion fails
            
            # 3. Delete metadata from database
            success = await self.data_service.delete_audio_file(audio_id)
            if success:
                logging.info(f"Deleted audio metadata from database: {audio_id}")
            else:
                logging.warning(f"Failed to delete audio metadata: {audio_id}")
            
            return success
            
        except Exception as e:
            logging.error(f"Error deleting audio {audio_id}: {e}")
            return False

    async def update_audio_metadata(
        self,
        audio_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> AudioMetadata:
        """Update audio metadata (name and/or description).
        
        Args:
            audio_id: ID of the audio to update.
            name: New name (optional).
            description: New description (optional).
            
        Returns:
            Updated AudioMetadata.
            
        Raises:
            ValueError: If audio not found.
        """
        logging.info(f"Updating audio metadata: {audio_id}")
        
        # Get existing audio
        audio_files = await self.data_service.get_audio_files()
        audio_to_update = next((a for a in audio_files if a.audio_id == audio_id), None)
        
        if not audio_to_update:
            raise ValueError(f"Audio {audio_id} not found")
        
        # Create updated metadata object
        updated_metadata = AudioMetadata(
            audio_id=audio_to_update.audio_id,
            audio_url=audio_to_update.audio_url,
            knowledge_id=audio_to_update.knowledge_id,
            voice_id=audio_to_update.voice_id,
            duration_seconds=audio_to_update.duration_seconds,
            script=audio_to_update.script,
            created_at=audio_to_update.created_at,
            doctor_id=audio_to_update.doctor_id,
            name=name if name is not None else audio_to_update.name,
            description=description if description is not None else audio_to_update.description
        )
        
        # Save to database
        saved_metadata = await self.data_service.save_audio_metadata(updated_metadata)
        logging.info(f"Updated audio metadata: {audio_id}")
        return saved_metadata

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
