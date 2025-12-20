"""Property tests for agent setup usage patterns.

Properties:
6. Agent deletion: Creating and then deleting an agent results in it being removed.
7. Metadata completeness: All agent metadata is correctly stored and retrieved.
"""

from unittest.mock import MagicMock, AsyncMock
import pytest
from hypothesis import given, strategies as st, settings
from backend.services.agent_service import AgentService
from backend.models.schemas import AgentCreateRequest, AnswerStyle, AgentResponse
from datetime import datetime

# Strategies
agent_names = st.text(min_size=1, max_size=50).filter(lambda x: x.strip())
knowledge_ids = st.lists(st.uuids().map(str), max_size=5)
voice_ids = st.uuids().map(str)
styles = st.sampled_from(AnswerStyle)

@pytest.mark.asyncio
async def test_agent_deletion_property():
    """
    **Feature: agent-setup-page, Property 6: Agent deletion removes from storage**
    
    Validates: Requirements 5.2, 6.4
    """
    # Mock Dependencies
    mock_data_service = AsyncMock()
    mock_elevenlabs_service = MagicMock()
    mock_elevenlabs_service.create_agent.return_value = "elevenlabs_agent_id_123"
    mock_elevenlabs_service.delete_agent.return_value = True
    
    # Simulate storage
    internal_store = {}
    
    async def mock_save_agent(agent):
        internal_store[agent.agent_id] = agent
        return agent
        
    async def mock_get_agents(doctor_id=None):
        return list(internal_store.values())
        
    async def mock_delete_agent(agent_id):
        if agent_id in internal_store:
            del internal_store[agent_id]
            return True
        return False

    mock_data_service.save_agent = AsyncMock(side_effect=mock_save_agent)
    mock_data_service.get_agents = AsyncMock(side_effect=mock_get_agents)
    mock_data_service.delete_agent = AsyncMock(side_effect=mock_delete_agent)

    # Initialize Service
    service = AgentService(
        data_service=mock_data_service, 
        elevenlabs_service=mock_elevenlabs_service
    )
    
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
    mock_elevenlabs_service.delete_agent.assert_called_once()


@settings(max_examples=50, deadline=None)
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
    # Mock Dependencies
    mock_data_service = AsyncMock()
    mock_elevenlabs_service = MagicMock()
    mock_elevenlabs_service.create_agent.return_value = "el_id_123"
    
    # Mock save to return the agent passed
    async def mock_save_agent(agent):
        return agent
    mock_data_service.save_agent = AsyncMock(side_effect=mock_save_agent)

    service = AgentService(
        data_service=mock_data_service, 
        elevenlabs_service=mock_elevenlabs_service
    )
    
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
