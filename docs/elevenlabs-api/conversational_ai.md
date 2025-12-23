# WebSocket: Real-time Patient Interactions

The ElevenLabs [Agents Platform](https://elevenlabs.io/agents) WebSocket API enables real-time, interactive voice conversations with AI agents. By establishing a WebSocket connection, you can send audio input and receive audio responses in real-time, creating life-like conversational experiences.

## Connection URL

```
wss://api.elevenlabs.io/v1/convai/conversation?agent_id={agent_id}
```

## Authentication

### Using Agent ID

For public agents, you can directly use the `agent_id` in the WebSocket URL without additional authentication:

```
wss://api.elevenlabs.io/v1/convai/conversation?agent_id=<your-agent-id>
```

### Using a signed URL

For private agents or conversations requiring authorization, obtain a signed URL from your server. See `authentication.md` for details.

## WebSocket Events

### Client to Server Events

**Contextual Updates**
Send non-interrupting contextual information to update the conversation state.

```json
{
  "type": "contextual_update",
  "text": "User clicked on pricing page",
  "try_trigger_generation": true
}
```

> [!NOTE] > `try_trigger_generation` may be used to force audio generation for the text event.

Use cases:

- Adding background information

# Get Signed URL

Used for securing the WebSocket connection by generating a time-limited URL.

```python
from elevenlabs import ElevenLabs
client = ElevenLabs(
  base_url="https://api.elevenlabs.io"
)
response = client.conversational_ai.get_signed_url(
    agent_id="agent_id"
)
print(response.signed_url)
```

## Response

```json
{
  "signed_url": "wss://api.elevenlabs.io/v1/convai/conversation?agent_id=...&token=..."
}
```
