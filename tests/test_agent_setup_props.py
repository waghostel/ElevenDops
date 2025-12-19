"""Property tests for agent setup usage patterns.

Properties:
6. Agent deletion: Creating and then deleting an agent results in it being removed.
7. Metadata completeness: All agent metadata is correctly stored and retrieved.
"""

from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from hypothesis import given, strategies as st
from backend.services.agent_service import AgentService
from backend.models.schemas import AgentCreateRequest, AnswerStyle

# Strategies
agent_names = st.text(min_size=1, max_size=50).filter(lambda x: x.strip())
knowledge_ids = st.lists(st.uuids().map(str), max_size=5)
voice_ids = st.uuids().map(str)
styles = st.sampled_from(AnswerStyle)

@pytest.fixture
def mock_elevenlabs():
    mock = MagicMock()
    mock.create_agent.return_value = "elevenlabs_agent_id_123"
    mock.get_agent.return_value = {"name": "Test Agent"}
    mock.delete_agent.return_value = True
    return mock

@pytest.mark.asyncio
async def test_agent_deletion_property():
    """
    **Feature: agent-setup-page, Property 6: Agent deletion removes from storage**
    
    Validates: Requirements 5.2, 6.4
    """
    # Setup with mocked ElevenLabs service
    with patch("backend.services.agent_service.get_elevenlabs_service") as mock_get_service:
        mock_elevenlabs = MagicMock()
        mock_elevenlabs.create_agent.return_value = "elevenlabs_agent_id_123"
        mock_elevenlabs.delete_agent.return_value = True
        mock_get_service.return_value = mock_elevenlabs
        
        service = AgentService()
        # Reset in-memory storage
        service._agents = {}
        
        request = AgentCreateRequest(
            name="Test Agent",
            voice_id="voice_123",
            answer_style=AnswerStyle.PROFESSIONAL
        )
        
        # Action
        agent = await service.create_agent(request)
        
        # Verify created
        stored = await service.get_agents()
        assert len(stored.agents) == 1
        assert stored.agents[0].agent_id == agent.agent_id
        
        # Delete
        result = await service.delete_agent(agent.agent_id)
        assert result is True
        
        # Verify deleted
        stored_after = await service.get_agents()
        assert len(stored_after.agents) == 0
        mock_elevenlabs.delete_agent.assert_called_once()

@given(
    name=agent_names,
    k_ids=knowledge_ids,
    v_id=voice_ids,
    style=styles
)
@pytest.mark.asyncio
async def test_agent_metadata_completeness(name, k_ids, v_id, style):
    """
    **Feature: agent-setup-page, Property 7: Agent creation stores all metadata**
    
    Validates: Requirements 6.1
    """
    # Setup with mocked ElevenLabs service
    with patch("backend.services.agent_service.get_elevenlabs_service") as mock_get_service:
        mock_elevenlabs = MagicMock()
        mock_elevenlabs.create_agent.return_value = "el_id_123"
        mock_get_service.return_value = mock_elevenlabs
        
        service = AgentService()
        # Reset in-memory storage
        service._agents = {}
        
        request = AgentCreateRequest(
            name=name,
            knowledge_ids=k_ids,
            voice_id=v_id,
            answer_style=style
        )
        
        # Action
        agent = await service.create_agent(request)
        
        # Verify
        assert agent.name == name
        assert agent.knowledge_ids == k_ids
        assert agent.voice_id == v_id
        assert agent.answer_style == style
        assert agent.elevenlabs_agent_id == "el_id_123"
        assert agent.agent_id is not None
        assert agent.created_at is not None
