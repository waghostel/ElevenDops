# Agent Authentication: Secure API Access

## Overview

When building conversational agents, you may need to restrict access to certain agents or conversations. ElevenLabs offers two primary methods to secure your conversational agents.

## Authentication Methods

### Signed URLs

Signed URLs are the recommended approach for client-side applications. This method allows you to authenticate users without exposing your API key.

1. Your server requests a signed URL from ElevenLabs using your API key.
2. ElevenLabs generates a temporary token and returns a signed WebSocket URL.
3. Your client application uses this signed URL to establish a WebSocket connection.
4. The signed URL expires after 15 minutes.

**Generate a signed URL via the API:**
GET `https://api.elevenlabs.io/v1/convai/conversation/get-signed-url?agent_id=<your-agent-id>`

Header: `xi-api-key: <your-api-key>`

Response:

```json
{
  "signed_url": "wss://api.elevenlabs.io/v1/convai/conversation?agent_id=<your-agent-id>&conversation_signature=<token>"
}
```

### Allowlists

Restrict access to specific domains or hostnames that can connect to your agent.
