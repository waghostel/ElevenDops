# LangSmith Debug Integration - Quick Reference

Fast reference guide for using LangSmith debugging capabilities in ElevenDops.

## Quick Setup

### 1. Environment Configuration
```bash
# Add to .env file
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=elevendops-langgraph-debug
LANGSMITH_TRACING=true
LANGSMITH_TRACE_LEVEL=info
```

### 2. Start Backend
```bash
poetry run uvicorn backend.main:app --reload
```

### 3. Verify Setup
```bash
curl http://localhost:8000/api/debug/health
```

## Quick Commands

### Health Check
```bash
curl http://localhost:8000/api/debug/health
```

### Debug Script Generation
```bash
curl -X POST http://localhost:8000/api/debug/script-generation \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_content": "Diabetes is a chronic condition...",
    "prompt": "Create patient education script about diabetes"
  }'
```

### Create Debug Session
```bash
curl -X POST http://localhost:8000/api/debug/sessions \
  -H "Content-Type: application/json" \
  -d '{"name": "My Debug Session"}'
```

### List Debug Sessions
```bash
curl http://localhost:8000/api/debug/sessions
```

### Local Studio
```bash
cd langsmith-studio
npm run dev
```

## Debug Levels

| Level | Use Case | Data Captured |
|-------|----------|---------------|
| `debug` | Detailed troubleshooting | All workflow data, input/output states |
| `info` | General monitoring | Essential info, timing, status |
| `error` | Production monitoring | Only errors and stack traces |

## Common Workflows

### Basic Debug Session
```bash
# 1. Create session
SESSION_ID=$(curl -s -X POST http://localhost:8000/api/debug/sessions \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Session"}' | jq -r '.session_id')

# 2. Run debug execution
curl -X POST http://localhost:8000/api/debug/script-generation \
  -H "Content-Type: application/json" \
  -d "{
    \"knowledge_content\": \"Test content\",
    \"prompt\": \"Test prompt\",
    \"session_name\": \"Test Session\",
    \"debug_level\": \"debug\"
  }"

# 3. End session
curl -X POST http://localhost:8000/api/debug/sessions/$SESSION_ID/end
```

### Check Configuration
```bash
poetry run python -c "
from backend.config import get_settings
settings = get_settings()
print(f'LangSmith configured: {settings.is_langsmith_configured()}')
print(f'Project: {settings.langsmith_project}')
print(f'Trace level: {settings.langsmith_trace_level}')
"
```

### Test Tracer Service
```bash
poetry run python -c "
from backend.services.langsmith_tracer import get_tracer
tracer = get_tracer()
print(f'Tracer available: {tracer.is_available()}')
"
```

## API Endpoints Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/debug/health` | GET | Check service status |
| `/api/debug/script-generation` | POST | Execute traced workflow |
| `/api/debug/sessions` | GET | List debug sessions |
| `/api/debug/sessions` | POST | Create debug session |
| `/api/debug/sessions/{id}` | GET | Get session details |
| `/api/debug/sessions/{id}/end` | POST | End debug session |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LANGCHAIN_API_KEY` | - | LangSmith API key (required) |
| `LANGCHAIN_PROJECT` | `elevendops-langgraph-debug` | Project name |
| `LANGSMITH_TRACING` | `true` | Enable/disable tracing |
| `LANGSMITH_TRACE_LEVEL` | `info` | Trace verbosity level |

## Troubleshooting Quick Fixes

### LangSmith Not Configured
```bash
# Check if API key is set
echo $LANGCHAIN_API_KEY

# Set API key
export LANGCHAIN_API_KEY=your_key_here
```

### Service Unavailable
```bash
# Check internet connection
curl -I https://api.smith.langchain.com

# System will gracefully degrade - check health endpoint
curl http://localhost:8000/api/debug/health
```

### Local Studio Connection Failed
```bash
# Check backend is running
curl http://localhost:8000/api/debug/health

# Start studio
cd langsmith-studio && npm run dev
```

## Testing Commands

### Run All Debug Tests
```bash
poetry run python -m pytest tests/ -k "debug" -v
```

### Run LangSmith Tests
```bash
poetry run python -m pytest tests/ -k "langsmith" -v
```

### Run Specific Test File
```bash
poetry run python -m pytest tests/test_debug_api_props.py -v
```

## URLs

| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| Debug Health | http://localhost:8000/api/debug/health |
| API Docs | http://localhost:8000/docs |
| LangSmith Dashboard | https://smith.langchain.com |
| Local Studio | Run `npm run dev` in langsmith-studio/ |

## File Locations

| Component | Path |
|-----------|------|
| Debug API | `backend/api/routes/debug.py` |
| Tracer Service | `backend/services/langsmith_tracer.py` |
| Workflow Service | `backend/services/langgraph_workflow.py` |
| Configuration | `backend/config.py` |
| Local Studio | `langsmith-studio/` |
| Tests | `tests/test_*debug*.py`, `tests/test_*langsmith*.py` |

## Performance Impact

| Debug Level | Latency Overhead | Bandwidth Usage |
|-------------|------------------|-----------------|
| `debug` | ~100-200ms | ~10-50KB per trace |
| `info` | ~50-100ms | ~2-10KB per trace |
| `error` | ~10-20ms | ~1-5KB per trace |

## Integration Status

✅ **Complete Features:**
- LangSmith tracer service
- Debug API endpoints  
- Session management
- Graceful degradation
- Local studio environment
- Property-based testing (53 tests passing)

---

**Quick Links:**
- [Full Documentation](LANGSMITH_DEBUG_INTEGRATION.md)
- [Debug API Reference](DEBUG_API_REFERENCE.md)
- [Architecture Guide](MVP1_ARCHITECTURE.md)