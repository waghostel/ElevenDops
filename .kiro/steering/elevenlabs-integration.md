---
inclusion: fileMatch
fileMatchPattern: "**/*elevenlabs*"
---

# ElevenLabs Integration Guidelines

## API Documentation Reference
For detailed API specifications, see: #[[file:docs/elevenlabs-api/index.md]]

## Core APIs Used in This Project

### 1. Knowledge Base API
- Upload medical education documents
- Sync with Firestore as primary source
- Endpoint: `client.conversational_ai.knowledge_base.documents.create_from_text()`

### 2. Agents API
- Create/update conversational AI agents
- Configure system prompts, voice, and knowledge base links
- Endpoint: `client.conversational_ai.agents.create_or_update()`

### 3. Text-to-Speech API
- Generate education audio files
- Use `eleven_multilingual_v2` model for Chinese support
- Endpoint: `client.text_to_speech.convert()`

### 4. Conversational AI WebSocket
- Real-time patient voice conversations
- Use signed URLs for security (15-min expiry)
- Endpoint: `wss://api.elevenlabs.io/v1/convai/conversation`

## Implementation Patterns

### API Client Initialization
```python
from elevenlabs import ElevenLabs
import os

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
```

### Error Handling
- Implement retry with exponential backoff
- Handle quota exceeded gracefully
- Log all API errors for debugging

### Security
- Never expose API keys to frontend
- Use signed URLs for patient-side WebSocket connections
- Store sensitive config in environment variables

## Data Flow
```
Firestore (source) → ElevenLabs Knowledge Base (copy)
                   → ElevenLabs Agent (references KB)
                   → Patient Conversation → Firestore (logs)
```
