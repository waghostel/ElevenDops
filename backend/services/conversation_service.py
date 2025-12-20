"""Conversation service for business logic."""

from typing import List, Optional
from datetime import datetime

from backend.models.schemas import (
    ConversationSummarySchema,
    ConversationDetailSchema,
    ConversationMessageSchema,
    ConversationLogsResponseSchema,
    ConversationLogsQueryParams
)
from backend.services.data_service import DataServiceInterface, get_data_service
from backend.services.analysis_service import AnalysisService

class ConversationService:
    """Service for conversation log management and analysis."""
    
    def __init__(
        self, 
        data_service: Optional[DataServiceInterface] = None,
        analysis_service: Optional[AnalysisService] = None
    ):
        self.data_service = data_service or get_data_service()
        self.analysis_service = analysis_service or AnalysisService()

    async def get_conversations(
        self, query_params: ConversationLogsQueryParams
    ) -> ConversationLogsResponseSchema:
        """Get filtered conversation logs with statistics.
        
        Args:
            query_params: Filter parameters.
            
        Returns:
            Response containing list of conversations and aggregate counts.
        """
        # Get conversations from data service with basic filtering
        conversations = await self.data_service.get_conversation_logs(
            patient_id=query_params.patient_id,
            start_date=query_params.start_date,
            end_date=query_params.end_date,
            requires_attention_only=query_params.requires_attention_only
        )
        
        # Calculate statistics from the filtered result set
        total_count = len(conversations)
        attention_count = sum(1 for c in conversations if c.requires_attention)
        answered_total = sum(c.answered_count for c in conversations)
        unanswered_total = sum(c.unanswered_count for c in conversations)
        
        return ConversationLogsResponseSchema(
            conversations=conversations,
            total_count=total_count,
            attention_required_count=attention_count,
            total_answered=answered_total,
            total_unanswered=unanswered_total
        )

    async def get_conversation_details(
        self, conversation_id: str
    ) -> Optional[ConversationDetailSchema]:
        """Get detailed conversation view.
        
        Args:
            conversation_id: ID of the conversation.
            
        Returns:
            Detailed conversation object or None if not found.
        """
        detail = await self.data_service.get_conversation_detail(conversation_id)
        if not detail:
            return None
            
        # Ensure messages are sorted chronologically
        detail.messages.sort(key=lambda m: m.timestamp)
        
        return detail

    async def get_conversation_statistics(self) -> dict:
        """Get overall conversation dashboard statistics.
        
        Returns:
            Dictionary with statistical metrics.
        """
        # In a real app, this might be a single aggregated query
        # For MVP/Mock, we use the data service methods
        
        total = await self.data_service.get_conversation_count()
        avg_duration = await self.data_service.get_average_duration()
        attention_pct = await self.data_service.get_attention_percentage()
        
        formatted_duration = self.analysis_service.format_duration(int(avg_duration))
        
        return {
            "total_conversations": total,
            "average_duration_seconds": avg_duration,
            "average_duration_formatted": formatted_duration,
            "attention_percentage": round(attention_pct, 1)
        }
