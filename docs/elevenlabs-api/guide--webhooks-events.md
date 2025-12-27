# Events: Conversation Logging and Monitoring

Events are the foundation of real-time communication in ElevenLabs Agents applications using WebSockets. They facilitate the exchange of information like audio streams, transcriptions, agent responses, and contextual updates.

## Overview

Events are broken down into two categories:

### Client Events (Server-to-Client)

Events sent from the server to the client, delivering:

- Audio
- Transcripts
- Agent messages
- System signals

### Client-to-Server Events

Events sent from the client to the server:

- Providing contextual updates
- Responding to server requests

## Webhooks (Post-call) (From Platform Customization)

(Note: Specific webhook payloads for post-call logging are managed in the ElevenLabs dashboard settings).
