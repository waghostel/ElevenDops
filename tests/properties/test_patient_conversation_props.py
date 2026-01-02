
import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

from backend.services.elevenlabs_service import ElevenLabsService, ElevenLabsAgentError

# **Feature: patient-conversation-text, Property 2: Session creation includes signed_url**
@given(agent_id=st.text(min_size=1))
def test_get_signed_url_returns_valid_format(agent_id):
    """Verify that get_signed_url returns a valid wss:// URL."""
    # Mock the client
    with patch("backend.services.elevenlabs_service.ElevenLabs") as MockClient:
        service = ElevenLabsService()
        
        # Configure the mock chain
        mock_response = MagicMock()
        mock_response.signed_url = f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={agent_id}&token=valid"
        service.client.conversational_ai.conversations.get_signed_url.return_value = mock_response

        url = service.get_signed_url(agent_id)
        
        assert url.startswith("wss://")
        assert f"agent_id={agent_id}" in url
        # Verify call
        service.client.conversational_ai.conversations.get_signed_url.assert_called_with(agent_id=agent_id)

# **Feature: patient-conversation-text, Property 4: Message response contains text and audio**
# Testing async method with Hypothesis requires explicit event loop handling or just standard pytest-asyncio for unit test style if strategies are simple.
# Since we are mocking heavily, a unit test style is more appropriate for the "structure" check.
# But keeping it property-based for "any inputs":

@given(
    agent_id=st.text(min_size=1),
    text=st.text(min_size=1),
    response_text=st.text(min_size=1),
    audio_bytes=st.binary(min_size=1)
)
@settings(deadline=None)  # Disable deadline for this test
def test_send_text_message_returns_text_and_audio(agent_id, text, response_text, audio_bytes):
    """Verify send_text_message returns correct tuple."""
    
    # We need to mock websockets.connect context manager
    with patch("backend.services.elevenlabs_service.websockets.connect") as mock_connect:
        service = ElevenLabsService()
        
        # Mock get_signed_url internal call
        service.get_signed_url = MagicMock(return_value="wss://test-url")
        
        # Setup Async Mock for websocket
        mock_ws = AsyncMock()
        
        # Simulate interaction: 
        # 1. recv() -> JSON with audio
        # 2. recv() -> JSON with text
        # 3. recv() -> TimeoutError (to break loop) or ConnectionClosed
        
        import json
        import base64
        
        # Create events
        audio_event = json.dumps({
            "audio_event": {
                "audio_base_64": base64.b64encode(audio_bytes).decode('utf-8')
            }
        })
        text_event = json.dumps({
            "agent_response_event": {
                "agent_response": response_text
            }
        })
        
        # Side effect for recv: yield events then raise TimeoutError
        async def side_effect(*args, **kwargs):
            if side_effect.counter == 0:
                side_effect.counter += 1
                return audio_event
            elif side_effect.counter == 1:
                side_effect.counter += 1
                return text_event
            else:
                # Trigger loop break
                raise asyncio.TimeoutError()
        side_effect.counter = 0
        
        mock_ws.recv.side_effect = side_effect
        mock_connect.return_value.__aenter__.return_value = mock_ws
        
        # Run async test
        # Note: Hypothesis doesn't natively run async functions without a runner
        # So we wrap in run.
        
        loop = asyncio.new_event_loop()
        try:
             result_text, result_audio = loop.run_until_complete(
                 service.send_text_message(agent_id, text)
             )
        finally:
            loop.close()
            
        assert result_text == response_text
        assert result_audio == audio_bytes
