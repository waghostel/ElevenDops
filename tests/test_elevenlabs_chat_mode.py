
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
import os
import json
import websockets
from websockets.exceptions import ConnectionClosedOK

from backend.services.elevenlabs_service import ElevenLabsService, ElevenLabsAgentError

# Set dummy env var before importing service might not be enough if it's top level, 
# but constructor uses os.getenv. 

@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {"ELEVENLABS_API_KEY": "fake_key", "USE_MOCK_ELEVENLABS": "false"}):
        yield

# Mock database service
@pytest.fixture
def mock_db_service():
    return AsyncMock()

@pytest.mark.asyncio
async def test_send_text_message_chat_mode(mock_db_service, mock_env):
    """Test send_text_message with text_only=True."""
    # Setup service with mock websockets
    service = ElevenLabsService()
    service.use_mock = False # We want to test the logic, even though we mock websockets
    
    agent_id = "test_agent_id"
    text = "Hello chat mode"
    
    # Mock websockets
    mock_ws = AsyncMock()
    mock_ws.send = AsyncMock()
    
    # We need to simulate the response cycle
    # First recv() returns empty to keep loop going or returns response immediately
    # Let's simulate a response with JUST text event, no audio event
    
    # Mock response data
    response_data = {
        "agent_response_event": {
            "agent_response": "This is a text response"
        }
    }
    
    mock_ws.recv.side_effect = [
        # First call returns response
        json.dumps(response_data),
        # Second call raises ConnectionClosed to exit loop
        ConnectionClosedOK(None, None)
    ]
    
    # Mock get_signed_url to avoid external API call
    service.get_signed_url = MagicMock(return_value="wss://mock.elevenlabs.io")
    
    with patch("websockets.connect", return_value=AsyncMock())as mock_connect:
        mock_connect.return_value.__aenter__.return_value = mock_ws
        
        response_text, audio_bytes = await service.send_text_message(agent_id, text, text_only=True)
        
        # Verification
        
        # 1. Verify payload contained try_trigger_generation=False
        expected_payload = {
            "text": text,
            "try_trigger_generation": False
        }
        
        # Get the call args of send
        args, _ = mock_ws.send.call_args
        sent_payload = json.loads(args[0])
        
        assert sent_payload["try_trigger_generation"] is False
        assert sent_payload["text"] == text
        
        # 2. Verify response text matches
        assert response_text == "This is a text response"
        
        # 3. Verify audio is empty
        assert audio_bytes == b""

@pytest.mark.asyncio
async def test_send_text_message_voice_mode(mock_db_service, mock_env):
    """Test send_text_message with text_only=False (default)."""
    service = ElevenLabsService()
    service.use_mock = False 
    
    agent_id = "test_agent_id"
    text = "Hello voice mode"
    
    mock_ws = AsyncMock()
    mock_ws.send = AsyncMock()
    
    # Mock response with audio
    response_data_audio = {
        "audio_event": {
            "audio_base_64": "UklGRi4AAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=" # Invalid wav header but some mock b64
        }
    }
    response_data_text = {
         "agent_response_event": {
            "agent_response": "Voice response"
        }
    }
    
    mock_ws.recv.side_effect = [
        json.dumps(response_data_text),
        json.dumps(response_data_audio),
        ConnectionClosedOK(None, None)
    ]
    
    # Mock get_signed_url
    service.get_signed_url = MagicMock(return_value="wss://mock.elevenlabs.io")
    
    with patch("websockets.connect", return_value=AsyncMock())as mock_connect:
        mock_connect.return_value.__aenter__.return_value = mock_ws
        mock_connect.return_value.__aenter__.return_value = mock_ws
        
        response_text, audio_bytes = await service.send_text_message(agent_id, text, text_only=False)
        
        # 1. Verify payload contained try_trigger_generation=True (default)
        args, _ = mock_ws.send.call_args
        sent_payload = json.loads(args[0])
        
        assert sent_payload["try_trigger_generation"] is True
        
        # 2. Verify text and audio
        assert response_text == "Voice response"
        assert len(audio_bytes) > 0

