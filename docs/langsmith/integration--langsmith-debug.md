# LangSmith Debug Integration Guide

Complete guide to using LangSmith debugging capabilities for ElevenDops LangGraph workflows.

## Overview

The LangSmith Debug Integration provides comprehensive debugging, tracing, and visualization capabilities for the ElevenDops script generation workflow. This integration enables developers to monitor, debug, and optimize LangGraph workflow execution using LangSmith's powerful debugging tools.

## Features

### ✅ **Implemented Features**

- **🔍 Comprehensive Tracing**: Automatic trace capture for all workflow steps
- **🎯 Debug API Endpoints**: Dedicated endpoints for debugging workflow execution
- **📊 Session Management**: Group and manage debug sessions
- **🛡️ Graceful Degradation**: System continues working when LangSmith is unavailable
- **⚙️ Configurable Trace Levels**: Debug, info, and error trace levels
- **🏠 Local Studio Environment**: Node.js utilities for local debugging
- **🧪 Property-Based Testing**: Comprehensive test coverage with 53 passing tests

## Quick Start

### 1. Environment Setup

Add LangSmith configuration to your `.env` file:

```bash
# LangSmith Configuration
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=elevendops-langgraph-debug
LANGSMITH_TRACING=true
LANGSMITH_TRACE_LEVEL=info
```

### 2. Start the Backend

```bash
uv run uvicorn backend.main:app --reload
```

### 3. Verify Integration

Check the debug health endpoint:

```bash
curl http://localhost:8000/api/debug/health
```

Expected response:

```json
{
  "status": "healthy",
  "langsmith_configured": true,
  "langsmith_available": true,
  "project": "elevendops-langgraph-debug",
  "trace_level": "info"
}
```

### 4. Start Local Studio (Optional)

```bash
cd langsmith-studio
pnpm run dev
```

## Debug API Reference

### Health Check

```http
GET /api/debug/health
```

Returns LangSmith integration status and configuration.

### Execute Debug Script Generation

```http
POST /api/debug/script-generation
```

**Request Body:**

```json
{
  "knowledge_content": "Medical knowledge content here",
  "prompt": "Generate a script about diabetes care",
  "model_name": "gemini-2.0-flash",
  "debug_level": "info",
  "session_name": "diabetes-debug-session"
}
```

**Response:**

```json
{
  "trace_id": "trace_abc123",
  "session_id": "session_xyz789",
  "execution_status": "completed",
  "generated_script": "Generated script content...",
  "steps": [
    {
      "step_id": "step_1",
      "node_name": "prepare_context",
      "start_time": "2024-12-24T10:00:00Z",
      "end_time": "2024-12-24T10:00:05Z",
      "duration_ms": 5000,
      "error": null
    }
  ],
  "total_duration_ms": 15000,
  "langsmith_url": "https://smith.langchain.com/o/default/projects/p/elevendops-langgraph-debug"
}
```

### Session Management

#### Create Debug Session

```http
POST /api/debug/sessions
```

**Request Body:**

```json
{
  "name": "My Debug Session"
}
```

#### List Debug Sessions

```http
GET /api/debug/sessions
```

#### Get Session Details

```http
GET /api/debug/sessions/{session_id}
```

#### End Debug Session

```http
POST /api/debug/sessions/{session_id}/end
```

## Configuration Options

### Environment Variables

| Variable                | Default                      | Description                                |
| ----------------------- | ---------------------------- | ------------------------------------------ |
| `LANGCHAIN_API_KEY`     | -                            | LangSmith API key (required for tracing)   |
| `LANGCHAIN_PROJECT`     | `elevendops-langgraph-debug` | LangSmith project name                     |
| `LANGSMITH_TRACING`     | `true`                       | Enable/disable LangSmith tracing           |
| `LANGSMITH_TRACE_LEVEL` | `info`                       | Trace verbosity level (debug, info, error) |

### Trace Levels

- **`debug`**: Captures all workflow data including input/output states
- **`info`**: Captures essential workflow information and timing
- **`error`**: Captures only error information and stack traces

## Local Studio Environment

The `langsmith-studio` directory contains Node.js utilities for local debugging:

### Setup

```bash
cd langsmith-studio
pnpm install
```

### Usage

```bash
# Check backend connection and LangSmith status
pnpm run dev

# Test connection only
pnpm run test
```

### Configuration

Edit `langsmith-studio/src/studio.config.js`:

```javascript
export const studioConfig = {
  backend: {
    url: "http://localhost:8000",
    debugEndpoint: "/api/debug",
    healthEndpoint: "/api/debug/health",
    timeout: 30000,
  },
  langsmith: {
    apiKey: process.env.LANGCHAIN_API_KEY,
    project: "elevendops-langgraph-debug",
    baseUrl: "https://smith.langchain.com",
  },
  debug: {
    traceLevel: "info",
    logRequests: false,
  },
};
```

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LangSmith Debug Integration                        │
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Debug API       │  │  LangSmith       │  │  Local Studio    │  │
│  │  Endpoints       │  │  Tracer Service  │  │  Environment     │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  │
│           │                     │                     │             │
└───────────┼─────────────────────┼─────────────────────┼─────────────┘
            │                     │                     │
┌───────────▼─────────────────────▼─────────────────────▼─────────────┐
│                    Enhanced LangGraph Workflow                       │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Traced Workflow Nodes                                       │   │
│  │  - prepare_context (with tracing)                            │   │
│  │  - generate_script (with tracing)                            │   │
│  │  - post_process (with tracing)                               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
└───────────────────────────────────────┬───────────────────────────────┘
                                        │
┌───────────────────────────────────────▼───────────────────────────────┐
│                         LangSmith Cloud                                │
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │  Trace Database  │  │  Project:        │  │  Web Dashboard   │    │
│  │                  │  │  elevendops-     │  │                  │    │
│  │                  │  │  langgraph-debug │  │                  │    │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Debug Request** → Debug API receives request with workflow parameters
2. **Session Creation** → Optional debug session created for grouping traces
3. **Workflow Execution** → Enhanced LangGraph workflow runs with tracing
4. **Trace Capture** → Each workflow step captured with timing and state data
5. **LangSmith Upload** → Trace data sent to LangSmith cloud (if available)
6. **Response** → Debug response returned with trace ID and execution details
7. **Visualization** → Traces viewable in LangSmith dashboard or local studio

## Testing

### Running Tests

```bash
# Run all LangSmith-related tests
uv run python -m pytest tests/ -k "langsmith" -v

# Run debug API tests
uv run python -m pytest tests/ -k "debug" -v

# Run specific test file
uv run python -m pytest tests/test_langsmith_tracer_props.py -v
```

### Test Coverage

- **29 LangSmith tracer tests** ✅
- **24 Debug API tests** ✅
- **Property-based tests** for all correctness properties
- **Graceful degradation tests** when LangSmith is unavailable
- **Session persistence tests** for debug session management

## Troubleshooting

### Common Issues

#### 1. LangSmith API Key Not Set

**Symptom**: `langsmith_configured: false` in health check

**Solution**: Set `LANGCHAIN_API_KEY` in your `.env` file

#### 2. LangSmith Service Unavailable

**Symptom**: `langsmith_available: false` in health check

**Solution**: Check internet connection and API key validity. System will gracefully degrade.

#### 3. Traces Not Appearing in LangSmith

**Symptom**: Debug API works but no traces in LangSmith dashboard

**Solutions**:

- Verify `LANGCHAIN_PROJECT` matches your LangSmith project
- Check API key permissions
- Ensure `LANGSMITH_TRACING=true`

#### 4. Local Studio Connection Failed

**Symptom**: Studio shows "Backend not connected"

**Solutions**:

- Ensure backend is running on `http://localhost:8000`
- Check firewall settings
- Verify debug endpoints are accessible

### Debug Commands

```bash
# Check LangSmith configuration
uv run python -c "
from backend.config import get_settings
settings = get_settings()
print(f'LangSmith configured: {settings.is_langsmith_configured()}')
print(f'Project: {settings.langsmith_project}')
print(f'Trace level: {settings.langsmith_trace_level}')
"

# Test tracer service
uv run python -c "
from backend.services.langsmith_tracer import get_tracer
tracer = get_tracer()
print(f'Tracer available: {tracer.is_available()}')
session_id = tracer.start_trace_session('test-session')
print(f'Test session created: {session_id}')
"

# Test debug API
curl -X POST http://localhost:8000/api/debug/script-generation \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_content": "Test content",
    "prompt": "Test prompt"
  }'
```

## Best Practices

### 1. Session Management

- Use descriptive session names for easier identification
- Group related debug runs in the same session
- End sessions when debugging is complete to free resources

### 2. Trace Levels

- Use `debug` level for detailed troubleshooting
- Use `info` level for general monitoring
- Use `error` level in production to minimize overhead

### 3. Performance Considerations

- Tracing adds minimal overhead (~50-100ms per workflow)
- Debug level tracing captures more data but uses more bandwidth
- Sessions are stored in memory; end unused sessions

### 4. Security

- Keep LangSmith API keys secure
- Don't commit API keys to version control
- Use environment-specific projects for different deployments

## Integration with Existing Workflow

The LangSmith integration is designed to be non-invasive:

- **No changes required** to existing workflow logic
- **Automatic tracing** when LangSmith is configured
- **Graceful degradation** when LangSmith is unavailable
- **Optional debug endpoints** for enhanced debugging

## Future Enhancements

### Planned Features

- **Real-time trace streaming** via WebSocket
- **Advanced filtering** in debug API
- **Trace comparison** tools
- **Performance analytics** dashboard
- **Custom trace annotations**

### Integration Opportunities

- **CI/CD pipeline integration** for automated testing
- **Alerting system** for workflow failures
- **Performance monitoring** dashboards
- **A/B testing** framework for workflow optimization

## Support

### Documentation

- [LangSmith Official Documentation](https://docs.smith.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [ElevenDops Architecture Guide](./MVP1_ARCHITECTURE.md)

### Getting Help

1. Check this documentation first
2. Review test files for usage examples
3. Check LangSmith dashboard for trace details
4. Use debug health endpoint to verify configuration

---

**Last Updated**: December 26, 2024  
**Integration Status**: ✅ Complete and Tested  
**Test Coverage**: 53 passing tests
