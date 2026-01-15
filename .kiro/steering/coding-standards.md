---
inclusion: always
---

# ElevenDops Coding Standards

## Project Structure
```
backend/           # FastAPI backend with business logic
  api/             # API route handlers
    routes/        # Modular route files
      agent.py     # Agent management endpoints
      audio.py     # Audio generation endpoints
      conversation.py  # Conversation log endpoints
      debug.py     # Debug/health endpoints
      knowledge.py # Knowledge document endpoints
      patient.py   # Patient session endpoints
      templates.py # Prompt template endpoints
    dashboard.py   # Dashboard statistics
    health.py      # Health check endpoint
  config/          # Configuration files and prompts
    prompts/       # Prompt templates
  services/        # Service layer
    elevenlabs_service.py    # ElevenLabs API
    audio_service.py         # Audio generation
    agent_service.py         # Agent management
    patient_service.py       # Patient sessions
    conversation_service.py  # Conversation handling
    analysis_service.py      # Conversation analysis
    langgraph_workflow.py    # AI script workflow
    script_generation_service.py  # Script generation
    prompt_template_service.py    # Prompt templates
    langsmith_tracer.py      # LangSmith tracing
    firestore_data_service.py    # Firestore operations
    storage_service.py       # GCS file storage
    websocket_manager.py     # WebSocket connections
  models/          # Pydantic schemas
streamlit_app/     # Streamlit UI (presentation only)
  pages/           # Multi-page app structure
    1_Doctor_Dashboard.py
    2_Upload_Knowledge.py
    3_Education_Audio.py
    4_Agent_Setup.py
    5_Patient_Test.py
    6_Conversation_Logs.py
  services/        # Backend API client
    backend_api.py
tests/             # Property-based and unit tests
  properties/      # Property test helpers
docs/              # Documentation and API references
.kiro/specs/       # Feature specifications
```

## Key Principles

### Streamlit Responsibilities
✅ User interface rendering
✅ Backend API calls via `streamlit_app/services/backend_api.py`
✅ Display results (audio, agent IDs, conversation logs)

❌ Direct ElevenLabs API calls
❌ Direct Firestore operations
❌ Business logic processing
❌ LLM prompt handling

### Backend Responsibilities
✅ All ElevenLabs API integration
✅ Firestore CRUD operations
✅ Business logic and validation
✅ Data transformation

## API Design
- Follow RESTful conventions
- Route files in `backend/api/routes/`
- Endpoints: `/api/knowledge`, `/api/audio`, `/api/agent`, `/api/patient`, `/api/conversation`, `/api/templates`, `/api/debug`
- Return consistent response schemas
- Handle errors with proper HTTP status codes
- Use dependency injection for services

## Testing
- Use Hypothesis for property-based testing
- Test files: `tests/test_*_props.py`
- Focus on core logic validation

## Environment Variables
Required in `.env`:
- `ELEVENLABS_API_KEY` - ElevenLabs API access
- `GOOGLE_API_KEY` - Google Gemini API for script generation
- `LANGCHAIN_API_KEY` - LangSmith tracing (optional)
- `LANGCHAIN_PROJECT` - LangSmith project name
- Firestore credentials (service account JSON)

## Language
- Code: English
- UI text: Traditional Chinese (繁體中文)
- Documentation: Bilingual where appropriate
