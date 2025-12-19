
import pytest
from hypothesis import given, strategies as st
from hypothesis import settings, HealthCheck
from backend.services.data_service import MockDataService
from backend.models.schemas import ConversationDetailSchema, ConversationMessageSchema
from backend.services.conversation_service import ConversationService
from backend.services.patient_service import PatientService
from backend.models.schemas import ConversationDetailSchema, ConversationMessageSchema, PatientSessionResponse
from datetime import datetime
import asyncio

# Strategies
# Use naive datetimes to avoid comparison issues in mock service logic
datetime_st = st.datetimes(min_value=datetime(2000, 1, 1), max_value=datetime(2030, 1, 1), timezones=st.none())

message_st = st.builds(
    ConversationMessageSchema,
    role=st.sampled_from(["patient", "agent"]),
    content=st.text(min_size=1),
    timestamp=datetime_st,
    is_answered=st.one_of(st.none(), st.booleans())
)

conversation_detail_st = st.builds(
    ConversationDetailSchema,
    conversation_id=st.uuids().map(str),
    patient_id=st.text(min_size=1, max_size=20),
    agent_id=st.text(min_size=1),
    agent_name=st.text(min_size=1),
    requires_attention=st.booleans(),
    main_concerns=st.lists(st.text(), max_size=5),
    messages=st.lists(message_st, max_size=10),
    answered_questions=st.lists(st.text(), max_size=5),
    unanswered_questions=st.lists(st.text(), max_size=5),
    duration_seconds=st.integers(min_value=0),
    created_at=datetime_st
)

@pytest.fixture
def data_service():
    service = MockDataService()
    service._conversation_details = {}  # Clean state
    return service

@given(conversation=conversation_detail_st)
@pytest.mark.asyncio
async def test_save_and_retrieve_detail(conversation):
    """
    Sanity check: verifying save and retrieve works.
    """
    service = MockDataService()
    service._conversation_details = {}
    
    await service.save_conversation(conversation)
    retrieved = await service.get_conversation_detail(conversation.conversation_id)
    assert retrieved == conversation

@given(conversations=st.lists(conversation_detail_st, min_size=1, max_size=20), 
       filter_patient_id=st.text(min_size=1))
@pytest.mark.asyncio
async def test_patient_id_filter(conversations, filter_patient_id):
    """
    **Feature: conversation-logs-page, Property 2: Patient ID Filter Correctness**
    **Validates: Requirements 2.2, 2.4**
    """
    service = MockDataService()
    service._conversation_details = {}
    
    # Save all
    for c in conversations:
        await service.save_conversation(c)
        
    results = await service.get_conversation_logs(patient_id=filter_patient_id)
    
    for summary in results:
        # Check that the result contains the filter string (case-insensitive)
        assert filter_patient_id.lower() in summary.patient_id.lower()

@given(conversations=st.lists(conversation_detail_st, min_size=1, max_size=20),
       start_date=datetime_st,
       end_date=datetime_st)
@pytest.mark.asyncio
async def test_date_range_filter(conversations, start_date, end_date):
    """
    **Feature: conversation-logs-page, Property 3: Date Range Filter Correctness**
    **Validates: Requirements 3.2, 3.3, 3.4**
    """
    service = MockDataService()
    service._conversation_details = {}
    
    for c in conversations:
        await service.save_conversation(c)

    # Handle case where start > end which usually results in empty list or specific logic
    # but here we just test that IF we get results, they are valid.
    
    results = await service.get_conversation_logs(start_date=start_date, end_date=end_date)
    
    for summary in results:
        if start_date:
            assert summary.created_at >= start_date
        if end_date:
             assert summary.created_at <= end_date

@given(conversations=st.lists(conversation_detail_st, min_size=1, max_size=20))
@pytest.mark.asyncio
async def test_attention_filter(conversations):
    """
    **Feature: conversation-logs-page, Property 4: Attention Filter Correctness**
    **Validates: Requirements 4.2**
    """
    service = MockDataService()
    service._conversation_details = {}
    
    for c in conversations:
        await service.save_conversation(c)
        
    results = await service.get_conversation_logs(requires_attention_only=True)
    
    for summary in results:
        assert summary.requires_attention is True

@given(conversations=st.lists(conversation_detail_st, min_size=1, max_size=20))
@pytest.mark.asyncio
async def test_statistics_accuracy(conversations):
    """
    **Feature: conversation-logs-page, Property 5: Statistics Accuracy**
    **Validates: Requirements 5.2, 5.3**
    """
    service = ConversationService()
    # Manually override the data service for isolation
    mock_ds = MockDataService()
    mock_ds._conversation_details = {}
    service.data_service = mock_ds
    
    for c in conversations:
        await service.save_conversation(c)
        
    response = await service.get_conversation_logs()
    
    assert response.total_count == len(conversations)
    assert response.attention_required_count == sum(1 for c in conversations if c.requires_attention)
    assert response.total_answered == sum(len(c.answered_questions) for c in conversations)
    assert response.total_answered == sum(len(c.answered_questions) for c in conversations)
    assert response.total_unanswered == sum(len(c.unanswered_questions) for c in conversations)

@given(messages=st.lists(message_st, min_size=1, max_size=20))
@pytest.mark.asyncio
async def test_question_categorization_consistency(messages):
    """
    **Feature: conversation-logs-page, Property 7: Question Categorization Consistency**
    **Validates: Requirements 7.3, 7.4**
    """
    mock_ds = MockDataService()
    mock_ds._sessions = {} # Ensure clean
    mock_ds._session_messages = {}
    mock_ds._conversation_details = {}
    
    # Setup session
    mock_ds._sessions['test_session'] = PatientSessionResponse(
        session_id='test_session', patient_id='p1', agent_id='a1', signed_url='url', created_at=datetime.now()
    )
    # Sort messages by timestamp to matching logic in end_session
    messages.sort(key=lambda m: m.timestamp)
    mock_ds._session_messages['test_session'] = messages
    
    conv_service = ConversationService()
    conv_service.data_service = mock_ds
    
    patient_srv = PatientService(data_service=mock_ds, conversation_service=conv_service)
    
    await patient_srv.end_session('test_session')
    
    detail = await mock_ds.get_conversation_detail('test_session')
    
    if detail:
        total_questions = sum(1 for m in messages if m.role == 'patient' and '?' in m.content)
        assert len(detail.answered_questions) + len(detail.unanswered_questions) == total_questions
