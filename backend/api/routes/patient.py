from fastapi import APIRouter, HTTPException, Depends
from backend.models.schemas import (
    PatientSessionCreate,
    PatientSessionResponse,
    PatientMessageRequest,
    PatientMessageResponse,
    SessionEndResponse,
    ErrorResponse,
)
from backend.services.patient_service import PatientService
from backend.services.elevenlabs_service import ElevenLabsServiceError

router = APIRouter()

def get_patient_service() -> PatientService:
    """Dependency to get PatientService instance."""
    return PatientService()

@router.post(
    "/session",
    response_model=PatientSessionResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Create a new patient session"
)
async def create_session(
    request: PatientSessionCreate,
    service: PatientService = Depends(get_patient_service)
):
    """Create a new conversation session with an agent."""
    try:
        return await service.create_session(request)
    except ElevenLabsServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/session/{session_id}/message",
    response_model=PatientMessageResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Send a message to the agent"
)
async def send_message(
    session_id: str,
    request: PatientMessageRequest,
    service: PatientService = Depends(get_patient_service)
):
    """Send a text message and get an audio response."""
    try:
        return await service.send_message(session_id, request.message, chat_mode=request.chat_mode)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ElevenLabsServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/session/{session_id}/end",
    response_model=SessionEndResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="End a patient session"
)
async def end_session(
    session_id: str,
    service: PatientService = Depends(get_patient_service)
):
    """End the conversation session."""
    try:
        return await service.end_session(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
