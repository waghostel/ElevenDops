# ElevenLabs API Documentation Index

Welcome to the ElevenLabs API documentation. This comprehensive guide covers all aspects of integrating with ElevenLabs' powerful voice AI platform, from basic text-to-speech to advanced conversational agents.

## Getting Started

- [**Introduction**](intro.md) - Overview of ElevenLabs platform capabilities and services
- [**Authentication**](authentication.md) - Secure API access methods including signed URLs and allowlists

## Core APIs

### Text-to-Speech
- [**TTS API**](api_tts.md) - Convert text into lifelike speech with voice customization
- [**Streaming Audio**](streaming_audio.md) - Real-time voice conversion with optimized latency

### Voice Management
- [**Voices API**](api_voices.md) - Create and manage custom PVC voices

### Conversational AI
- [**Agents API**](api_agents.md) - Create and manage conversational AI agents
- [**Conversational AI WebSocket**](conversational_ai.md) - Real-time voice conversations via WebSocket
- [**Get Conversation Details**](api_get_conversation.md) - Retrieve conversation transcripts and metadata

## Platform Features

### Agent Configuration
- [**Agents Overview**](agents_overview.md) - Complete platform capabilities for building, deploying, and monitoring agents
- [**Prompting Guide**](prompting-guide.md) - System design principles for production-grade conversational AI
- [**Knowledge Base**](knowledge_base.md) - Enhance agents with custom knowledge and context
- [**Client Tools**](client_tools.md) - Enable client-side operations and UI interactions
- [**Data Collection**](data_collection.md) - Extract structured information from conversations

### Integration & SDKs
- [**React SDK**](react_sdk.md) - Frontend integration with useConversation hook
- [**Events & WebSockets**](webhooks_events.md) - Real-time communication and conversation monitoring

### Analytics & Monitoring
- [**Usage Analytics**](usage_analytics.md) - Performance metrics and system monitoring dashboard

## Quick Reference

### Authentication Methods
- **Signed URLs**: Recommended for client-side applications (15-minute expiry)
- **Allowlists**: Domain/hostname restrictions for agent access

### Key Endpoints
- **TTS**: `POST /v1/text-to-speech/{voice_id}`
- **Streaming**: `POST /v1/text-to-speech/{voice_id}/stream`
- **Agents**: `POST /v1/convai/agents`
- **WebSocket**: `wss://api.elevenlabs.io/v1/convai/conversation`

### SDK Support
- Python SDK with `ElevenLabs` client
- React SDK with `@elevenlabs/react` package
- WebSocket API for real-time interactions

## Platform Architecture

The ElevenLabs Agents Platform coordinates four core components:
1. **Speech-to-Text (ASR)** - Fine-tuned speech recognition
2. **Language Models** - Your choice of LLM or custom models
3. **Text-to-Speech (TTS)** - Low-latency voice synthesis across 5k+ voices and 31 languages
4. **Turn-taking Model** - Proprietary conversation timing management

## Use Cases

- **Voice Agents**: Deploy intelligent conversational AI across web, mobile, and telephony
- **Content Creation**: Generate lifelike speech for media and entertainment
- **Customer Service**: Automate support with natural voice interactions
- **Healthcare**: Patient interaction systems with real-time voice processing
- **Education**: Interactive learning experiences with voice AI

---

*For detailed implementation examples and advanced configurations, refer to the individual documentation files linked above.*