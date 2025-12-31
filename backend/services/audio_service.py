"""Service for audio generation and management."""

import logging
import uuid
from datetime import datetime
from typing import List, Optional, AsyncGenerator

from backend.models.schemas import AudioMetadata, VoiceOption
from backend.services.elevenlabs_service import ElevenLabsService, get_elevenlabs_service
from backend.services.storage_service import StorageService, get_storage_service
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
        """Stream script generation from a knowledge document.
        
        This method streams tokens as they are generated, keeping the
        connection alive and providing real-time feedback to avoid
        timeout issues with large documents.
        
        Args:
            knowledge_id: ID of the knowledge document.
            model_name: Gemini model to use.
            custom_prompt: Optional custom prompt (legacy support).
            template_config: Optional template configuration for building prompt.
            
        Yields:
            dict events with type: 'token', 'complete', or 'error'
        """
        logging.info(f"Starting streaming script generation for knowledge_id: {knowledge_id}")
        
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
                system_prompt_override=template_config.system_prompt_override,
                preferred_languages=template_config.preferred_languages,
                speaker1_languages=template_config.speaker1_languages,
                speaker2_languages=template_config.speaker2_languages,
                target_duration_minutes=template_config.target_duration_minutes,
                is_multi_speaker=template_config.is_multi_speaker,
            )
            logging.info(f"Using template config with {len(template_config.template_ids)} templates, multi_speaker={template_config.is_multi_speaker}")
        else:
            prompt = custom_prompt or get_default_script_prompt()
        
        api_model_name = GEMINI_MODELS.get(model_name, model_name)
        
        async for event in self.script_service.generate_script_stream(
            knowledge_content=doc.raw_content,
            model_name=api_model_name,
            prompt=prompt
        ):
            yield event

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
