# LangSmith Studio

Local development utilities for debugging ElevenDops LangGraph workflows.

## Setup

```bash
cd langsmith-studio
pnpm install
```

## Configuration

Set these environment variables (or create a `.env` file):

```bash
# Optional - LangSmith API key for cloud features
LANGCHAIN_API_KEY=your_api_key_here

# Optional - Backend URL (defaults to localhost:8000)
BACKEND_URL=http://localhost:8000

# Optional - LangSmith project name
LANGCHAIN_PROJECT=elevendops-langgraph-debug
```

## Usage

### Start Studio

```bash
pnpm dev
```

This will:

1. Check connection to the backend debug API
2. Display LangSmith dashboard URL
3. Show available debug endpoints

### Test Connection

```bash
pnpm test
```

Verifies that the backend debug API is reachable and responding correctly.

## Debug Endpoints

The backend provides these debug endpoints:

| Method | Endpoint                       | Description                   |
| ------ | ------------------------------ | ----------------------------- |
| POST   | `/api/debug/script-generation` | Execute workflow with tracing |
| GET    | `/api/debug/sessions`          | List debug sessions           |
| POST   | `/api/debug/sessions`          | Create new session            |
| GET    | `/api/debug/sessions/{id}`     | Get session details           |
| GET    | `/api/debug/health`            | Health check                  |

## Example: Debug Script Generation

```bash
curl -X POST http://localhost:8000/api/debug/script-generation \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_content": "Patient education about diabetes management...",
    "prompt": "Generate a clear, empathetic script for patients",
    "model_name": "gemini-2.0-flash",
    "debug_level": "debug",
    "session_name": "diabetes-test-1"
  }'
```

Response includes:

- `trace_id` - Unique trace identifier
- `session_id` - Session ID (if session name provided)
- `execution_status` - completed/error
- `steps` - Detailed step-by-step execution data
- `langsmith_url` - Link to LangSmith dashboard
