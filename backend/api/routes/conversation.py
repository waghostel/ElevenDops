"""API routes for conversation logs."""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query

from backend.models.schemas import (
    ConversationLogsResponseSchema,
    ConversationDetailSchema,
    ConversationLogsQueryParams,
    ConversationSummarySchema
)
from backend.services.conversation_service import ConversationService
from backend.services.data_service import DataServiceInterface, get_data_service
from backend.services.analysis_service import AnalysisService

router = APIRouter()

def get_conversation_service(
    data_service: DataServiceInterface = Depends(get_data_service)
) -> ConversationService:
    """Dependency for getting conversation service."""
    return ConversationService(data_service=data_service, analysis_service=AnalysisService())

@router.get("", response_model=ConversationLogsResponseSchema)
async def get_conversations(
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    requires_attention_only: bool = Query(False, description="Filter by attention status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    service: ConversationService = Depends(get_conversation_service)
):
    """Get list of conversations with statistics."""
    query_params = ConversationLogsQueryParams(
        patient_id=patient_id,
        requires_attention_only=requires_attention_only,
        start_date=start_date,
        end_date=end_date
    )
    return await service.get_conversations(query_params)

@router.get("/statistics", response_model=dict)
async def get_conversation_statistics(
    service: ConversationService = Depends(get_conversation_service)
):
    """Get overall conversation dashboard statistics."""
    return await service.get_conversation_statistics()

@router.get("/{conversation_id}", response_model=ConversationDetailSchema)
async def get_conversation_detail(
    conversation_id: str,
    service: ConversationService = Depends(get_conversation_service)
):
    """Get detailed conversation view."""
    detail = await service.get_conversation_details(conversation_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return detail
