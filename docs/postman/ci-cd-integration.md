# CI/CD Integration

## GitHub Actions Workflow

The project includes a GitHub Actions workflow for automated testing.

**Location**: `.github/workflows/postman-tests.yml`

```yaml
name: Postman Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - name: Install dependencies
        run: uv sync --extra dev
      - name: Start backend
        run: |
          uv run uvicorn backend.main:app &
          sleep 5
      - name: Run tests
        run: uv run pytest tests/postman/ -v
```

## Test Reporting

Test results are output in standard pytest format. For JUnit XML:

```bash
uv run --extra dev pytest tests/postman/ --junitxml=reports/postman-tests.xml
```

## Failure Notifications

Configure GitHub Actions to notify on failures via:

- Slack integration
- Email notifications
- GitHub Issues

## Environment Variables

| Variable       | Description                                    |
| -------------- | ---------------------------------------------- |
| `BASE_URL`     | Backend URL (default: `http://localhost:8000`) |
| `TEST_TIMEOUT` | Request timeout (default: 30s)                 |
