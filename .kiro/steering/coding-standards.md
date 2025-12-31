---
inclusion: always
---

# ElevenDops Coding Standards

## Project Structure
```
backend/           # FastAPI backend with business logic
  api/             # API route handlers
    routes/        # Modular route files (audio, agent, knowledge, etc.)
  config/          # Configuration files and prompts
    prompts/       # Prompt templates
  services/        # Service layer (elevenlabs, langgraph, data)
  models/          # Pydantic schemas
streamlit_app/     # Streamlit UI (presentation only)
  pages/           # Multi-page app structure
  services/        # Backend API client
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
- Endpoints: `/api/knowledge`, `/api/audio`, `/api/agent`, `/api/patient/*`
- Return consistent response schemas
- Handle errors with proper HTTP status codes

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
