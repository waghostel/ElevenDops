
import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import MagicMock, AsyncMock
import asyncio
from datetime import datetime, timedelta

from backend.services.patient_service import PatientService
from backend.services.data_service import MockDataService
from backend.models.schemas import (
    PatientSessionResponse, 
    ConversationMessageSchema,
    ConversationDetailSchema
)

# Shared strategies
@st.composite
def conversation_strategy(draw):
    """Generates a list of messages with timestamps."""
    start_time = datetime(2023, 1, 1, 12, 0, 0)
    messages = []
    
    # Random number of exchanges (0 to 10)
    num_exchanges = draw(st.integers(min_value=0, max_value=10))
    
    current_time = start_time
    
    for i in range(num_exchanges):
        # Patient message
        patient_text = draw(st.text(min_size=1))
        # 50% chance to be a question
        if draw(st.booleans()):
            patient_text += "?"
            
        messages.append(ConversationMessageSchema(
            role="patient",
            content=patient_text,
            timestamp=current_time
        ))
        
        current_time += timedelta(seconds=draw(st.integers(min_value=1, max_value=60)))
        
        # Agent response (maybe)
        # 80% chance agent responds
        if draw(st.booleans()):
            agent_text = draw(st.text(min_size=1))
            messages.append(ConversationMessageSchema(
                role="agent",
                content=agent_text,
                timestamp=current_time,
                audio_data="mock_audio"
            ))
            current_time += timedelta(seconds=draw(st.integers(min_value=1, max_value=60)))
            
    return messages

@settings(deadline=None)
@given(messages=conversation_strategy())
def test_conversation_analysis_question_categorization(messages):
    """**Property 6: Question categorization correctness**
    
    Validates that:
    1. Messages with '?' from patient are treated as questions.
    2. Questions followed by agent message are 'answered'.
    3. Questions NOT followed by agent message are 'unanswered'.
    """
    session_id = "test_session"
    
    # Mock Data Service with pre-loaded messages
    mock_data = MockDataService()
    mock_data.get_patient_session = AsyncMock(return_value=PatientSessionResponse(
        session_id=session_id, patient_id="p1", agent_id="a1", signed_url="url", created_at=datetime.now()
    ))
    mock_data.get_session_messages = AsyncMock(return_value=messages)
    
    # Mock Conversation service to capture save call
    mock_conv_service = MagicMock()
    mock_conv_service.save_conversation = AsyncMock()
    
    service = PatientService(
        data_service=mock_data,
        conversation_service=mock_conv_service,
        elevenlabs_service=MagicMock()
    )
    
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(service.end_session(session_id))
        
        # Verify save_conversation called
        if messages:
            assert mock_conv_service.save_conversation.called
            saved_detail: ConversationDetailSchema = mock_conv_service.save_conversation.call_args[0][0]
            
            # Re-implement verification logic to check against service output
            expected_answered = 0
            expected_unanswered = 0
            
            for i, msg in enumerate(messages):
                if msg.role == 'patient' and '?' in msg.content:
                    # Check if next is agent
                    is_answered = False
                    if i + 1 < len(messages) and messages[i+1].role == 'agent':
                        is_answered = True
                        expected_answered += 1
                    else:
                        expected_unanswered += 1
            
            assert len(saved_detail.answered_questions) == expected_answered
            assert len(saved_detail.unanswered_questions) == expected_unanswered
            
    finally:
        loop.close()

@settings(deadline=None)
@given(messages=conversation_strategy())
def test_requires_attention_flag(messages):
    """**Property 7: Requires attention flag correctness**
    
    Validates that requires_attention is True IFF there are unanswered questions.
    """
    session_id = "test_session"
    mock_data = MockDataService()
    mock_data.get_patient_session = AsyncMock(return_value=PatientSessionResponse(
        session_id=session_id, patient_id="p1", agent_id="a1", signed_url="url", created_at=datetime.now()
    ))
    mock_data.get_session_messages = AsyncMock(return_value=messages)
    
    mock_conv_service = MagicMock()
    mock_conv_service.save_conversation = AsyncMock()
    
    service = PatientService(
        data_service=mock_data,
        conversation_service=mock_conv_service,
        elevenlabs_service=MagicMock()
    )
    
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(service.end_session(session_id))
        
        if messages:
            saved_detail: ConversationDetailSchema = mock_conv_service.save_conversation.call_args[0][0]
            
            has_unanswered = len(saved_detail.unanswered_questions) > 0
            assert saved_detail.requires_attention == has_unanswered

    finally:
        loop.close()

@settings(deadline=None)
@given(messages=conversation_strategy())
def test_duration_calculation(messages):
    """**Property 8: Duration calculation correctness**
    
    Validates duration equals (last_msg - first_msg) time delta.
    """
    session_id = "test_session"
    mock_data = MockDataService()
    mock_data.get_patient_session = AsyncMock(return_value=PatientSessionResponse(
        session_id=session_id, patient_id="p1", agent_id="a1", signed_url="url", created_at=datetime.now()
    ))
    mock_data.get_session_messages = AsyncMock(return_value=messages)
    
    mock_conv_service = MagicMock()
    mock_conv_service.save_conversation = AsyncMock()
    
    service = PatientService(
        data_service=mock_data,
        conversation_service=mock_conv_service,
        elevenlabs_service=MagicMock()
    )
    
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(service.end_session(session_id))
        
        expected_duration = 0
        if messages:
             expected_duration = int((messages[-1].timestamp - messages[0].timestamp).total_seconds())
             
        assert str(expected_duration) in result.conversation_summary["duration"]
        
        if messages:
            saved_detail: ConversationDetailSchema = mock_conv_service.save_conversation.call_args[0][0]
            assert saved_detail.duration_seconds == expected_duration

    finally:
        loop.close()

@settings(deadline=None)
@given(messages=conversation_strategy())
def test_end_session_summary_completeness(messages):
    """**Property 9: End session summary completeness**
    
    Validates that end_session returns a summary object with all required fields:
    - session_id
    - patient_id
    - duration
    - message_count
    """
    session_id = "test_session"
    patient_id = "p1"
    mock_data = MockDataService()
    mock_data.get_patient_session = AsyncMock(return_value=PatientSessionResponse(
        session_id=session_id, patient_id=patient_id, agent_id="a1", signed_url="url", created_at=datetime.now()
    ))
    mock_data.get_session_messages = AsyncMock(return_value=messages)
    
    mock_conv_service = MagicMock()
    mock_conv_service.save_conversation = AsyncMock()
    
    service = PatientService(
        data_service=mock_data,
        conversation_service=mock_conv_service,
        elevenlabs_service=MagicMock()
    )
    
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(service.end_session(session_id))
        
        # Verify result structure (SessionEndResponse)
        assert result.success is True
        
        # Check conversation_summary dict fields
        summary = result.conversation_summary
        assert "session_id" in summary
        assert "patient_id" in summary
        assert "duration" in summary
        assert "message_count" in summary
        
        assert summary["session_id"] == session_id
        assert summary["patient_id"] == patient_id
        assert summary["message_count"] == len(messages)
        # Duration verification is covered by Property 8, but we ensure it's present here
        assert isinstance(summary["duration"], str)

    finally:
        loop.close()

@settings(deadline=None)
@given(messages=conversation_strategy())
def test_conversation_persistence(messages):
    """**Property 10: Conversation log round-trip**
    
    Validates that the full conversation object is passed to save_conversation.
    """
    session_id = "test_session"
    mock_data = MockDataService()
    mock_data.get_patient_session = AsyncMock(return_value=PatientSessionResponse(
        session_id=session_id, patient_id="p1", agent_id="a1", signed_url="url", created_at=datetime.now()
    ))
    mock_data.get_session_messages = AsyncMock(return_value=messages)
    
    mock_conv_service = MagicMock()
    mock_conv_service.save_conversation = AsyncMock()
    
    service = PatientService(
        data_service=mock_data,
        conversation_service=mock_conv_service,
        elevenlabs_service=MagicMock()
    )
    
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(service.end_session(session_id))
        
        if messages:
            mock_conv_service.save_conversation.assert_called_once()
            saved_detail: ConversationDetailSchema = mock_conv_service.save_conversation.call_args[0][0]
            
            assert saved_detail.conversation_id == session_id
            assert len(saved_detail.messages) == len(messages)
            assert saved_detail.messages[0].content == messages[0].content

    finally:
        loop.close()
