import asyncio
import logging
import json
import base64
import time
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass, field

import websockets
from websockets.client import WebSocketClientProtocol


@dataclass
class ConnectionState:
    """Tracks the state of a WebSocket connection."""

    websocket: WebSocketClientProtocol
    agent_id: str
    signed_url: str
    created_at: float = field(default_factory=time.time)
    message_count: int = 0
    is_active: bool = True


class WebSocketConnectionManager:
    """Manages persistent WebSocket connections for patient sessions.

    This class maintains WebSocket connections keyed by session_id, allowing
    multiple messages to be sent through the same connection for multi-turn
    conversations with context preservation.

    Attributes:
        _connections: Dictionary mapping session_id to ConnectionState.
        _lock: Async lock for thread-safe access to connections.
    """

    def __init__(self):
        """Initialize the connection manager."""
        self._connections: Dict[str, ConnectionState] = {}
        self._lock = asyncio.Lock()

    async def create_connection(
        self,
        session_id: str,
        signed_url: str,
        agent_id: str,
    ) -> bool:
        """Create and store a new WebSocket connection for a session.

        Args:
            session_id: Unique session identifier.
            signed_url: The signed WebSocket URL from ElevenLabs.
            agent_id: The ElevenLabs agent ID.

        Returns:
            bool: True if connection was successfully established.

        Raises:
            Exception: If connection fails.
        """
        async with self._lock:
            # Close existing connection if any
            if session_id in self._connections:
                await self._close_connection_internal(session_id)

            try:
                logging.info(f"Creating WebSocket connection for session {session_id}")
                websocket = await websockets.connect(signed_url)

                # Send initialization event using correct SDK protocol
                # Type must be "conversation_initiation_client_data"
                # conversation_config_override must be a top-level key in the payload dict
                init_event = {
                    "type": "conversation_initiation_client_data",
                    "conversation_config_override": {
                        "conversation": {
                            "text_only": True
                        }
                    }
                }
                await websocket.send(json.dumps(init_event))

                # Wait for initial greeting/metadata from agent
                initial_response = await self._wait_for_initial_response(websocket)
                logging.info(
                    f"WebSocket connected for session {session_id}. "
                    f"Initial response received: {bool(initial_response)}"
                )

                self._connections[session_id] = ConnectionState(
                    websocket=websocket,
                    agent_id=agent_id,
                    signed_url=signed_url,
                )

                return True

            except Exception as e:
                logging.error(f"Failed to create WebSocket connection for session {session_id}: {e}")
                raise

    async def _wait_for_initial_response(
        self, websocket: WebSocketClientProtocol, timeout: float = 8.0
    ) -> Optional[str]:
        """Wait for the initial response from the agent after connection.
        
        Handles Pings and consumes the Agent's Greeting.
        """
        try:
            while True:
                message = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                data = json.loads(message)
                msg_type = data.get("type", "")
                
                # Handle Ping
                if msg_type == "ping":
                    event = data["ping_event"]
                    pong_payload = {
                        "type": "pong",
                        "event_id": event["event_id"]
                    }
                    await websocket.send(json.dumps(pong_payload))
                    continue

                if msg_type == "agent_response":
                    return data.get("agent_response", {}).get("message", "")
                
                if msg_type == "conversation_initiation_metadata":
                    continue

        except asyncio.TimeoutError:
            logging.warning("Timeout waiting for initial agent response")
            return None
        except Exception as e:
            logging.error(f"Error in initial response wait: {e}")
            return None

    async def send_message(
        self,
        session_id: str,
        text: str,
        text_only: bool = True,
        timeout: float = 30.0,
    ) -> Tuple[str, Optional[bytes]]:
        """Send a message through the persistent WebSocket and wait for response.

        Args:
            session_id: The session ID.
            text: Thinking text to send.
            text_only: Whether to request audio.
            timeout: Max time to wait for response.

        Returns:
            Tuple[str, Optional[bytes]]: (response_text, audio_bytes).
        """
        async with self._lock:
            state = self._connections.get(session_id)
            if not state or not state.is_active:
                raise RuntimeError(f"No active connection for session {session_id}")

            websocket = state.websocket
            state.message_count += 1

            try:
                # Correct payload format for ElevenLabs WebSocket
                payload = {
                    "type": "user_message",
                    "text": text
                }
                await websocket.send(json.dumps(payload))

                # Collect response parts
                full_text = []
                audio_parts = []
                
                start_time = time.time()
                while time.time() - start_time < timeout:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    msg_type = data.get("type", "")

                    if msg_type == "ping":
                        event = data["ping_event"]
                        pong_payload = {
                            "type": "pong",
                            "event_id": event["event_id"]
                        }
                        await websocket.send(json.dumps(pong_payload))
                        continue

                    if msg_type == "agent_response":
                        response = data.get("agent_response", {})
                        text_part = response.get("message", "")
                        if text_part:
                            full_text.append(text_part)
                        
                        # Check for end of response
                        # ElevenLabs usually sends multiple parts, then a final metadata or next user prompt
                        # For simple implementation, we assume a single response message is complete
                        # or we wait for a specific flag if the SDK provides it.
                        break

                    if msg_type == "audio_event":
                        audio_b64 = data.get("audio_event", {}).get("audio", "")
                        if audio_b64:
                            audio_parts.append(base64.b64decode(audio_b64))

                response_text = " ".join(full_text)
                audio_bytes = b"".join(audio_parts) if audio_parts else None
                
                return response_text, audio_bytes

            except asyncio.TimeoutError:
                logging.error(f"Timeout waiting for response on session {session_id}")
                return "Response timed out.", None
            except Exception as e:
                logging.error(f"Error sending message on session {session_id}: {e}")
                state.is_active = False
                raise

    def has_connection(self, session_id: str) -> bool:
        """Check if an active connection exists for the session."""
        state = self._connections.get(session_id)
        return state is not None and state.is_active

    async def close_connection(self, session_id: str):
        """Public method to close a session connection."""
        async with self._lock:
            await self._close_connection_internal(session_id)

    async def _close_connection_internal(self, session_id: str):
        """Lock-internal method to close connection."""
        state = self._connections.pop(session_id, None)
        if state and state.websocket:
            try:
                await state.websocket.close()
                logging.info(f"Closed WebSocket for session {session_id}")
            except Exception as e:
                logging.error(f"Error closing WebSocket for session {session_id}: {e}")

# Singleton instance
_manager = WebSocketConnectionManager()

def get_connection_manager() -> WebSocketConnectionManager:
    """Get the connection manager singleton."""
    return _manager
