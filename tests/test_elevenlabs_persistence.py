import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch
from backend.services.websocket_manager import WebSocketConnectionManager, ConnectionState

@pytest.mark.asyncio
async def test_websocket_persistence_lifecycle():
    """Test that the manager maintains connection state across messages."""
    manager = WebSocketConnectionManager()
    session_id = "test_session_123"
    signed_url = "wss://mock.elevenlabs.io/v1/conv"
    agent_id = "agent_abc"

    # 1. Mock the WebSocket connection
    mock_ws = AsyncMock()
    # Simple AsyncMock needs to return a context manager or itself if used as one
    mock_ws.__aenter__ = AsyncMock(return_value=mock_ws)
    mock_ws.__aexit__ = AsyncMock(return_value=None)
    
    # Simulate initialization handshake
    # 1st recv: initiation metadata
    # 2nd recv: agent response (greeting)
    mock_ws.recv.side_effect = [
        json.dumps({"type": "conversation_initiation_metadata"}),
        json.dumps({
            "type": "agent_response", 
            "agent_response_event": {
                "agent_response": "Hello!"
            }
        })
    ]

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = mock_ws
        # 2. Test create_connection
        success = await manager.create_connection(session_id, signed_url, agent_id)
        assert success is True
        assert manager.has_connection(session_id) is True
        
        # Verify initialization message was sent
        init_call_args = mock_ws.send.call_args_list[0]
        init_payload = json.loads(init_call_args[0][0])
        assert init_payload["type"] == "conversation_initiation_client_data"
        assert init_payload["conversation_config_override"]["conversation"]["text_only"] is True

    # 3. Test send_message (Persistence Check)
    # mock_ws.recv for next message
    mock_ws.recv.side_effect = [
        json.dumps({
            "type": "agent_response", 
            "agent_response_event": {
                "agent_response": "I am persistent."
            }
        })
    ]
    
    response_text, audio = await manager.send_message(session_id, "Who are you?")
    assert response_text == "I am persistent."
    assert audio is None
    
    # Verify the message count increased
    state = manager._connections[session_id]
    assert state.message_count == 1

    # 4. Test Ping/Pong handling during send_message
    mock_ws.recv.side_effect = [
        json.dumps({"type": "ping", "ping_event": {"event_id": "p1"}}),
        json.dumps({
            "type": "agent_response", 
            "agent_response_event": {
                "agent_response": "Ping pong worked."
            }
        })
    ]
    
    response_text, audio = await manager.send_message(session_id, "Testing ping.")
    assert response_text == "Ping pong worked."
    
    # Verify pong was sent
    pong_call = [call for call in mock_ws.send.call_args_list if "pong" in call[0][0]]
    assert len(pong_call) > 0
    pong_payload = json.loads(pong_call[0][0][0])
    assert pong_payload["type"] == "pong"
    assert pong_payload["event_id"] == "p1"

    # 5. Test close_connection
    await manager.close_connection(session_id)
    assert manager.has_connection(session_id) is False
    assert mock_ws.close.called
