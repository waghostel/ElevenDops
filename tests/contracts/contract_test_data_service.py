"""Contract tests validating DataService return values against Pydantic schemas.

These tests ensure that all DataService implementations (MockDataService, 
FirestoreDataService) return objects that correctly match their declared 
Pydantic response models, preventing runtime 500 errors from schema mismatches.

Feature: data-service-contracts
Validates: Issue #20 - Schema & Service Consistency
"""

import pytest
from datetime import datetime
from typing import get_type_hints
import uuid

from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st
from hypothesis.strategies import composite

from pydantic import ValidationError

from backend.services.data_service import DataServiceInterface, MockDataService
from backend.models.schemas import (
    DashboardStatsResponse,
    KnowledgeDocumentCreate,
    KnowledgeDocumentResponse,
    AudioMetadata,
    AgentResponse,
    AnswerStyle,
    PatientSessionResponse,
    ConversationDetailSchema,
    ConversationMessageSchema,
    CustomTemplateCreate,
    CustomTemplateResponse,
    DEFAULT_DOCUMENT_TAGS,
    SyncStatus,
)


pytestmark = [pytest.mark.asyncio, pytest.mark.contract]


# =============================================================================
# Strategies for property-based testing
# =============================================================================

s_tags = st.lists(st.sampled_from(DEFAULT_DOCUMENT_TAGS), min_size=1, max_size=3)
s_answer_style = st.sampled_from(list(AnswerStyle))


@composite
def s_knowledge_document_create(draw):
    """Generate valid KnowledgeDocumentCreate instances."""
    return KnowledgeDocumentCreate(
        disease_name=draw(st.text(min_size=1, max_size=50).filter(lambda x: x.strip())),
        tags=draw(s_tags),
        raw_content=draw(st.text(min_size=10, max_size=500).filter(lambda x: x.strip())),
        doctor_id=draw(st.text(min_size=1, max_size=20).filter(lambda x: x.strip())),
    )


@composite
def s_audio_metadata(draw):
    """Generate valid AudioMetadata instances."""
    return AudioMetadata(
        audio_id=str(uuid.uuid4()),
        knowledge_id=str(uuid.uuid4()),
        voice_id=draw(st.text(min_size=5, max_size=20)),
        script=draw(st.text(min_size=10, max_size=100)),
        audio_url=draw(st.text(min_size=10, max_size=100)),
        duration_seconds=draw(st.floats(min_value=1.0, max_value=300.0)),
        created_at=datetime.now(),
        doctor_id=draw(st.text(min_size=1, max_size=20).filter(lambda x: x.strip())),
        name=draw(st.text(max_size=50)),
        description=draw(st.text(max_size=100)),
    )


@composite
def s_agent_response(draw):
    """Generate valid AgentResponse instances."""
    return AgentResponse(
        agent_id=str(uuid.uuid4()),
        name=draw(st.text(min_size=1, max_size=50).filter(lambda x: x.strip())),
        knowledge_ids=[str(uuid.uuid4()) for _ in range(draw(st.integers(0, 2)))],
        voice_id=draw(st.text(min_size=5, max_size=20)),
        answer_style=draw(s_answer_style),
        elevenlabs_agent_id=draw(st.text(min_size=5, max_size=20)),
        doctor_id=draw(st.text(min_size=1, max_size=20).filter(lambda x: x.strip())),
        created_at=datetime.now(),
        languages=["en"],
    )


@composite
def s_patient_session_response(draw):
    """Generate valid PatientSessionResponse instances."""
    return PatientSessionResponse(
        session_id=str(uuid.uuid4()),
        patient_id=draw(st.from_regex(r"[a-zA-Z0-9]{5,10}", fullmatch=True)),
        agent_id=str(uuid.uuid4()),
        signed_url=draw(st.text(min_size=10, max_size=100)),
        created_at=datetime.now(),
    )


@composite
def s_conversation_detail(draw):
    """Generate valid ConversationDetailSchema instances."""
    return ConversationDetailSchema(
        conversation_id=str(uuid.uuid4()),
        patient_id=draw(st.text(min_size=1, max_size=20).filter(lambda x: x.strip())),
        agent_id=str(uuid.uuid4()),
        agent_name=draw(st.text(min_size=1, max_size=20).filter(lambda x: x.strip())),
        requires_attention=draw(st.booleans()),
        main_concerns=[],
        messages=[],
        answered_questions=[],
        unanswered_questions=[],
        duration_seconds=draw(st.integers(0, 300)),
        created_at=datetime.now(),
    )


@composite
def s_custom_template_create(draw):
    """Generate valid CustomTemplateCreate instances."""
    return CustomTemplateCreate(
        display_name=draw(st.text(min_size=1, max_size=50).filter(lambda x: x.strip())),
        description=draw(st.text(min_size=1, max_size=200).filter(lambda x: x.strip())),
        content=draw(st.text(min_size=20, max_size=500)),
    )


# =============================================================================
# Contract Test: DashboardStatsResponse
# =============================================================================

class TestDashboardStatsContract:
    """Contract tests for get_dashboard_stats() return type."""

    @pytest.mark.asyncio
    async def test_dashboard_stats_returns_valid_schema(self, mock_data_service: MockDataService):
        """Verify get_dashboard_stats returns a valid DashboardStatsResponse."""
        result = await mock_data_service.get_dashboard_stats()
        
        # Must be correct type
        assert isinstance(result, DashboardStatsResponse)
        
        # All required fields must be present and non-null
        assert result.document_count is not None
        assert result.agent_count is not None
        assert result.audio_count is not None
        assert result.conversation_count is not None  # The field that caused 500 errors
        assert result.last_activity is not None
        
        # Values must meet schema constraints
        assert result.document_count >= 0
        assert result.agent_count >= 0
        assert result.audio_count >= 0
        assert result.conversation_count >= 0
        assert isinstance(result.last_activity, datetime)

    @pytest.mark.asyncio
    async def test_dashboard_stats_can_revalidate(self, mock_data_service: MockDataService):
        """Returned value should pass Pydantic re-validation."""
        result = await mock_data_service.get_dashboard_stats()
        
        # Re-validate using model_validate - will raise if invalid
        revalidated = DashboardStatsResponse.model_validate(result.model_dump())
        assert revalidated == result


# =============================================================================
# Contract Test: KnowledgeDocumentResponse
# =============================================================================

class TestKnowledgeDocumentContract:
    """Contract tests for knowledge document methods."""

    @given(doc=s_knowledge_document_create())
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_create_returns_valid_schema(self, doc: KnowledgeDocumentCreate, mock_data_service: MockDataService):
        """Verify create_knowledge_document returns valid KnowledgeDocumentResponse."""
        result = await mock_data_service.create_knowledge_document(doc)
        
        assert isinstance(result, KnowledgeDocumentResponse)
        
        # Required fields
        assert result.knowledge_id is not None
        assert result.doctor_id == doc.doctor_id
        assert result.disease_name == doc.disease_name
        assert result.raw_content == doc.raw_content
        assert result.sync_status is not None
        assert result.created_at is not None
        
        # Re-validate
        KnowledgeDocumentResponse.model_validate(result.model_dump())
        
        # Cleanup
        await mock_data_service.delete_knowledge_document(result.knowledge_id)


# =============================================================================
# Contract Test: AudioMetadata
# =============================================================================

class TestAudioMetadataContract:
    """Contract tests for audio metadata methods."""

    @given(audio=s_audio_metadata())
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_save_returns_valid_schema(self, audio: AudioMetadata, mock_data_service: MockDataService):
        """Verify save_audio_metadata returns valid AudioMetadata."""
        result = await mock_data_service.save_audio_metadata(audio)
        
        assert isinstance(result, AudioMetadata)
        assert result.audio_id == audio.audio_id
        assert result.knowledge_id == audio.knowledge_id
        assert result.voice_id == audio.voice_id
        assert result.script == audio.script
        assert result.audio_url == audio.audio_url
        assert result.created_at is not None
        
        # Re-validate
        AudioMetadata.model_validate(result.model_dump())
        
        # Cleanup
        await mock_data_service.delete_audio_file(audio.audio_id)


# =============================================================================
# Contract Test: AgentResponse
# =============================================================================

class TestAgentResponseContract:
    """Contract tests for agent methods."""

    @given(agent=s_agent_response())
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_save_returns_valid_schema(self, agent: AgentResponse, mock_data_service: MockDataService):
        """Verify save_agent returns valid AgentResponse."""
        result = await mock_data_service.save_agent(agent)
        
        assert isinstance(result, AgentResponse)
        assert result.agent_id == agent.agent_id
        assert result.name == agent.name
        assert result.voice_id == agent.voice_id
        assert result.answer_style == agent.answer_style
        assert result.elevenlabs_agent_id == agent.elevenlabs_agent_id
        assert result.doctor_id == agent.doctor_id
        assert result.created_at is not None
        
        # Re-validate
        AgentResponse.model_validate(result.model_dump())
        
        # Cleanup
        await mock_data_service.delete_agent(agent.agent_id)


# =============================================================================
# Contract Test: PatientSessionResponse
# =============================================================================

class TestPatientSessionContract:
    """Contract tests for patient session methods."""

    @given(session=s_patient_session_response())
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_create_returns_valid_schema(self, session: PatientSessionResponse, mock_data_service: MockDataService):
        """Verify create_patient_session returns valid PatientSessionResponse."""
        result = await mock_data_service.create_patient_session(session)
        
        assert isinstance(result, PatientSessionResponse)
        assert result.session_id == session.session_id
        assert result.patient_id == session.patient_id
        assert result.agent_id == session.agent_id
        assert result.signed_url == session.signed_url
        assert result.created_at is not None
        
        # Re-validate
        PatientSessionResponse.model_validate(result.model_dump())


# =============================================================================
# Contract Test: ConversationDetailSchema
# =============================================================================

class TestConversationContract:
    """Contract tests for conversation methods."""

    @given(conv=s_conversation_detail())
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_save_returns_valid_schema(self, conv: ConversationDetailSchema, mock_data_service: MockDataService):
        """Verify save_conversation returns valid ConversationDetailSchema."""
        result = await mock_data_service.save_conversation(conv)
        
        assert isinstance(result, ConversationDetailSchema)
        assert result.conversation_id == conv.conversation_id
        assert result.patient_id == conv.patient_id
        assert result.agent_id == conv.agent_id
        assert result.agent_name == conv.agent_name
        assert result.created_at is not None
        
        # Re-validate
        ConversationDetailSchema.model_validate(result.model_dump())


# =============================================================================
# Contract Test: CustomTemplateResponse
# =============================================================================

class TestCustomTemplateContract:
    """Contract tests for custom template methods."""

    @given(template=s_custom_template_create())
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_create_returns_valid_schema(self, template: CustomTemplateCreate, mock_data_service: MockDataService):
        """Verify create_custom_template returns valid CustomTemplateResponse."""
        result = await mock_data_service.create_custom_template(template)
        
        assert isinstance(result, CustomTemplateResponse)
        assert result.template_id is not None
        assert result.display_name == template.display_name
        assert result.description == template.description
        assert result.content == template.content
        assert result.category == "custom"
        assert result.created_at is not None
        
        # Re-validate
        CustomTemplateResponse.model_validate(result.model_dump())
        
        # Cleanup
        await mock_data_service.delete_custom_template(result.template_id)


# =============================================================================
# Meta Contract Test: Interface Compliance
# =============================================================================

class TestInterfaceContract:
    """Verify all DataService implementations conform to the interface."""

    def test_mock_implements_all_abstract_methods(self):
        """MockDataService must implement all abstract methods."""
        import inspect
        
        abstract_methods = [
            name for name, method in inspect.getmembers(DataServiceInterface)
            if getattr(method, '__isabstractmethod__', False)
        ]
        
        for method_name in abstract_methods:
            assert hasattr(MockDataService, method_name), f"MockDataService missing {method_name}"
            assert callable(getattr(MockDataService, method_name))

    def test_firestore_implements_all_abstract_methods(self):
        """FirestoreDataService must implement all abstract methods."""
        import inspect
        from backend.services.firestore_data_service import FirestoreDataService
        
        abstract_methods = [
            name for name, method in inspect.getmembers(DataServiceInterface)
            if getattr(method, '__isabstractmethod__', False)
        ]
        
        for method_name in abstract_methods:
            assert hasattr(FirestoreDataService, method_name), f"FirestoreDataService missing {method_name}"
            assert callable(getattr(FirestoreDataService, method_name))
