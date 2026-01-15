# Postman Backend Testing System

This documentation covers the comprehensive Postman-based testing system for the ElevenDops backend API.

## Quick Start

```bash
# Run all Postman tests
uv run --extra dev pytest tests/postman/ -v

# Run specific test file
uv run --extra dev pytest tests/postman/test_health_endpoints.py
```

## Documentation

| Document                                  | Description                          |
| ----------------------------------------- | ------------------------------------ |
| [Architecture](architecture.md)           | System design and component overview |
| [Test Components](test-components.md)     | Core testing components              |
| [API Test Coverage](api-test-coverage.md) | Endpoint coverage matrix             |
| [Running Tests](running-tests.md)         | How to execute tests                 |
| [CI/CD Integration](ci-cd-integration.md) | GitHub Actions setup                 |
| [Troubleshooting](troubleshooting.md)     | Common issues and solutions          |

## Test File Overview

| Test File                     | Purpose                 | Endpoints Covered                          |
| ----------------------------- | ----------------------- | ------------------------------------------ |
| `test_config_management.py`   | Configuration loading   | N/A (config)                               |
| `test_postman_power.py`       | Postman Power client    | N/A (client)                               |
| `test_backend_health.py`      | Health verification     | `/api/health`                              |
| `test_environment_manager.py` | Environment variables   | N/A (utility)                              |
| `test_script_generator.py`    | Test script generation  | N/A (utility)                              |
| `test_data_generator.py`      | Test data generation    | N/A (utility)                              |
| `test_collection_builder.py`  | Collection building     | N/A (builder)                              |
| `test_health_endpoints.py`    | Health & infrastructure | `/`, `/api/health`, `/api/dashboard/stats` |
| `test_knowledge_api.py`       | Knowledge CRUD          | `/api/knowledge/*`                         |
| `test_audio_api.py`           | Audio operations        | `/api/audio/*`                             |
| `test_agent_api.py`           | Agent management        | `/api/agent/*`                             |
| `test_patient_api.py`         | Patient sessions        | `/api/patient/*`                           |
| `test_conversations_api.py`   | Conversations           | `/api/conversations/*`                     |
| `test_templates_api.py`       | Templates               | `/api/templates/*`                         |
| `test_error_handling.py`      | Error scenarios         | All endpoints                              |

## Related Resources

- [Spec Documentation](.kiro/specs/postman-backend-testing/)
- [Improvement Backlog](.kiro/specs/postman-backend-testing/needImprovement.md)
