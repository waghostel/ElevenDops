"""Audio API routes."""

import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from backend.models.schemas import (
    AudioGenerateRequest,
    AudioGenerateResponse,
    AudioListResponse,
    AudioMetadata,
    ScriptGenerateRequest,
    ScriptGenerateResponse,
    VoiceOption,
    ErrorResponse
)
from backend.services.audio_service import AudioService, get_audio_service
from backend.services.elevenlabs_service import ElevenLabsTTSError

router = APIRouter(prefix="/api/audio", tags=["audio"])


@router.post(
    "/generate-script",
    response_model=ScriptGenerateResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def generate_script(
    request: ScriptGenerateRequest, service: AudioService = Depends(get_audio_service)
):
    """Generate script from knowledge document."""
    try:
        script = await service.generate_script(knowledge_id=request.knowledge_id)
        return ScriptGenerateResponse(
            script=script,
            knowledge_id=request.knowledge_id,
            generated_at=datetime.utcnow(),
        )
    except Exception as e:
        logging.error(f"Script generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/generate",
    response_model=AudioGenerateResponse,
    responses={
        400: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def generate_audio(
    request: AudioGenerateRequest, service: AudioService = Depends(get_audio_service)
):
    """Generate audio from script."""
    try:
        metadata = await service.generate_audio(
            script=request.script,
            voice_id=request.voice_id,
            knowledge_id=request.knowledge_id,
        )
        return AudioGenerateResponse(
            audio_id=metadata.audio_id,
            audio_url=metadata.audio_url,
            knowledge_id=metadata.knowledge_id,
            voice_id=metadata.voice_id,
            duration_seconds=metadata.duration_seconds,
            script=metadata.script,
            created_at=metadata.created_at,
        )
    except ElevenLabsTTSError as e:
        logging.error(f"ElevenLabs audio generation failed: {e}")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logging.error(f"Audio generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{knowledge_id}",
    response_model=AudioListResponse,
    responses={500: {"model": ErrorResponse}},
)
async def get_audio_files(
    knowledge_id: str, service: AudioService = Depends(get_audio_service)
):
    """Get audio files for a knowledge document."""
    try:
        audio_files = await service.get_audio_files(knowledge_id=knowledge_id)
        return AudioListResponse(
            audio_files=audio_files,
            total_count=len(audio_files)
        )
    except Exception as e:
        logging.error(f"Failed to fetch audio history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/voices/list",
    response_model=List[VoiceOption],
    responses={502: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_available_voices(service: AudioService = Depends(get_audio_service)):
    """Get available voices."""
    try:
        return service.get_available_voices()
    except ElevenLabsTTSError as e:
         # Map internal service error to HTTP 502 Bad Gateway
        logging.error(f"Failed to fetch voices from ElevenLabs: {e}")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logging.error(f"Failed to fetch voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))
