"""Property-based tests for AgentService."""

import pytest
from hypothesis import given, strategies as st
from unittest.mock import MagicMock, patch

from backend.services.agent_service import AgentService
from backend.models.schemas import AgentCreateRequest, AnswerStyle, AgentResponse


@pytest.fixture
def mock_elevenlabs():
    return MagicMock()


from backend.services.data_service import MockDataService

@pytest.fixture
def agent_service(mock_elevenlabs):
    with patch("backend.services.agent_service.get_elevenlabs_service", return_value=mock_elevenlabs):
        # Inject mock data service
        service = AgentService(data_service=MockDataService())
        return service


@given(style=st.sampled_from(AnswerStyle))
def test_answer_style_mapping(style):
    """
    **Feature: agent-setup-page, Property 5: Answer style to prompt mapping**
    
    Validates: Requirements 4.2, 4.3, 4.4
    """
    # Pass mocks
    service = AgentService(
        data_service=MockDataService(),
        elevenlabs_service=MagicMock()
    )
    
    prompt = service._get_system_prompt(style)
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    
    # Check for style-specific keywords (English)
    if style == AnswerStyle.PROFESSIONAL:
        assert "professional" in prompt.lower() or "objective" in prompt.lower()
    elif style == AnswerStyle.FRIENDLY:
        assert "warm" in prompt.lower() or "friendly" in prompt.lower()
    elif style == AnswerStyle.EDUCATIONAL:
        assert "educator" in prompt.lower() or "teaching" in prompt.lower()


@pytest.mark.asyncio
async def test_create_agent_returns_valid_id(agent_service, mock_elevenlabs):
    """
    **Feature: agent-setup-page, Property 2: Agent creation returns valid ID**
    
    Validates: Requirements 1.4
    """
    # Setup mock
    mock_elevenlabs.create_agent.return_value = "el_agent_123"
    
    request = AgentCreateRequest(
        name="Test Agent",
        voice_id="voice123",
        answer_style=AnswerStyle.PROFESSIONAL,
        knowledge_ids=["doc1"],
        doctor_id="doc1"
    )
    
    response = await agent_service.create_agent(request)
    
    assert response.agent_id is not None
    assert len(response.agent_id) > 0
    assert response.elevenlabs_agent_id == "el_agent_123"
    assert response.knowledge_ids == ["doc1"]
    
    # Verify mock called correctly
    mock_elevenlabs.create_agent.assert_called_once()
    args, kwargs = mock_elevenlabs.create_agent.call_args
    assert kwargs['name'] == "Test Agent"
    assert kwargs['voice_id'] == "voice123"
    # assert knowledge_ids passed


@given(knowledge_ids=st.lists(st.uuids().map(str), min_size=0, max_size=5))
@pytest.mark.asyncio
async def test_knowledge_document_association_persistence(knowledge_ids):
    """
    **Feature: agent-setup-page, Property 3: Knowledge document association persistence**
    
    Validates: Requirements 2.2, 2.4
    """
    # Setup with mocked ElevenLabs service
    with patch("backend.services.agent_service.get_elevenlabs_service") as mock_get_service:
        mock_elevenlabs = MagicMock()
        mock_elevenlabs.create_agent.return_value = "el_agent_123"
        mock_get_service.return_value = mock_elevenlabs
        
        service = AgentService(data_service=MockDataService())
        # Reset in-memory storage removed
        
        request = AgentCreateRequest(
            name="Test Agent",
            voice_id="voice123",
            answer_style=AnswerStyle.PROFESSIONAL,
            knowledge_ids=knowledge_ids,
            doctor_id="doc1"
        )
        
        response = await service.create_agent(request)
        
        # Verify knowledge IDs are exactly preserved
        assert response.knowledge_ids == knowledge_ids
        assert len(response.knowledge_ids) == len(knowledge_ids)
        for kid in knowledge_ids:
            assert kid in response.knowledge_ids


@given(voice_id=st.uuids().map(str))
@pytest.mark.asyncio
async def test_voice_selection_persistence(voice_id):
    """
    **Feature: agent-setup-page, Property 4: Voice selection persistence**
    
    Validates: Requirements 3.2
    """
    # Setup with mocked ElevenLabs service
    with patch("backend.services.agent_service.get_elevenlabs_service") as mock_get_service:
        mock_elevenlabs = MagicMock()
        mock_elevenlabs.create_agent.return_value = "el_agent_123"
        mock_get_service.return_value = mock_elevenlabs
        
        service = AgentService(data_service=MockDataService())
        # Reset in-memory storage removed
        
        request = AgentCreateRequest(
            name="Test Agent",
            voice_id=voice_id,
            answer_style=AnswerStyle.PROFESSIONAL,
            knowledge_ids=[],
            doctor_id="doc1"
        )
        
        response = await service.create_agent(request)
        
        # Verify voice ID is exactly preserved
        assert response.voice_id == voice_id
        
        # Verify it was passed to ElevenLabs
        mock_elevenlabs.create_agent.assert_called_once()
        args, kwargs = mock_elevenlabs.create_agent.call_args
        assert kwargs['voice_id'] == voice_id 
