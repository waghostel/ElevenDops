# Debug API Reference

Complete REST API documentation for LangSmith Debug Integration endpoints.

## Base URL

```
http://localhost:8000/api/debug
```

## Authentication

Debug endpoints do not require authentication in the current implementation.

## Response Format

All responses follow the standard ElevenDops API format:

### Success Response (2xx)
```json
{
  "status": "success",
  "data": {
    // Response data
  }
}
```

### Error Response (4xx, 5xx)
```json
{
  "status": "error",
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {}
}
```

## Endpoints

### Health Check

#### Check Debug Service Health
```http
GET /api/debug/health
```

Returns the status of the debug service and LangSmith integration.

**Response (200):**
```json
{
  "status": "healthy",
  "langsmith_configured": true,
  "langsmith_available": true,
  "project": "elevendops-langgraph-debug",
  "trace_level": "info"
}
```

**Response Fields:**
- `status`: Service health status
- `langsmith_configured`: Whether LangSmith API key is configured
- `langsmith_available`: Whether LangSmith service is reachable
- `project`: LangSmith project name
- `trace_level`: Current trace verbosity level

---

### Script Generation Debugging

#### Execute Debug Script Generation
```http
POST /api/debug/script-generation
```

Executes the script generation workflow with full tracing and debugging capabilities.

**Request Body:**
```json
{
  "knowledge_content": "Medical knowledge content for script generation",
  "prompt": "Generate a script about diabetes management",
  "model_name": "gemini-2.0-flash",
  "debug_level": "info",
  "session_name": "diabetes-debug-session"
}
```

**Request Fields:**
- `knowledge_content` (required): Medical knowledge content to use for script generation
- `prompt` (required): Generation prompt describing what script to create
- `model_name` (optional): Gemini model to use (default: "gemini-2.0-flash")
- `debug_level` (optional): Trace verbosity level - "debug", "info", or "error" (default: "info")
- `session_name` (optional): Name for debug session to group related traces

**Response (200):**
```json
{
  "trace_id": "trace_abc123xyz",
  "session_id": "session_def456",
  "execution_status": "completed",
  "generated_script": "Generated medical script content...",
  "error_details": null,
  "steps": [
    {
      "step_id": "step_1",
      "node_name": "prepare_context",
      "start_time": "2024-12-24T10:00:00Z",
      "end_time": "2024-12-24T10:00:05Z",
      "duration_ms": 5000,
      "error": null,
      "has_stack_trace": false
    },
    {
      "step_id": "step_2", 
      "node_name": "generate_script",
      "start_time": "2024-12-24T10:00:05Z",
      "end_time": "2024-12-24T10:00:15Z",
      "duration_ms": 10000,
      "error": null,
      "has_stack_trace": false
    }
  ],
  "total_duration_ms": 15000,
  "langsmith_url": "https://smith.langchain.com/o/default/projects/p/elevendops-langgraph-debug"
}
```

**Response Fields:**
- `trace_id`: Unique identifier for this workflow execution trace
- `session_id`: Debug session ID (if session_name was provided)
- `execution_status`: Workflow execution status ("completed", "failed", "partial")
- `generated_script`: Generated script content (if successful)
- `error_details`: Error information (if execution failed)
- `steps`: Array of workflow step details with timing information
- `total_duration_ms`: Total workflow execution time in milliseconds
- `langsmith_url`: URL to view trace in LangSmith dashboard

**Error Responses:**
- `400`: Invalid request parameters (missing required fields, invalid debug_level)
- `500`: Workflow execution failed

**Example cURL:**
```bash
curl -X POST http://localhost:8000/api/debug/script-generation \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_content": "Diabetes is a chronic condition that affects blood sugar levels...",
    "prompt": "Create an educational script about diabetes management for patients",
    "debug_level": "debug",
    "session_name": "diabetes-education-debug"
  }'
```

---

### Debug Session Management

#### Create Debug Session
```http
POST /api/debug/sessions
```

Creates a new debug session for grouping related traces.

**Request Body:**
```json
{
  "name": "Diabetes Script Generation Debug"
}
```

**Request Fields:**
- `name` (required): Descriptive name for the debug session

**Response (201):**
```json
{
  "session_id": "session_abc123",
  "name": "Diabetes Script Generation Debug",
  "created_at": "2024-12-24T10:00:00Z"
}
```

---

#### List Debug Sessions
```http
GET /api/debug/sessions
```

Returns a list of all debug sessions.

**Response (200):**
```json
{
  "sessions": [
    {
      "session_id": "session_abc123",
      "name": "Diabetes Script Generation Debug",
      "created_at": "2024-12-24T10:00:00Z",
      "ended_at": null,
      "trace_count": 3,
      "status": "active"
    },
    {
      "session_id": "session_def456",
      "name": "Hypertension Debug Session",
      "created_at": "2024-12-24T09:30:00Z",
      "ended_at": "2024-12-24T09:45:00Z",
      "trace_count": 5,
      "status": "completed"
    }
  ],
  "total_count": 2
}
```

**Response Fields:**
- `sessions`: Array of debug session objects
- `total_count`: Total number of sessions

**Session Object Fields:**
- `session_id`: Unique session identifier
- `name`: Session name
- `created_at`: Session creation timestamp
- `ended_at`: Session end timestamp (null if active)
- `trace_count`: Number of traces in this session
- `status`: Session status ("active" or "completed")

---

#### Get Debug Session Details
```http
GET /api/debug/sessions/{session_id}
```

Returns detailed information about a specific debug session.

**Path Parameters:**
- `session_id`: The session identifier

**Response (200):**
```json
{
  "session_id": "session_abc123",
  "name": "Diabetes Script Generation Debug",
  "created_at": "2024-12-24T10:00:00Z",
  "ended_at": null,
  "trace_count": 3,
  "status": "active"
}
```

**Error Responses:**
- `404`: Session not found

---

#### End Debug Session
```http
POST /api/debug/sessions/{session_id}/end
```

Ends an active debug session.

**Path Parameters:**
- `session_id`: The session identifier

**Response (200):**
```json
{
  "session_id": "session_abc123",
  "status": "completed",
  "trace_count": 3,
  "langsmith_url": "https://smith.langchain.com/o/default/projects/p/elevendops-langgraph-debug"
}
```

**Response Fields:**
- `session_id`: The session identifier
- `status`: Updated session status
- `trace_count`: Final number of traces in the session
- `langsmith_url`: URL to view session traces in LangSmith

**Error Responses:**
- `404`: Session not found

---

## Debug Levels

The `debug_level` parameter controls the verbosity of trace data captured:

### `debug`
- **Most Verbose**: Captures all available workflow data
- **Includes**: Input/output states, intermediate values, detailed timing
- **Use Case**: Detailed troubleshooting and development
- **Performance Impact**: Higher bandwidth usage

### `info` (Default)
- **Balanced**: Captures essential workflow information
- **Includes**: Step names, timing, success/failure status
- **Use Case**: General monitoring and debugging
- **Performance Impact**: Moderate bandwidth usage

### `error`
- **Minimal**: Captures only error information
- **Includes**: Error messages, stack traces, failure points
- **Use Case**: Production monitoring
- **Performance Impact**: Minimal bandwidth usage

## Error Handling

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Invalid request parameters |
| `MISSING_REQUIRED_FIELD` | 400 | Required field missing from request |
| `INVALID_DEBUG_LEVEL` | 400 | Invalid debug_level value |
| `SESSION_NOT_FOUND` | 404 | Debug session not found |
| `WORKFLOW_EXECUTION_FAILED` | 500 | Script generation workflow failed |
| `LANGSMITH_ERROR` | 502 | LangSmith service error |
| `INTERNAL_ERROR` | 500 | Internal server error |

### Error Response Examples

#### Invalid Request
```json
{
  "status": "error",
  "error": "MISSING_REQUIRED_FIELD",
  "message": "Field 'knowledge_content' is required",
  "details": {
    "field": "knowledge_content",
    "provided_value": null
  }
}
```

#### Workflow Execution Failed
```json
{
  "status": "error",
  "error": "WORKFLOW_EXECUTION_FAILED",
  "message": "Script generation workflow failed",
  "details": {
    "step": "generate_script",
    "error": "Model API rate limit exceeded"
  }
}
```

## Testing Examples

### Basic Debug Execution
```bash
curl -X POST http://localhost:8000/api/debug/script-generation \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_content": "Hypertension is high blood pressure that can lead to serious health complications.",
    "prompt": "Create a patient education script about hypertension management"
  }'
```

### Debug with Session
```bash
# Create session
SESSION_RESPONSE=$(curl -s -X POST http://localhost:8000/api/debug/sessions \
  -H "Content-Type: application/json" \
  -d '{"name": "Hypertension Debug Session"}')

SESSION_ID=$(echo $SESSION_RESPONSE | jq -r '.session_id')

# Execute debug with session
curl -X POST http://localhost:8000/api/debug/script-generation \
  -H "Content-Type: application/json" \
  -d "{
    \"knowledge_content\": \"Hypertension management guidelines...\",
    \"prompt\": \"Create educational content about blood pressure monitoring\",
    \"session_name\": \"Hypertension Debug Session\",
    \"debug_level\": \"debug\"
  }"

# End session
curl -X POST http://localhost:8000/api/debug/sessions/$SESSION_ID/end
```

### Health Check
```bash
curl http://localhost:8000/api/debug/health
```

### List Sessions
```bash
curl http://localhost:8000/api/debug/sessions
```

## Integration with LangSmith

### Trace Visualization

When LangSmith is configured, traces are automatically uploaded and can be viewed at:
```
https://smith.langchain.com/o/default/projects/p/elevendops-langgraph-debug
```

### Trace Data Structure

Each trace includes:
- **Workflow Steps**: Individual node executions with timing
- **Input/Output Data**: Request parameters and generated results
- **Error Information**: Stack traces and error context (when applicable)
- **Metadata**: Session information, debug level, model configuration
- **Performance Metrics**: Execution timing and resource usage

### Project Organization

Traces are organized by:
- **Project**: `elevendops-langgraph-debug`
- **Sessions**: Grouped traces for related debugging activities
- **Tags**: Automatic tagging with debug level and workflow type

## Performance Considerations

### Trace Overhead

- **Debug Level**: ~100-200ms additional latency
- **Info Level**: ~50-100ms additional latency  
- **Error Level**: ~10-20ms additional latency

### Bandwidth Usage

- **Debug Level**: ~10-50KB per trace
- **Info Level**: ~2-10KB per trace
- **Error Level**: ~1-5KB per trace

### Recommendations

- Use `info` level for general debugging
- Use `debug` level only when detailed troubleshooting is needed
- Use `error` level in production environments
- End debug sessions when no longer needed to free memory

## Security Considerations

### API Key Management

- LangSmith API keys are configured via environment variables
- Keys are not exposed in API responses
- Traces may contain sensitive medical content - ensure proper LangSmith project access controls

### Data Privacy

- Debug traces may contain medical knowledge content
- Ensure LangSmith project has appropriate access restrictions
- Consider data retention policies for debug traces

---

**Last Updated**: December 24, 2024  
**API Version**: 1.0  
**Integration Status**: ✅ Complete and Tested