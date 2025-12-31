
import pytest
from unittest.mock import MagicMock, patch
from backend.services.elevenlabs_service import ElevenLabsService

@pytest.fixture
def mock_elevenlabs_client():
    with patch("backend.services.elevenlabs_service.ElevenLabs") as MockClient:
        instance = MockClient.return_value
        yield instance

@pytest.mark.asyncio
async def test_agent_model_selection_english(mock_elevenlabs_client):
    """Test that English-only agents use eleven_turbo_v2."""
    service = ElevenLabsService()
    # Force use_mock to False to use the mocked client instead of internal mock
    service.use_mock = False
    service.client = mock_elevenlabs_client
    
    # Configure mock response
    mock_response = MagicMock()
    mock_response.agent_id = "agent_123"
    mock_elevenlabs_client.conversational_ai.agents.create.return_value = mock_response

    # Call create_agent with English
    service.create_agent(
        name="English Agent",
        system_prompt="You are helpful.",
        knowledge_base=[],
        voice_id="voice_123",
        languages=["en"]
    )

    # Verify model_id
    call_args = mock_elevenlabs_client.conversational_ai.agents.create.call_args
    _, kwargs = call_args
    tts_config = kwargs["conversation_config"]["tts"]
    
    assert tts_config["model_id"] == "eleven_turbo_v2", "English agents must use eleven_turbo_v2"


@pytest.mark.asyncio
async def test_agent_model_selection_spanish(mock_elevenlabs_client):
    """Test that Spanish agents use eleven_turbo_v2_5."""
    service = ElevenLabsService()
    service.use_mock = False
    service.client = mock_elevenlabs_client
    
    mock_response = MagicMock()
    mock_response.agent_id = "agent_456"
    mock_elevenlabs_client.conversational_ai.agents.create.return_value = mock_response

    # Call create_agent with Spanish
    service.create_agent(
        name="Spanish Agent",
        system_prompt="Hola.",
        knowledge_base=[],
        voice_id="voice_123",
        languages=["es"]
    )

    # Verify model_id
    call_args = mock_elevenlabs_client.conversational_ai.agents.create.call_args
    _, kwargs = call_args
    tts_config = kwargs["conversation_config"]["tts"]
    
    assert tts_config["model_id"] == "eleven_turbo_v2_5", "Spanish agents must use eleven_turbo_v2_5"

@pytest.mark.asyncio
async def test_agent_model_selection_multilingual(mock_elevenlabs_client):
    """Test that Multilingual agents use eleven_turbo_v2_5."""
    service = ElevenLabsService()
    service.use_mock = False
    service.client = mock_elevenlabs_client
    
    mock_response = MagicMock()
    mock_response.agent_id = "agent_789"
    mock_elevenlabs_client.conversational_ai.agents.create.return_value = mock_response

    # Call create_agent with English and Spanish
    service.create_agent(
        name="Multi Agent",
        system_prompt="Hello Hola.",
        knowledge_base=[],
        voice_id="voice_123",
        languages=["en", "es"]
    )

    # Verify model_id
    call_args = mock_elevenlabs_client.conversational_ai.agents.create.call_args
    _, kwargs = call_args
    tts_config = kwargs["conversation_config"]["tts"]
    
    assert tts_config["model_id"] == "eleven_turbo_v2_5", "Multilingual agents must use eleven_turbo_v2_5"
