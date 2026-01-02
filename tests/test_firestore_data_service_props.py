import pytest
import asyncio
from typing import List
from datetime import datetime, timedelta
import inspect

from hypothesis import given, strategies as st, settings, HealthCheck, assume, strategies
from hypothesis.strategies import composite

from backend.services.data_service import get_data_service, DataServiceInterface, MockDataService
from backend.services.firestore_data_service import FirestoreDataService
from backend.models.schemas import (
    KnowledgeDocumentCreate, SyncStatus, DEFAULT_DOCUMENT_TAGS,
    AudioMetadata, AgentResponse, AnswerStyle,
    PatientSessionResponse, ConversationDetailSchema, ConversationMessageSchema,
    ConversationSummarySchema, KnowledgeDocumentResponse
)
import uuid

# Mark all as integration because stateless mocks cannot support persistence tests
pytestmark = [pytest.mark.asyncio, pytest.mark.integration]

# --- Strategies ---

s_tags = st.lists(st.sampled_from(DEFAULT_DOCUMENT_TAGS), min_size=1, max_size=3)
s_sync_status = st.sampled_from(list(SyncStatus))
s_answer_style = st.sampled_from(list(AnswerStyle))

@composite
def s_knowledge_document_create(draw):
    return KnowledgeDocumentCreate(
        disease_name=draw(st.text(min_size=1, max_size=50)),
        tags=draw(s_tags),
        raw_content=draw(st.text(min_size=10, max_size=1000)),
        doctor_id=draw(st.text(min_size=1, max_size=20))
    )

@composite
def s_audio_metadata(draw):
    now = datetime.now()
    return AudioMetadata(
        audio_id=str(uuid.uuid4()),
        knowledge_id=str(uuid.uuid4()),
        voice_id=draw(st.text(min_size=5, max_size=20)),
        script=draw(st.text(min_size=10, max_size=100)),
        audio_url=draw(st.text(min_size=10, max_size=100)),
        duration_seconds=draw(st.floats(min_value=1.0, max_value=300.0)),
        created_at=now
    )

@composite
def s_agent_response(draw):
    now = datetime.now()
    return AgentResponse(
        agent_id=str(uuid.uuid4()),
        name=draw(st.text(min_size=1, max_size=50)),
        knowledge_ids=[str(uuid.uuid4()) for _ in range(draw(st.integers(0, 3)))],
        voice_id=draw(st.text(min_size=5, max_size=20)),
        answer_style=draw(s_answer_style),
        elevenlabs_agent_id=draw(st.text(min_size=5, max_size=20)),
        doctor_id=draw(st.text(min_size=1, max_size=20)),
        created_at=now
    )

@composite
def s_conversation_detail(draw):
    now = datetime.now()
    return ConversationDetailSchema(
        conversation_id=str(uuid.uuid4()),
        patient_id=draw(st.text(min_size=1, max_size=20)),
        agent_id=str(uuid.uuid4()),
        agent_name=draw(st.text(min_size=1, max_size=20)),
        requires_attention=draw(st.booleans()),
        main_concerns=[draw(st.text(min_size=1, max_size=10)) for _ in range(2)],
        messages=[],
        answered_questions=[],
        unanswered_questions=[],
        duration_seconds=draw(st.integers(0, 300)),
        created_at=now
    )

# --- Tests ---

@pytest.mark.asyncio
async def test_property_1_interface_compliance():
    # **Feature: firestore-data-service, Property 1: Interface Implementation Completeness**
    # **Validates: Requirements 1.1, 1.2**
    
    # Test MockDataService implements the interface
    mock_service = MockDataService()
    assert isinstance(mock_service, DataServiceInterface)
    
    # Test FirestoreDataService implements the interface (check class definition)
    # We verify the class itself is a subclass without instantiating (avoids credential issues)
    assert issubclass(FirestoreDataService, DataServiceInterface)
    
    # Verify all abstract methods are implemented in both classes
    abstract_methods = [
        name for name, method in inspect.getmembers(DataServiceInterface, predicate=inspect.isfunction)
        if getattr(method, '__isabstractmethod__', False)
    ]
    
    for method_name in abstract_methods:
        assert hasattr(MockDataService, method_name), f"MockDataService missing {method_name}"
        assert hasattr(FirestoreDataService, method_name), f"FirestoreDataService missing {method_name}"
    
    # Try to instantiate FirestoreDataService only if credentials are available
    try:
        fs_service = FirestoreDataService()
        assert isinstance(fs_service, DataServiceInterface)
    except Exception as e:
        # Skip if credentials not available (emulator not running)
        if "credentials" in str(e).lower() or "connect" in str(e).lower():
            pytest.skip(f"Firestore not available: {e}")

@pytest.mark.asyncio
async def test_property_2_factory_singleton():
    # **Feature: firestore-data-service, Property 2: Factory Singleton Consistency**
    # **Validates: Requirements 2.4**
    s1 = get_data_service()
    s2 = get_data_service()
    assert s1 is s2

# To perform property tests against state operations, we need to clean up or use unique IDs.
# Since we might rely on the implementation, we can test just Mock for now to confirm logic?
# Or if we want to test Firestore, we need the emulator running.
# We will assume emulator is running.


@given(doc=s_knowledge_document_create())
@pytest.mark.asyncio
async def test_property_3_knowledge_document_persistence(doc):
    # **Feature: firestore-data-service, Property 3: Knowledge Document Persistence**
    # **Validates: Requirements 3.1, 3.2, 3.3**
    service = get_data_service()
    
    created_doc = await service.create_knowledge_document(doc)
    
    assert created_doc.disease_name == doc.disease_name
    assert created_doc.raw_content == doc.raw_content
    
    # Read back
    fetched_doc = await service.get_knowledge_document(created_doc.knowledge_id)
    assert fetched_doc is not None
    assert fetched_doc.knowledge_id == created_doc.knowledge_id
    assert fetched_doc.raw_content == doc.raw_content
    
    # Clean up
    await service.delete_knowledge_document(created_doc.knowledge_id)


@given(audio=s_audio_metadata())
@pytest.mark.asyncio
async def test_property_audio_persistence(audio):
    # **Feature: firestore-data-service, Property 6 partial: Delete Operation Completeness (Audio)**
    service = get_data_service()
    
    await service.save_audio_metadata(audio)
    
    fetched = await service.get_audio_file(audio.audio_id)
    assert fetched is not None
    assert fetched.audio_id == audio.audio_id
    
    # Test delete
    assert await service.delete_audio_file(audio.audio_id)
    assert await service.get_audio_file(audio.audio_id) is None


@given(agent=s_agent_response())
@pytest.mark.asyncio
async def test_property_agent_persistence(agent):
    # **Feature: firestore-data-service, Property 6 partial: Delete Operation Completeness (Agent)**
    service = get_data_service()
    
    await service.save_agent(agent)
    
    fetched = await service.get_agent(agent.agent_id)
    assert fetched is not None
    assert fetched.agent_id == agent.agent_id
    
    # Test delete
    assert await service.delete_agent(agent.agent_id)
    assert await service.get_agent(agent.agent_id) is None


@given(conv=s_conversation_detail())
@pytest.mark.asyncio
async def test_property_4_conversation_query_filtering(conv):
    # **Feature: firestore-data-service, Property 4: Conversation Query Filtering**
    # **Validates: Requirements 6.3, 6.5**
    service = get_data_service()
    
    await service.save_conversation(conv)
    
    # Test filter by exact patient_id
    logs = await service.get_conversation_logs(patient_id=conv.patient_id)
    # Note: there might be other conversations for this patient ID from previous tests if not cleaned
    assert any(l.conversation_id == conv.conversation_id for l in logs)
    
    # Test filter by non-existent patient_id
    # Use a UUID that shouldn't exist
    fake_id = str(uuid.uuid4())
    logs_empty = await service.get_conversation_logs(patient_id=fake_id)
    assert not any(l.conversation_id == conv.conversation_id for l in logs_empty)
    
    # Test requires_attention filter
    if conv.requires_attention:
        logs_attn = await service.get_conversation_logs(requires_attention_only=True)
        assert any(l.conversation_id == conv.conversation_id for l in logs_attn)
    else:
        # If it doesn't require attention, it shouldn't appear in attention_only list
        # But we must be careful if we created it previously and didn't clean up?
        # We rely on unique conversation IDs.
        logs_attn = await service.get_conversation_logs(requires_attention_only=True)
        assert not any(l.conversation_id == conv.conversation_id for l in logs_attn)

# Dashboard stats test requires cleaning up DB or knowing exact counts.
# We can skip it for now or implement it by creating N items, checking stats count increased by N.


@given(doc=s_knowledge_document_create())
@pytest.mark.asyncio
async def test_property_5_dashboard_stats_accuracy(doc):
    # **Feature: firestore-data-service, Property 5: Dashboard Statistics Accuracy**
    # **Validates: Requirements 7.1, 7.2, 7.3**
    service = get_data_service()
    
    initial_stats = await service.get_dashboard_stats()
    
    # Create one
    created = await service.create_knowledge_document(doc)
    
    new_stats = await service.get_dashboard_stats()
    
    assert new_stats.document_count == initial_stats.document_count + 1
    
    await service.delete_knowledge_document(created.knowledge_id)
    
    final_stats = await service.get_dashboard_stats()
    assert final_stats.document_count == initial_stats.document_count

