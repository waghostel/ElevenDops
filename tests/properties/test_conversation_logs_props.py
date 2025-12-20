"""Property-based tests for conversation logs integration."""

import asyncio
from datetime import datetime, timedelta
from typing import List

import pytest
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import DataObject

from backend.models.schemas import (
    ConversationDetailSchema,
    ConversationMessageSchema,
    ConversationLogsQueryParams,
    ConversationSummarySchema
)
from backend.services.data_service import MockDataService
from backend.services.conversation_service import ConversationService
from backend.services.analysis_service import AnalysisService

# Strategies for generating data

@st.composite
def conversation_message_strategy(draw: st.DrawFn) -> ConversationMessageSchema:
    """Generate a random conversation message."""
    role = draw(st.sampled_from(["patient", "agent"]))
    content = draw(st.text(min_size=1, max_size=100))
    # Add question mark randomly if patient
    if role == "patient" and draw(st.booleans()):
        content += "?"
    
    return ConversationMessageSchema(
        role=role,
        content=content,
        timestamp=draw(st.datetimes(min_value=datetime(2024, 1, 1), max_value=datetime(2025, 1, 1))),
        audio_data=None 
    )

@st.composite
def conversation_detail_strategy(draw: st.DrawFn) -> ConversationDetailSchema:
    """Generate a random conversation detail."""
    messages = draw(st.lists(conversation_message_strategy(), min_size=0, max_size=10))
    messages.sort(key=lambda x: x.timestamp)
    
    # Calculate derived fields roughly to match logic
    created_at = messages[0].timestamp if messages else datetime.now()
    duration = 0
    if messages:
        duration = int((messages[-1].timestamp - messages[0].timestamp).total_seconds())
        
    return ConversationDetailSchema(
        conversation_id=draw(st.uuids()).hex,
        patient_id=draw(st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('L', 'N')))),
        agent_id="test_agent",
        agent_name="Test Agent",
        requires_attention=draw(st.booleans()),
        main_concerns=[],
        messages=messages,
        answered_questions=[],
        unanswered_questions=[],
        duration_seconds=duration,
        created_at=created_at
    )

@pytest.mark.asyncio
class TestConversationLogsProperties:
    
    @given(st.lists(conversation_detail_strategy(), min_size=1, max_size=20))
    @settings(max_examples=50)
    async def test_conversation_list_ordering(self, conversations: List[ConversationDetailSchema]):
        """Property 1: Conversation list ordering.
        
        For any set of conversation records, when retrieved from the system,
        they SHALL be ordered by creation date in descending order.
        """
        # Setup
        data_service = MockDataService()
        for conv in conversations:
            await data_service.save_conversation(conv)
            
        service = ConversationService(data_service=data_service)
        
        # Action
        result = await service.get_conversations(ConversationLogsQueryParams())
        
        # Verification
        retrieved_convs = result.conversations
        dates = [c.created_at for c in retrieved_convs]
        
        # Check descending order
        assert dates == sorted(dates, reverse=True)

    @given(st.lists(conversation_detail_strategy(), min_size=1, max_size=20))
    @settings(max_examples=50)
    async def test_requires_attention_filter(self, conversations: List[ConversationDetailSchema]):
        """Property 3: Attention filter accuracy.
        
        When filtered by "Requires Attention", all returned conversations
        SHALL have requires_attention set to true.
        """
        # Setup
        data_service = MockDataService()
        for conv in conversations:
            await data_service.save_conversation(conv)
            
        service = ConversationService(data_service=data_service)
        
        # Action
        result = await service.get_conversations(
            ConversationLogsQueryParams(requires_attention_only=True)
        )
        
        # Verification
        for conv in result.conversations:
            assert conv.requires_attention is True

    @given(st.lists(conversation_detail_strategy(), min_size=1, max_size=20))
    @settings(max_examples=50)
    async def test_all_conversations_completeness(self, conversations: List[ConversationDetailSchema]):
        """Property 4: All conversations filter completeness.
        
        When "All Conversations" (no filter) is applied, the result count 
        SHALL equal the total conversation count.
        """
        # Setup
        data_service = MockDataService()
        for conv in conversations:
            await data_service.save_conversation(conv)
            
        service = ConversationService(data_service=data_service)
        
        # Action
        result = await service.get_conversations(ConversationLogsQueryParams())
        
        # Verification
        assert result.total_count == len(conversations)
        assert len(result.conversations) == len(conversations)

    @given(conversation_detail_strategy())
    @settings(max_examples=50)
    async def test_message_history_completeness(self, conversation: ConversationDetailSchema):
        """Property 6: Message history completeness.
        
        Retrieving conversation details SHALL return all messages.
        """
        # Setup
        data_service = MockDataService()
        await data_service.save_conversation(conversation)
            
        service = ConversationService(data_service=data_service)
        
        # Action
        result = await service.get_conversation_details(conversation.conversation_id)
        
        # Verification
        assert result is not None
        assert len(result.messages) == len(conversation.messages)
        # Check content match for first message if exists
        if conversation.messages:
            assert result.messages[0].content == conversation.messages[0].content

    @given(st.lists(conversation_message_strategy(), min_size=1, max_size=20))
    @settings(max_examples=50)
    async def test_question_categorization(self, messages: List[ConversationMessageSchema]):
        """Property 9: Question categorization accuracy.
        
        A message SHALL be categorized as "answered" if and only if it is
        immediately followed by an agent response.
        """
        # Force messages to trigger logic
        # We need to manually construct a sequence to be sure of expected outcome
        # But we can test the function logic directly
        
        analysis = AnalysisService()
        answered, unanswered = analysis.categorize_questions(messages)
        
        # Verification logic
        # Re-implement verification logic strictly
        expected_answered = []
        expected_unanswered = []
        
        for i, msg in enumerate(messages):
            if msg.role == "patient" and ("?" in msg.content or "？" in msg.content):
                is_answered = False
                if i + 1 < len(messages):
                    if messages[i+1].role == "agent":
                        is_answered = True
                
                if is_answered:
                    expected_answered.append(msg.content)
                else:
                    expected_unanswered.append(msg.content)
        
        assert answered == expected_answered
        assert unanswered == expected_unanswered

    @given(st.lists(conversation_detail_strategy(), min_size=1, max_size=20))
    @settings(max_examples=50)
    async def test_statistics_calculation(self, conversations: List[ConversationDetailSchema]):
        """Property 12: Statistics calculation accuracy.
        
        Total conversations and attention percentage SHALL be calculated correctly.
        """
        # Setup
        data_service = MockDataService()
        for conv in conversations:
            await data_service.save_conversation(conv)
            
        service = ConversationService(data_service=data_service)
        
        # Action
        stats = await service.get_conversation_statistics()
        
        # Verification
        assert stats["total_conversations"] == len(conversations)
        
        expected_attention_count = sum(1 for c in conversations if c.requires_attention)
        expected_pct = (expected_attention_count / len(conversations)) * 100.0 if conversations else 0
        
        assert stats["attention_percentage"] == round(expected_pct, 1)

