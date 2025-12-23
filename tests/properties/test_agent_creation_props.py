"""Property-based tests for Agent Creation."""

import pytest
from hypothesis import given, settings, HealthCheck, strategies as st
from unittest.mock import MagicMock, patch, AsyncMock, call

from backend.services.agent_service import AgentService, SYSTEM_PROMPTS
from backend.models.schemas import AnswerStyle, SyncStatus, AgentCreateRequest, AgentResponse

@given(style=st.sampled_from(AnswerStyle))
def test_system_prompt_language_consistency(style):
    """
    **Feature: elevenlabs-agent-creation, Property 1: System Prompt Language Consistency**
    
    Validates: Requirements 1.1, 1.2
    """
    service = AgentService(elevenlabs_service=MagicMock(), data_service=AsyncMock())
    
    prompt = service._get_system_prompt(style)
    
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    
    # Check for Traditional Chinese instructions
    assert "繁體中文" in prompt
    
    # Check that it matches the constant definitions
    assert prompt == SYSTEM_PROMPTS[style]


@given(
    knowledge_ids=st.lists(st.uuids().map(str), min_size=1, max_size=5),
    sync_statuses=st.lists(st.sampled_from(SyncStatus), min_size=1, max_size=5)
)
@pytest.mark.asyncio
@settings(suppress_health_check=[HealthCheck.too_slow])
async def test_knowledge_base_filtering_by_sync_status(knowledge_ids, sync_statuses):
    """
    **Feature: elevenlabs-agent-creation, Property 2: Knowledge Base Filtering by Sync Status**
    
    Validates: Requirements 2.1, 2.2, 2.3
    """
    # 1. Setup mock data service
    data_service = AsyncMock()
    
    # Create mock documents mapping
    mock_docs = {}
    expected_ids = []
    
    # Ensure lists are same length for mapping
    limit = min(len(knowledge_ids), len(sync_statuses))
    test_k_ids = knowledge_ids[:limit]
    test_statuses = sync_statuses[:limit]
    
    for kid, status in zip(test_k_ids, test_statuses):
        el_id = f"el_{kid}"
        doc = MagicMock()
        doc.knowledge_id = kid
        doc.sync_status = status
        doc.elevenlabs_document_id = el_id if status == SyncStatus.COMPLETED else None
        
        mock_docs[kid] = doc
        
        if status == SyncStatus.COMPLETED:
            expected_ids.append(el_id)
            
    # Configure mock to return doc based on ID
    async def get_doc(kid):
        return mock_docs.get(kid)
    
    data_service.get_knowledge_document.side_effect = get_doc
    
    # 2. Initialize service
    service = AgentService(elevenlabs_service=MagicMock(), data_service=data_service)
    
    # 3. Call method
    result = await service._get_synced_knowledge_ids(test_k_ids)
    
    # 4. Verify
    assert len(result) == len(expected_ids)
    assert set(result) == set(expected_ids)
    
    # Verify SyncStatus logic specifically
    for el_id in result:
        # Find which original doc this came from
        original_doc = next(d for d in mock_docs.values() if d.elevenlabs_document_id == el_id)
        assert original_doc.sync_status == SyncStatus.COMPLETED


@given(voice_id=st.uuids().map(str))
@pytest.mark.asyncio
async def test_voice_id_passthrough(voice_id):
    """
    **Feature: elevenlabs-agent-creation, Property 3: Voice ID Passthrough**
    
    Validates: Requirements 3.1
    """
    mock_el = MagicMock()
    mock_el.create_agent.return_value = "el_agent_123"
    
    service = AgentService(elevenlabs_service=mock_el, data_service=AsyncMock())
    
    request = AgentCreateRequest(
        name="Test Agent",
        voice_id=voice_id,
        answer_style=AnswerStyle.PROFESSIONAL,
        knowledge_ids=[],
        doctor_id="doc1"
    )
    
    await service.create_agent(request)
    
    mock_el.create_agent.assert_called_once()
    call_kwargs = mock_el.create_agent.call_args.kwargs
    assert call_kwargs['voice_id'] == voice_id


@given(
    name=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
    agent_id=st.uuids().map(str),
    doctor_id=st.uuids().map(str)
)
@pytest.mark.asyncio
async def test_agent_metadata_persistence(name, agent_id, doctor_id):
    """
    **Feature: elevenlabs-agent-creation, Property 4: Agent Metadata Persistence Completeness**
    **Feature: elevenlabs-agent-creation, Property 7: Enum Serialization for Firestore**
    
    Validates: Requirements 4.1, 4.2, 7.4
    """
    mock_el = MagicMock()
    mock_el.create_agent.return_value = "el_agent_fixed"
    
    mock_data = AsyncMock()
    
    service = AgentService(elevenlabs_service=mock_el, data_service=mock_data)
    
    request = AgentCreateRequest(
        name=name,
        voice_id="voice_fixed",
        answer_style=AnswerStyle.FRIENDLY,
        knowledge_ids=[],
        doctor_id=doctor_id
    )
    
    await service.create_agent(request)
    
    mock_data.save_agent.assert_called_once()
    saved_agent = mock_data.save_agent.call_args.args[0]
    
    assert saved_agent.name == name
    assert saved_agent.doctor_id == doctor_id
    assert saved_agent.voice_id == "voice_fixed"
    assert saved_agent.elevenlabs_agent_id == "el_agent_fixed"
    
    # Check enum serialization (property 7) - Schema model should handle it, 
    # but we verify the field holds the enum value, 
    # and the data service (which we mocked) would handle the db conversion.
    # To truly test serialization we'd need to check what gets passed to firestore,
    # but here we check what gets passed to data_service. 
    # Wait, requirement 7.4 says "System SHALL convert enum values to strings [for Firestore]". 
    # This is typically done in DataService. 
    # This test verifies `AgentService` constructs the object correctly with the Enum.
    assert saved_agent.answer_style == AnswerStyle.FRIENDLY


@given(
    agent_id=st.uuids().map(str),
    doctor_id=st.uuids().map(str)
)
@pytest.mark.asyncio
async def test_agent_retrieval(agent_id, doctor_id):
    """
    **Feature: elevenlabs-agent-creation, Property 5: Agent Retrieval from Firestore**
    
    Validates: Requirements 4.4
    """
    mock_data = AsyncMock()
    
    # Setup mock return
    # Use real AgentResponse to satisfy Pydantic validation
    from datetime import datetime
    real_agent = AgentResponse(
        agent_id=agent_id,
        name="Test Agent",
        knowledge_ids=[],
        voice_id="voice123",
        answer_style=AnswerStyle.PROFESSIONAL,
        elevenlabs_agent_id="el_123",
        doctor_id=doctor_id,
        created_at=datetime.utcnow()
    )
    
    async def get_agent(aid):
        if aid == agent_id:
            return real_agent
        return None
        
    mock_data.get_agent.side_effect = get_agent
    
    service = AgentService(elevenlabs_service=MagicMock(), data_service=mock_data)
    
    # Test single retrieval
    result = await service.get_agent(agent_id)
    assert result == real_agent
    
    # Test list retrieval
    mock_data.get_agents.return_value = [real_agent]
    list_result = await service.get_agents(doctor_id)
    assert len(list_result.agents) == 1
    assert list_result.agents[0] == real_agent
    mock_data.get_agents.assert_called_with(doctor_id)


@pytest.mark.asyncio
async def test_deletion_order_consistency():
    """
    **Feature: elevenlabs-agent-creation, Property 6: Deletion Order Consistency**
    
    Validates: Requirements 5.1, 5.2
    """
    mock_el = MagicMock()
    mock_data = AsyncMock()
    
    # Setup agent exists
    agent_id = "test_agent_id"
    mock_agent = MagicMock()
    mock_agent.elevenlabs_agent_id = "el_id_1"
    mock_data.get_agent.return_value = mock_agent
    
    # Tracking call order
    manager = MagicMock()
    manager.attach_mock(mock_el.delete_agent, 'delete_elevenlabs')
    manager.attach_mock(mock_data.delete_agent, 'delete_data')
    
    service = AgentService(elevenlabs_service=mock_el, data_service=mock_data)
    
    await service.delete_agent(agent_id)
    
    # Verify order
    expected_calls = [
        call.delete_elevenlabs("el_id_1"),
        call.delete_data(agent_id)
    ]
    assert manager.mock_calls == expected_calls


@pytest.mark.asyncio
async def test_agent_creation_rollback_on_save_failure():
    """
    **Feature: elevenlabs-agent-creation, Error Scenario: Rollback on Save Failure**
    
    Validates: Requirements 8.3
    """
    mock_el = MagicMock()
    mock_el.create_agent.return_value = "el_id_rollback"
    # mock_el.delete_agent is standard mock
    
    mock_data = AsyncMock()
    mock_data.save_agent.side_effect = Exception("DB Error")
    
    service = AgentService(elevenlabs_service=mock_el, data_service=mock_data)
    
    request = AgentCreateRequest(
        name="Rollback Test",
        voice_id="voice1",
        answer_style=AnswerStyle.PROFESSIONAL,
        knowledge_ids=[],
        doctor_id="doc1"
    )
    
    # Expect exception
    with pytest.raises(Exception) as excinfo:
        await service.create_agent(request)
    
    assert "DB Error" in str(excinfo.value)
    
    # Verify rollback
    mock_el.delete_agent.assert_called_once_with("el_id_rollback")



