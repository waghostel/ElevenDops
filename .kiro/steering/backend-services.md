---
inclusion: fileMatch
fileMatchPattern: "backend/**/*.py"
---

# Backend Service Development Guidelines

## Reference Documents
- **User Requirements**: #[[file:user-need/user-need-phase1.md]]
- **ElevenLabs API**: #[[file:docs/elevenlabs-api/index.md]]

## Service Layer Structure

### Core Services

#### elevenlabs_service.py
All ElevenLabs API interactions:
- `create_knowledge_document(text, name)` - Upload to KB
- `create_or_update_agent(config)` - Agent management
- `generate_audio(text, voice_id)` - TTS conversion
- `get_signed_url(agent_id)` - WebSocket auth
- `get_conversation(conversation_id)` - Fetch transcript

#### audio_service.py
Audio generation and management:
- TTS audio generation via ElevenLabs
- Audio file storage to GCS
- Audio metadata management

#### agent_service.py
Agent configuration and management:
- Create/update ElevenLabs agents
- Link knowledge bases to agents
- Configure voice and behavior settings

#### patient_service.py
Patient session management:
- Start conversation sessions
- Generate signed URLs for WebSocket
- Track patient interactions

### AI/LLM Services

#### langgraph_workflow.py
LangGraph-based AI script generation:
- `ScriptGenerationState` - TypedDict for workflow state
- `create_script_generation_graph()` - Build workflow graph
- Nodes: prepare_context → generate_script → post_process

#### script_generation_service.py
Script generation orchestration:
- `ScriptGenerationService` - Main service class
- `generate_script(knowledge_id, model, prompt)` - Generate TTS-optimized scripts
- Integrates LangGraph workflow with Firestore data

#### prompt_template_service.py
Prompt template management:
- Load default prompts from `backend/config/`
- Support custom prompt overrides
- ElevenLabs voice optimization guidelines

#### langsmith_tracer.py
LangSmith observability integration:
- Trace LangGraph workflow executions
- Debug LLM calls and responses

#### analysis_service.py
Conversation analysis:
- Analyze patient questions
- Identify unanswered questions
- Flag items requiring doctor attention

### Data Services

#### firestore_data_service.py
Primary Firestore operations:
- Knowledge document CRUD
- Agent configuration storage
- Conversation log management
- Dashboard statistics

#### firestore_service.py
Low-level Firestore client wrapper

#### storage_service.py
GCS file storage:
- Upload audio files
- Generate signed URLs
- Manage file lifecycle

#### conversation_service.py
Conversation data management:
- Store conversation transcripts
- Retrieve conversation history
- Link conversations to patients/agents

### Infrastructure Services

#### websocket_manager.py
WebSocket connection management:
- Manage active connections
- Handle connection lifecycle
- Support real-time communication

## API Endpoints

### Knowledge Management (`/api/knowledge`)
```python
POST /api/knowledge
- Upload and sync knowledge document
- Body: { text, disease_name, document_type, doctor_id }
- Returns: { knowledge_id, elevenlabs_document_id }

GET /api/knowledge
- List all knowledge documents
- Returns: [{ id, disease_name, document_type, created_at }]

GET /api/knowledge/{id}
- Get specific knowledge document
- Returns: { id, text, disease_name, document_type, metadata }

DELETE /api/knowledge/{id}
- Delete knowledge document (Firestore + ElevenLabs)
```

### Audio Generation (`/api/audio`)
```python
POST /api/audio
- Generate TTS from script
- Body: { script_content, voice_id, disease_name }
- Returns: { audio_url, duration_seconds }

POST /api/audio/generate-script
- AI-powered script generation
- Body: { knowledge_id, model?, custom_prompt? }
- Returns: { script_content, model_used, generation_time_ms }
```

### Agent Management (`/api/agent`)
```python
POST /api/agent
- Create/update agent
- Body: { name, knowledge_ids[], voice_id, answer_style }
- Returns: { agent_id }

GET /api/agent
- List all agents
- Returns: [{ id, name, voice_id, knowledge_ids }]

GET /api/agent/{id}
- Get agent details
- Returns: { id, name, config, elevenlabs_agent_id }
```

### Patient Session (`/api/patient`)
```python
POST /api/patient/session
- Start conversation session
- Body: { patient_id, agent_id }
- Returns: { signed_url, session_id }

GET /api/patient/{id}/summary
- Get patient conversation summary
- Returns: { answered_questions[], unanswered_questions[], requires_attention[] }
```

### Conversation Logs (`/api/conversation`)
```python
GET /api/conversation
- List conversations with filters
- Query: patient_id?, agent_id?, date_range?
- Returns: [{ id, patient_id, agent_id, transcript, created_at }]

GET /api/conversation/{id}
- Get conversation details
- Returns: { id, transcript, analysis, metadata }
```

### Prompt Templates (`/api/templates`)
```python
GET /api/templates
- List available prompt templates
- Returns: [{ id, name, description, content }]

GET /api/templates/{id}
- Get specific template
- Returns: { id, name, content, variables }
```

### Debug Endpoints (`/api/debug`)
```python
GET /api/debug/health
- System health check

GET /api/debug/config
- Configuration status (non-sensitive)
```

## Error Handling Pattern
```python
from fastapi import HTTPException
import backoff
from elevenlabs.exceptions import ElevenLabsError

@backoff.on_exception(backoff.expo, ElevenLabsError, max_tries=3)
async def api_call_with_retry():
    try:
        # API call
    except ElevenLabsError as e:
        raise HTTPException(status_code=502, detail=str(e))
```

## Data Models
Define in `backend/models/schemas.py`:
- Use Pydantic for validation
- Match Firestore document structure
- Include ElevenLabs ID references
