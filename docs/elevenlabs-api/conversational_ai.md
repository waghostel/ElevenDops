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
  "text": "User clicked on pricing page"
}
```

Use cases:

- Updating user status or preferences (e.g. "Patient selected generic symptoms")
- Providing environmental context
- Adding background information
