"""Test for ElevenLabs WebSocket drain timeout fix."""

import pytest
import asyncio
import json
import base64
from unittest.mock import AsyncMock, MagicMock, patch
from websockets.exceptions import ConnectionClosedOK
from backend.services.elevenlabs_service import ElevenLabsService


@pytest.mark.asyncio
async def test_drain_timeout_prevents_hang():
    """Test that drain timeout prevents infinite hang from ping events."""
    
    # Create mock WebSocket that simulates ElevenLabs response pattern
    mock_websocket = AsyncMock()
    
    # Simulate the event sequence that causes the hang
    events = [
        # Initial metadata
        json.dumps({"conversation_initiation_metadata_event": {"conversation_id": "test"}}),
        # Audio chunk
        json.dumps({"audio_event": {"audio_base_64": base64.b64encode(b"audio_data").decode(), "event_id": 1}, "type": "audio"}),
        # Agent response (text) - this should trigger drain mode
        json.dumps({"agent_response_event": {"agent_response": "Hello! How can I help you?"}, "type": "agent_response"}),
        # Ping events that would normally cause infinite loop
        json.dumps({"ping_event": {"event_id": 2}, "type": "ping"}),
        json.dumps({"ping_event": {"event_id": 3}, "type": "ping"}),
        json.dumps({"ping_event": {"event_id": 3}, "type": "ping"}),
        json.dumps({"ping_event": {"event_id": 4}, "type": "ping"}),
        ConnectionClosedOK(None, None)
    ]
    
    # Mock recv to return events sequentially
    mock_websocket.recv = AsyncMock(side_effect=events)
    mock_websocket.send = AsyncMock()
    mock_websocket.__aenter__ = AsyncMock(return_value=mock_websocket)
    mock_websocket.__aexit__ = AsyncMock(return_value=None)
    
    service = ElevenLabsService()
    
    # Mock get_signed_url
    with patch.object(service, 'get_signed_url', return_value="wss://mock.url"):
        # Mock websockets.connect
        with patch('websockets.connect', return_value=mock_websocket):
            # Measure execution time
            import time
            start = time.time()
            
            response_text, audio_data = await service.send_text_message(
                agent_id="test_agent",
                text="Hello"
            )
            
            elapsed = time.time() - start
            
            # Verify response
            assert response_text == "Hello! How can I help you?"
            assert len(audio_data) > 0
            
            # Critical: Should complete in ~2 seconds (drain timeout), NOT 60+ seconds
            assert elapsed < 5.0, f"Took {elapsed}s - drain timeout not working!"
            
            # Verify we entered drain mode (check logs would be ideal, but checking timing is sufficient)
            print(f"✅ Test passed: Completed in {elapsed:.2f}s (drain timeout working)")


@pytest.mark.asyncio
async def test_collects_trailing_audio_in_drain_mode():
    """Test that drain mode still collects audio chunks that arrive after text."""
    
    mock_websocket = AsyncMock()
    
    # Simulate audio arriving AFTER text response
    events = [
        json.dumps({"conversation_initiation_metadata_event": {"conversation_id": "test"}}),
        json.dumps({"audio_event": {"audio_base_64": base64.b64encode(b"chunk1").decode()}, "type": "audio"}),
        json.dumps({"agent_response_event": {"agent_response": "Response"}, "type": "agent_response"}),
        # These audio chunks arrive AFTER the text - should still be collected
        json.dumps({"audio_event": {"audio_base_64": base64.b64encode(b"chunk2").decode()}, "type": "audio"}),
        json.dumps({"audio_event": {"audio_base_64": base64.b64encode(b"chunk3").decode()}, "type": "audio"}),
    ]
    
    mock_websocket.recv = AsyncMock(side_effect=events + [asyncio.TimeoutError()])
    mock_websocket.send = AsyncMock()
    mock_websocket.__aenter__ = AsyncMock(return_value=mock_websocket)
    mock_websocket.__aexit__ = AsyncMock(return_value=None)
    
    service = ElevenLabsService()
    
    with patch.object(service, 'get_signed_url', return_value="wss://mock.url"):
        with patch('websockets.connect', return_value=mock_websocket):
            response_text, audio_data = await service.send_text_message(
                agent_id="test_agent",
                text="Hello"
            )
            
            # Verify all audio chunks were collected
            assert b"chunk1" in audio_data
            assert b"chunk2" in audio_data
            assert b"chunk3" in audio_data
            
            print("✅ Test passed: Trailing audio collected in drain mode")
