from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime

from backend.models.schemas import ConversationLogsResponseSchema, ConversationDetailSchema
from backend.services.conversation_service import ConversationService

router = APIRouter()

def get_conversation_service() -> ConversationService:
    return ConversationService()

@router.get("/logs", response_model=ConversationLogsResponseSchema)
async def get_conversation_logs(
    patient_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    requires_attention_only: bool = False,
    service: ConversationService = Depends(get_conversation_service),
):
    """List conversation logs with filtering."""
    try:
        return await service.get_conversation_logs(
            patient_id=patient_id,
            start_date=start_date,
            end_date=end_date,
            requires_attention_only=requires_attention_only
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{conversation_id}", response_model=ConversationDetailSchema)
async def get_conversation_detail(
    conversation_id: str,
    service: ConversationService = Depends(get_conversation_service),
):
    """Get conversation details."""
    result = await service.get_conversation_detail(conversation_id)
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return result
