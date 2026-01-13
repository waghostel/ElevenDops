import pytest
import datetime
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.agent_service import get_agent_service, AgentService
from backend.models.schemas import AgentResponse, AnswerStyle, AgentUpdateRequest

# Mock AgentService
mock_agent_service = AsyncMock(spec=AgentService)

# Override dependency
app.dependency_overrides[get_agent_service] = lambda: mock_agent_service

client = TestClient(app)

@pytest.mark.asyncio
async def test_update_agent_valid_request():
    """Test successful agent update."""
    agent_id = "test_agent_id"
    update_data = {
        "name": "Updated Agent Name",
        "languages": ["en", "es"]
    }
    
    mock_response = AgentResponse(
        agent_id=agent_id,
        name="Updated Agent Name",
        knowledge_ids=["doc1"],
        voice_id="voice1",
        answer_style=AnswerStyle.PROFESSIONAL,
        languages=["en", "es"],
        elevenlabs_agent_id="eleven_id",
        doctor_id="doc_id",
        created_at=datetime.datetime.utcnow()
    )
    mock_agent_service.update_agent.return_value = mock_response

    response = client.put(f"/api/agent/{agent_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Agent Name"
    assert data["languages"] == ["en", "es"]
    mock_agent_service.update_agent.assert_called_once()


@pytest.mark.asyncio
async def test_update_agent_not_found():
    """Test update for non-existent agent."""
    agent_id = "non_existent"
    mock_agent_service.update_agent.side_effect = KeyError("Agent not found")
    
    response = client.put(f"/api/agent/{agent_id}", json={"name": "New Name"})
    
    assert response.status_code == 404
    assert "Agent not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_agent_validation_error():
    """Test update with invalid data (empty name)."""
    agent_id = "test_agent_id"
    
    # Empty name should fail validation before reaching service
    response = client.put(f"/api/agent/{agent_id}", json={"name": "   "})
    
    assert response.status_code == 422
