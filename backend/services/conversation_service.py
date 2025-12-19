from datetime import datetime
from typing import Optional

from backend.models.schemas import (
    ConversationLogsResponseSchema,
    ConversationDetailSchema,
)
from backend.services.data_service import get_data_service


class ConversationService:
    """Service for managing conversation logs."""

    def __init__(self):
        self.data_service = get_data_service()

    async def get_conversation_logs(
        self,
        patient_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        requires_attention_only: bool = False,
    ) -> ConversationLogsResponseSchema:
        """Get conversation logs with statistics."""
        conversations = await self.data_service.get_conversation_logs(
            patient_id=patient_id,
            start_date=start_date,
            end_date=end_date,
            requires_attention_only=requires_attention_only,
        )

        total_count = len(conversations)
        attention_required_count = sum(1 for c in conversations if c.requires_attention)
        total_answered = sum(c.answered_count for c in conversations)
        total_unanswered = sum(c.unanswered_count for c in conversations)

        return ConversationLogsResponseSchema(
            conversations=conversations,
            total_count=total_count,
            attention_required_count=attention_required_count,
            total_answered=total_answered,
            total_unanswered=total_unanswered,
        )

    async def get_conversation_detail(
        self, conversation_id: str
    ) -> Optional[ConversationDetailSchema]:
        """Get conversation details."""
        return await self.data_service.get_conversation_detail(conversation_id)

    async def save_conversation(
        self, conversation: ConversationDetailSchema
    ) -> ConversationDetailSchema:
        """Save a new conversation."""
        return await self.data_service.save_conversation(conversation)
