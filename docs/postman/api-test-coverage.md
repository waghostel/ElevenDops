# API Test Coverage

## Endpoint Coverage Matrix

| Endpoint                            | Method           | Test File                   | Property Tests |
| ----------------------------------- | ---------------- | --------------------------- | -------------- |
| `/`                                 | GET              | `test_health_endpoints.py`  | ✅ Schema      |
| `/api/health`                       | GET              | `test_health_endpoints.py`  | ✅ Status      |
| `/api/health/ready`                 | GET              | `test_health_endpoints.py`  | ✅ Readiness   |
| `/api/dashboard/stats`              | GET              | `test_health_endpoints.py`  | ✅ Stats       |
| `/api/knowledge`                    | GET, POST        | `test_knowledge_api.py`     | ✅ CRUD        |
| `/api/knowledge/{id}`               | GET, PUT, DELETE | `test_knowledge_api.py`     | ✅ Round-trip  |
| `/api/audio/voices/list`            | GET              | `test_audio_api.py`         | ✅ List        |
| `/api/audio/generate`               | POST             | `test_audio_api.py`         | ✅ Generate    |
| `/api/audio/generate-script`        | POST             | `test_audio_api.py`         | ✅ Script      |
| `/api/audio/list`                   | GET              | `test_audio_api.py`         | ✅ Filter      |
| `/api/agent`                        | GET, POST        | `test_agent_api.py`         | ✅ CRUD        |
| `/api/agent/{id}`                   | GET, PUT, DELETE | `test_agent_api.py`         | ✅ Lifecycle   |
| `/api/patient/session`              | POST             | `test_patient_api.py`       | ✅ Session     |
| `/api/patient/session/{id}/message` | POST             | `test_patient_api.py`       | ✅ Message     |
| `/api/patient/session/{id}/end`     | POST             | `test_patient_api.py`       | ✅ End         |
| `/api/conversations`                | GET              | `test_conversations_api.py` | ✅ Query       |
| `/api/conversations/{id}`           | GET              | `test_conversations_api.py` | ✅ Detail      |
| `/api/templates`                    | GET, POST        | `test_templates_api.py`     | ✅ CRUD        |
| `/api/templates/{id}`               | GET, PUT, DELETE | `test_templates_api.py`     | ✅ Lifecycle   |

## Property Tests Summary

- **Total Property Tests**: 40+
- **Minimum Iterations**: 100 per test
- **Coverage Areas**:
  - CRUD operations
  - Error handling
  - Schema validation
  - Response timing
