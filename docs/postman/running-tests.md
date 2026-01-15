# Running Tests

## Prerequisites

1. Backend server running on `http://localhost:8000`
2. Python environment with dev dependencies

```bash
# Start backend
.\start-servers-gcp-firestore.ps1

# Or manually
uv run uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

## Running All Postman Tests

```bash
uv run --extra dev pytest tests/postman/ -v
```

## Running Specific Tests

```bash
# Health endpoints
uv run --extra dev pytest tests/postman/test_health_endpoints.py

# Knowledge API
uv run --extra dev pytest tests/postman/test_knowledge_api.py

# With pattern matching
uv run --extra dev pytest tests/postman/ -k "health"
```

## Running in Parallel

```bash
# Install pytest-xdist
uv add --dev pytest-xdist

# Run in parallel
uv run --extra dev pytest tests/postman/ -n auto
```

## CLI Runner

```bash
# Run all tests
uv run python -m tests.postman.cli_runner run

# Run with health check
uv run python -m tests.postman.cli_runner run --check-health

# Cleanup test resources
uv run python -m tests.postman.cli_runner cleanup
```

## Test Output

Tests generate output in:

- Console: Test results and summaries
- `.postman.json`: Updated with `last_run` statistics
