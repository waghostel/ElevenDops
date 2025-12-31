---
inclusion: fileMatch
fileMatchPattern: "backend/**/*.py"
---

# Backend Service Development Guidelines

## Reference Documents
- **User Requirements**: #[[file:user-need/user-need-phase1.md]]
- **ElevenLabs API**: #[[file:docs/elevenlabs-api/index.md]]

## Service Layer Structure

### elevenlabs_service.py
All ElevenLabs API interactions:
- `create_knowledge_document(text, name)` - Upload to KB
- `create_or_update_agent(config)` - Agent management
- `generate_audio(text, voice_id)` - TTS conversion
- `get_signed_url(agent_id)` - WebSocket auth
- `get_conversation(conversation_id)` - Fetch transcript

### langgraph_workflow.py
LangGraph-based AI script generation:
- `ScriptGenerationState` - TypedDict for workflow state
- `create_script_generation_graph()` - Build workflow graph
- Nodes: prepare_context → generate_script → post_process

### script_generation_service.py
Script generation orchestration:
- `ScriptGenerationService` - Main service class
- `generate_script(knowledge_id, model, prompt)` - Generate TTS-optimized scripts
- Integrates LangGraph workflow with Firestore data

### prompt_template_service.py
Prompt template management:
- Load default prompts from `backend/config/`
- Support custom prompt overrides
- ElevenLabs voice optimization guidelines

### langsmith_tracer.py
LangSmith observability integration:
- Trace LangGraph workflow executions
- Debug LLM calls and responses

### firestore_data_service.py
Firestore operations:
- Knowledge document CRUD
- Agent configuration storage
- Conversation log management
- Dashboard statistics

### data_service.py
Legacy data service (being migrated to firestore_data_service.py)

## API Endpoints

### Knowledge Management
```python
POST /api/knowledge
- Upload and sync knowledge document
- Body: { text, disease_name, document_type, doctor_id }
- Returns: { knowledge_id, elevenlabs_document_id }
```

### Audio Generation
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

### Agent Management
```python
POST /api/agent
- Create/update agent
- Body: { name, knowledge_ids[], voice_id, answer_style }
- Returns: { agent_id }
```

### Patient Session
```python
POST /api/patient/session
- Start conversation session
- Body: { patient_id, agent_id }
- Returns: { signed_url, session_id }

GET /api/patient/{id}/summary
- Get patient conversation summary
- Returns: { answered_questions[], unanswered_questions[], requires_attention[] }
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
