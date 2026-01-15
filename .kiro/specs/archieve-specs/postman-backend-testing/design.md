# Design Document: Comprehensive Backend API Testing with Postman

## Overview

This design document outlines the architecture and implementation strategy for comprehensive backend API testing using the Postman Kiro Power. The solution will create an automated, maintainable test suite that validates all ElevenDops backend endpoints through programmatic Postman collection management and execution.

The testing framework will support both mock mode (for fast, isolated testing) and real service mode (for integration testing), with clear organization, reusable test patterns, and automated cleanup.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Test Orchestration Layer                  │
│  (Kiro Agent + Postman Power + Test Execution Scripts)      │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─── Postman API (via Kiro Power)
                 │    ├─── Collection Management
                 │    ├─── Environment Management
                 │    └─── Test Execution (Newman)
                 │
                 ├─── Backend Server (FastAPI)
                 │    ├─── Health & Infrastructure
                 │    ├─── Knowledge API
                 │    ├─── Audio API
                 │    ├─── Agent API
                 │    ├─── Patient API
                 │    ├─── Conversations API
                 │    ├─── Templates API
                 │    └─── Debug API
                 │
                 └─── Test Configuration
                      ├─── .postman.json (IDs & metadata)
                      ├─── Environment Variables
                      └─── Test Data Generators
```

### Testing Modes

1. **Mock Mode**: Backend uses mock data services (fast, no external dependencies)
2. **Real Service Mode**: Backend uses actual Firestore/GCS/ElevenLabs (integration testing)
3. **Hybrid Mode**: Some services mocked, others real (targeted testing)

### Test Organization Strategy

Tests are organized into a hierarchical folder structure within the Postman collection:

```
ElevenDops Backend API Tests
├── 00-Setup
│   └── Verify Backend Health
├── 01-Health-Infrastructure
│   ├── Root Endpoint
│   ├── Health Check
│   ├── Readiness Check
│   └── Dashboard Stats
├── 02-Knowledge-API
│   ├── Create Document
│   ├── List Documents
│   ├── Get Document
│   ├── Update Document
│   ├── Delete Document
│   └── Retry Sync
├── 03-Audio-API
│   ├── List Voices
│   ├── Generate Script
│   ├── Generate Script Stream
│   ├── Generate Audio
│   ├── List Audio Files
│   ├── Stream Audio
│   ├── Update Audio
│   └── Delete Audio
├── 04-Agent-API
│   ├── Create Agent
│   ├── List Agents
│   ├── Update Agent
│   ├── Delete Agent
│   └── Get System Prompts
├── 05-Patient-API
│   ├── Create Session
│   ├── Send Message
│   └── End Session
├── 06-Conversations-API
│   ├── List Conversations
│   ├── Get Statistics
│   └── Get Conversation Detail
├── 07-Templates-API
│   ├── List Templates
│   ├── Create Custom Template
│   ├── Get Template
│   ├── Update Template
│   ├── Delete Template
│   ├── Get System Prompt
│   └── Preview Combined Prompt
├── 08-Debug-API (Non-Production)
│   ├── Debug Health
│   ├── Execute Script Generation
│   ├── List Sessions
│   ├── Create Session
│   ├── Get Session
│   └── End Session
├── 09-Integration-Workflows
│   ├── Knowledge-to-Audio Workflow
│   ├── Agent Setup Workflow
│   └── Patient Conversation Workflow
├── 10-Error-Handling
│   ├── Invalid IDs (404)
│   ├── Malformed Bodies (400)
│   ├── Missing Fields (422)
│   ├── Rate Limiting (429)
│   └── Service Failures (502)
└── 99-Cleanup
    ├── Delete Test Audio
    ├── Delete Test Agents
    ├── Delete Test Documents
    └── Delete Test Templates
```

## Components and Interfaces

### 1. Test Orchestration Component

**Responsibility**: Coordinate test execution using Postman Kiro Power

**Key Functions**:
- `activate_postman_power()`: Activate Postman Power and load tools
- `load_configuration()`: Read .postman.json for workspace/collection IDs
- `verify_backend_health()`: Check backend is running before tests
- `run_test_collection()`: Execute full test suite
- `run_test_folder()`: Execute specific test folder
- `update_test_results()`: Save test results to .postman.json

**Interface**:
```python
class TestOrchestrator:
    def __init__(self, config_path: str = ".postman.json"):
        self.config = self.load_configuration(config_path)
        self.postman_power = None
    
    async def activate_postman_power(self) -> dict:
        """Activate Postman Power and return available tools."""
        pass
    
    async def verify_backend_health(self) -> bool:
        """Check if backend is accessible."""
        pass
    
    async def run_test_collection(
        self, 
        stop_on_error: bool = False,
        iteration_count: int = 1
    ) -> TestResults:
        """Execute full test collection."""
        pass
    
    async def run_test_folder(self, folder_name: str) -> TestResults:
        """Execute specific test folder."""
        pass
```

### 2. Collection Builder Component

**Responsibility**: Create and update Postman collections programmatically

**Key Functions**:
- `create_collection()`: Create new test collection
- `add_folder()`: Add folder to collection
- `add_request()`: Add test request to folder
- `add_test_script()`: Add test assertions to request
- `add_pre_request_script()`: Add setup logic to request
- `update_collection()`: Update existing collection

**Interface**:
```python
class CollectionBuilder:
    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id
        self.collection_structure = {}
    
    def create_collection(self, name: str, description: str) -> dict:
        """Create new collection structure."""
        pass
    
    def add_folder(self, folder_name: str, parent: str = None) -> None:
        """Add folder to collection."""
        pass
    
    def add_request(
        self,
        folder: str,
        name: str,
        method: str,
        url: str,
        body: dict = None,
        headers: dict = None
    ) -> None:
        """Add request to folder."""
        pass
    
    def add_test_script(self, request_name: str, test_code: str) -> None:
        """Add test assertions to request."""
        pass
    
    def build(self) -> dict:
        """Build final collection JSON."""
        pass
```

### 3. Environment Manager Component

**Responsibility**: Manage Postman environment variables

**Key Functions**:
- `create_environment()`: Create new environment
- `set_variable()`: Set environment variable
- `get_variable()`: Get environment variable
- `update_environment()`: Update existing environment

**Interface**:
```python
class EnvironmentManager:
    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id
        self.variables = {}
    
    def create_environment(self, name: str) -> dict:
        """Create new environment."""
        pass
    
    def set_variable(self, key: str, value: str, enabled: bool = True) -> None:
        """Set environment variable."""
        pass
    
    def build(self) -> dict:
        """Build final environment JSON."""
        pass
```

### 4. Test Script Generator Component

**Responsibility**: Generate JavaScript test scripts for Postman requests

**Key Functions**:
- `generate_status_check()`: Generate status code assertion
- `generate_schema_validation()`: Generate response schema validation
- `generate_field_check()`: Generate field existence check
- `generate_value_assertion()`: Generate value comparison
- `generate_variable_save()`: Generate variable storage for chaining

**Interface**:
```python
class TestScriptGenerator:
    @staticmethod
    def generate_status_check(expected_status: int) -> str:
        """Generate status code test."""
        return f"""
pm.test('Status code is {expected_status}', function () {{
    pm.response.to.have.status({expected_status});
}});
"""
    
    @staticmethod
    def generate_schema_validation(required_fields: list[str]) -> str:
        """Generate schema validation test."""
        pass
    
    @staticmethod
    def generate_variable_save(var_name: str, json_path: str) -> str:
        """Generate variable save script."""
        pass
```

### 5. Test Data Generator Component

**Responsibility**: Generate realistic test data for requests

**Key Functions**:
- `generate_knowledge_document()`: Generate test knowledge document
- `generate_audio_request()`: Generate audio generation request
- `generate_agent_config()`: Generate agent configuration
- `generate_patient_session()`: Generate patient session data

**Interface**:
```python
class TestDataGenerator:
    @staticmethod
    def generate_knowledge_document() -> dict:
        """Generate test knowledge document."""
        return {
            "disease_name": "Test Disease",
            "tags": ["test", "automated"],
            "raw_content": "# Test Content\n\nThis is test content.",
            "doctor_id": "test_doctor_001"
        }
    
    @staticmethod
    def generate_audio_request(knowledge_id: str) -> dict:
        """Generate audio generation request."""
        pass
```

### 6. Results Reporter Component

**Responsibility**: Process and report test results

**Key Functions**:
- `parse_results()`: Parse Newman execution results
- `generate_summary()`: Generate test summary
- `update_config_file()`: Update .postman.json with results
- `format_failures()`: Format failure details

**Interface**:
```python
class ResultsReporter:
    def __init__(self, results: dict):
        self.results = results
    
    def parse_results(self) -> dict:
        """Parse Newman results."""
        pass
    
    def generate_summary(self) -> str:
        """Generate human-readable summary."""
        pass
    
    def get_failures(self) -> list[dict]:
        """Get list of failed tests."""
        pass
```

## Data Models

### Configuration Model

```python
class PostmanConfig:
    workspace_id: str
    collection_id: str
    collection_uid: str
    environment_id: str
    environment_uid: str
    base_url: str
    description: str
    created_at: datetime
    updated_at: datetime
    test_results: TestResults
```

### Test Results Model

```python
class TestResults:
    backend_status: str  # "running" | "stopped"
    endpoints_tested: list[EndpointResult]
    last_tested: datetime
    total_tests: int
    passed_tests: int
    failed_tests: int
    execution_time_ms: int
```

### Endpoint Result Model

```python
class EndpointResult:
    endpoint: str
    method: str
    status: str  # "✅ working" | "❌ failed" | "⚠️ warning"
    response_time_ms: int
    response: str  # Brief response summary
    error: Optional[str]
```

### Request Template Model

```python
class RequestTemplate:
    name: str
    method: str  # GET, POST, PUT, DELETE
    url: str
    headers: dict[str, str]
    body: Optional[dict]
    tests: list[str]  # JavaScript test scripts
    pre_request: Optional[str]  # Pre-request script
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

After analyzing all acceptance criteria, I've identified several areas where properties can be consolidated:

**Redundancy Analysis:**

1. **CRUD Round-Trip Properties**: Multiple requirements test create-retrieve-update-delete cycles for different resources (knowledge, audio, agents, templates, conversations). These can be consolidated into a single universal CRUD property that applies to all resources.

2. **Error Response Properties**: Requirements 11.1, 11.2, 11.3 all test that different error conditions return appropriate status codes. These can be combined into a single error handling property.

3. **Deletion Properties**: Requirements 3.5, 4.8, 5.4, 8.5 all test that after deletion, GET returns 404. This is the same property applied to different resources.

4. **Update Properties**: Requirements 3.4, 4.7, 5.3, 8.4 all test that updates are reflected when retrieving. This is the same property.

5. **Rate Limiting Properties**: Requirements 4.9 and 5.7 both test rate limiting. These can be combined.

6. **Filtering Properties**: Requirements 4.5, 7.1, 7.4 all test filtering behavior. These can be consolidated.

**Consolidated Properties:**

After reflection, we'll focus on these unique, high-value properties:

1. **Backend Health Verification** (1.1)
2. **Configuration Loading** (1.2)
3. **Environment Completeness** (1.3, 14.3, 14.5)
4. **Response Schema Validation** (2.5) - Universal across all endpoints
5. **CRUD Round-Trip** (3.3, 8.3, 9.5) - Universal create-retrieve-update-delete
6. **Resource Deletion** (3.5, 4.8, 5.4, 8.5) - Universal deletion verification
7. **Data Transformation** (3.7) - Structured sections parsing
8. **Naming Convention** (3.8) - ElevenLabs document naming
9. **Script Generation** (4.2) - Knowledge to script transformation
10. **Streaming Format** (4.3) - SSE format validation
11. **Audio Generation** (4.4) - Script to audio transformation
12. **Filtering Behavior** (4.5, 7.1, 7.4) - Universal filtering
13. **Rate Limiting** (4.9, 5.7, 11.4) - Universal rate limit enforcement
14. **Relationship Integrity** (5.6) - Agent-knowledge linking
15. **Session Management** (6.4) - Session ID usage
16. **Workflow Integrity** (10.1, 10.2, 10.3) - Multi-step workflows
17. **Data Consistency** (10.4) - Cross-endpoint consistency
18. **Error Handling** (11.1, 11.2, 11.3) - Universal error responses
19. **Error Message Quality** (11.6, 11.7) - Error response structure
20. **Test Execution Order** (13.1) - Sequential execution
21. **Result Reporting** (13.2, 13.3, 13.4) - Test result generation
22. **Variable Chaining** (14.2, 15.1) - Dynamic variable management
23. **Cleanup Execution** (12.6, 15.2) - Resource cleanup
24. **Test Idempotence** (15.5) - Multiple execution support

### Converting EARS to Properties

Based on the prework analysis and property reflection, here are the consolidated correctness properties:

**Property 1: Backend Health Verification**
*For any* test execution, before running tests, the backend health check endpoint should return a successful response indicating all services are operational.
**Validates: Requirements 1.1**

**Property 2: Configuration Loading Completeness**
*For any* test initialization, after activating the Postman Power, the loaded configuration should contain all required fields (workspace_id, collection_id, collection_uid, environment_id, base_url).
**Validates: Requirements 1.2**

**Property 3: Environment Variable Completeness**
*For any* test environment, it should contain all required variables (base_url, api_keys, test data IDs) before test execution begins.
**Validates: Requirements 1.3, 14.3, 14.5**

**Property 4: Universal Response Schema Validation**
*For any* API endpoint response, the response structure should match the defined Pydantic model schema for that endpoint.
**Validates: Requirements 2.5**

**Property 5: CRUD Round-Trip Consistency**
*For any* resource type (knowledge, audio, agent, template, conversation), creating a resource and then retrieving it should return data equivalent to what was created.
**Validates: Requirements 3.3, 8.3, 9.5**

**Property 6: Update Persistence**
*For any* resource type that supports updates, updating a resource and then retrieving it should reflect all the updated fields.
**Validates: Requirements 3.4, 4.7, 5.3, 8.4**

**Property 7: Deletion Verification**
*For any* resource type that supports deletion, after deleting a resource, attempting to retrieve it should return 404 Not Found.
**Validates: Requirements 3.5, 4.8, 5.4, 8.5**

**Property 8: Structured Content Parsing**
*For any* knowledge document with raw_content containing markdown sections, the parsed structured_sections should correctly extract all section headers and content.
**Validates: Requirements 3.7**

**Property 9: ElevenLabs Naming Convention**
*For any* knowledge document created with disease_name and tags, the ElevenLabs document name should follow the format "{disease_name}_{tag1_tag2...}".
**Validates: Requirements 3.8**

**Property 10: Script Generation from Knowledge**
*For any* knowledge document content, generating a script should produce non-empty script text that is derived from the knowledge content.
**Validates: Requirements 4.2**

**Property 11: SSE Streaming Format**
*For any* streaming script generation request, all events should be formatted as valid Server-Sent Events with "data: " prefix and proper JSON structure.
**Validates: Requirements 4.3**

**Property 12: Audio Generation from Script**
*For any* valid script text and voice_id, generating audio should produce an audio file with a valid audio_url that is accessible.
**Validates: Requirements 4.4**

**Property 13: Universal Filtering Behavior**
*For any* list endpoint that supports filtering (audio, conversations), applying a filter should return only results that match the filter criteria.
**Validates: Requirements 4.5, 7.1, 7.4**

**Property 14: Rate Limiting Enforcement**
*For any* rate-limited endpoint, making requests exceeding the rate limit should return 429 Too Many Requests status code.
**Validates: Requirements 4.9, 5.7, 11.4**

**Property 15: Agent-Knowledge Relationship Integrity**
*For any* agent created with knowledge_ids, retrieving the agent should show those knowledge_ids in its configuration, and the knowledge documents should exist.
**Validates: Requirements 5.6**

**Property 16: Session ID Continuity**
*For any* patient session created, the returned session_id should be usable for sending messages and ending the session without errors.
**Validates: Requirements 6.4**

**Property 17: Chat Mode Parameter Effect**
*For any* patient message sent with different chat_mode values, the response behavior should differ according to the mode (e.g., streaming vs non-streaming).
**Validates: Requirements 6.5**

**Property 18: Conversation Retrieval After Session End**
*For any* patient session that is ended, the conversation should be retrievable through the conversations API with all messages intact.
**Validates: Requirements 6.3, 7.3**

**Property 19: Conversation Analysis Inclusion**
*For any* conversation retrieved, the response should include analysis results (sentiment, topics, requires_attention flag).
**Validates: Requirements 7.5**

**Property 20: Template Preview Accuracy**
*For any* combination of template_ids and quick_instructions, the preview endpoint should return the same combined prompt that would be used for actual script generation.
**Validates: Requirements 8.7**

**Property 21: Debug Trace Completeness**
*For any* debug script generation execution, the returned trace should include all workflow steps with timing information and any errors encountered.
**Validates: Requirements 9.2**

**Property 22: Debug Session State Transitions**
*For any* debug session, after ending it, retrieving the session should show status as "ended" and ended_at timestamp should be set.
**Validates: Requirements 9.6**

**Property 23: Knowledge-to-Audio Workflow Integrity**
*For any* complete knowledge-to-audio workflow (create document → generate script → generate audio), each step should succeed and the audio should reference the original knowledge document.
**Validates: Requirements 10.1**

**Property 24: Agent Setup Workflow Integrity**
*For any* agent setup workflow (create document → create agent with knowledge_ids), the agent should be successfully linked to the document and retrievable.
**Validates: Requirements 10.2**

**Property 25: Patient Conversation Workflow Integrity**
*For any* patient conversation workflow (create session → send messages → end session), all steps should succeed and the conversation should be saved with all messages.
**Validates: Requirements 10.3**

**Property 26: Cross-Endpoint Data Consistency**
*For any* resource created through one endpoint, it should be retrievable and consistent when accessed through related endpoints (e.g., audio created should appear in audio list).
**Validates: Requirements 10.4**

**Property 27: Resource Lifecycle Completeness**
*For any* resource type, the complete lifecycle (create → retrieve → update → delete → verify deletion) should work without errors.
**Validates: Requirements 10.5**

**Property 28: Invalid ID Error Handling**
*For any* endpoint that accepts a resource ID, providing a non-existent ID should return 404 Not Found with a descriptive error message.
**Validates: Requirements 11.1**

**Property 29: Malformed Request Error Handling**
*For any* endpoint that accepts a request body, providing malformed JSON should return 400 Bad Request with a descriptive error message.
**Validates: Requirements 11.2**

**Property 30: Missing Field Validation**
*For any* endpoint that requires specific fields, omitting a required field should return 422 Unprocessable Entity with details about the missing field.
**Validates: Requirements 11.3**

**Property 31: Error Message Descriptiveness**
*For any* error response, the error message should clearly describe what went wrong and provide actionable information.
**Validates: Requirements 11.6**

**Property 32: Error Response Schema Consistency**
*For any* error response, it should follow the ErrorResponse model schema with status, message, and optional details fields.
**Validates: Requirements 11.7**

**Property 33: Test Execution Sequential Order**
*For any* test collection execution, requests should execute in the order they are defined in the collection structure.
**Validates: Requirements 13.1**

**Property 34: Test Result Summary Generation**
*For any* test collection execution, after completion, a summary should be generated containing total tests, passed tests, failed tests, and execution time.
**Validates: Requirements 13.2**

**Property 35: Test Failure Detail Reporting**
*For any* failed test, the failure report should include the request name, expected result, actual result, and error message.
**Validates: Requirements 13.3**

**Property 36: Configuration File Update**
*For any* test collection execution, after completion, the .postman.json file should be updated with test results and timestamp.
**Validates: Requirements 13.4**

**Property 37: Selective Folder Execution**
*For any* test folder in the collection, it should be executable independently without requiring the entire collection to run.
**Validates: Requirements 13.5**

**Property 38: Execution Configuration Flexibility**
*For any* test execution, configuring different iteration counts and timeout values should affect the execution behavior accordingly.
**Validates: Requirements 13.6**

**Property 39: Failure Isolation**
*For any* test collection execution with stop_on_error=false, a single test failure should not prevent subsequent tests from executing.
**Validates: Requirements 13.7**

**Property 40: Dynamic Variable Chaining**
*For any* test that creates a resource and saves its ID to a collection variable, subsequent tests should be able to use that variable to reference the resource.
**Validates: Requirements 14.2, 15.1**

**Property 41: Cleanup Request Execution**
*For any* test collection execution, cleanup requests should execute after main tests and successfully delete created resources.
**Validates: Requirements 12.6, 15.2**

**Property 42: Cleanup Failure Resilience**
*For any* cleanup request that fails, the failure should be logged but should not cause the entire test suite to fail.
**Validates: Requirements 15.4**

**Property 43: Test Idempotence**
*For any* test collection, running it multiple times in sequence should produce consistent results without conflicts from previous runs.
**Validates: Requirements 15.5**

## Error Handling

### Error Categories

1. **Configuration Errors**
   - Missing .postman.json file
   - Invalid workspace/collection IDs
   - Missing environment variables
   - **Handling**: Fail fast with clear error message and setup instructions

2. **Backend Connectivity Errors**
   - Backend not running
   - Backend not responding
   - Network timeouts
   - **Handling**: Provide instructions to start backend, retry logic with exponential backoff

3. **Test Execution Errors**
   - Test assertion failures
   - Request timeouts
   - Invalid response formats
   - **Handling**: Log detailed failure information, continue with remaining tests (unless stop_on_error=true)

4. **Postman API Errors**
   - Rate limiting (429)
   - Authentication failures (401)
   - Resource not found (404)
   - **Handling**: Retry with backoff for rate limits, fail with clear message for auth/not found

5. **Cleanup Errors**
   - Resource already deleted
   - Permission denied
   - Service unavailable
   - **Handling**: Log warning but don't fail test suite, allow manual cleanup

### Error Response Format

All errors should follow a consistent format:

```json
{
  "error_type": "ConfigurationError",
  "message": "Missing required configuration",
  "details": {
    "missing_fields": ["workspace_id"],
    "config_file": ".postman.json"
  },
  "suggested_action": "Create .postman.json with required fields or run setup script"
}
```

### Retry Strategy

For transient errors (network, rate limiting):
- Initial retry delay: 1 second
- Maximum retries: 3
- Backoff multiplier: 2x
- Maximum delay: 10 seconds

## Testing Strategy

### Dual Testing Approach

This specification requires both **unit tests** and **property-based tests** to ensure comprehensive coverage:

**Unit Tests** focus on:
- Specific endpoint examples (GET /, GET /api/health, etc.)
- Edge cases (empty lists, single items, maximum pagination)
- Error conditions (404, 400, 422, 429, 502)
- Integration points (Postman Power activation, configuration loading)

**Property-Based Tests** focus on:
- Universal properties across all resources (CRUD round-trip, deletion verification)
- Filtering behavior with random filter combinations
- Rate limiting with varying request counts
- Workflow integrity with different resource combinations
- Error handling with randomly generated invalid inputs

### Property Test Configuration

All property-based tests should:
- Run minimum **100 iterations** per property test
- Use Hypothesis library for Python implementation
- Generate realistic test data (valid knowledge documents, scripts, agent configs)
- Tag each test with format: **Feature: postman-backend-testing, Property {number}: {property_text}**

### Test Organization

Tests are organized into three layers:

1. **Unit Tests** (`tests/test_postman_unit.py`)
   - Test individual components (CollectionBuilder, EnvironmentManager, TestScriptGenerator)
   - Test specific endpoint examples
   - Test error handling for known cases

2. **Property Tests** (`tests/test_postman_properties.py`)
   - Test universal properties across all resources
   - Test with randomly generated valid and invalid inputs
   - Test workflow integrity with various combinations

3. **Integration Tests** (`tests/test_postman_integration.py`)
   - Test complete workflows end-to-end
   - Test Postman Power integration
   - Test backend API integration

### Test Execution Flow

```
1. Setup Phase
   ├── Activate Postman Power
   ├── Load configuration from .postman.json
   ├── Verify backend health
   └── Initialize test environment

2. Test Execution Phase
   ├── Run unit tests (specific examples)
   ├── Run property tests (universal properties)
   └── Run integration tests (workflows)

3. Reporting Phase
   ├── Generate test summary
   ├── Update .postman.json with results
   └── Output detailed failure information

4. Cleanup Phase
   ├── Delete created test resources
   ├── Reset environment variables
   └── Close connections
```

### Test Data Strategy

**Test Data Generators** create realistic data:

```python
# Knowledge Document Generator
def generate_test_knowledge_document():
    return {
        "disease_name": f"Test_Disease_{uuid.uuid4().hex[:8]}",
        "tags": ["test", "automated", random.choice(["surgery", "medication"])],
        "raw_content": generate_markdown_content(),
        "doctor_id": "test_doctor_001"
    }

# Audio Request Generator
def generate_test_audio_request(knowledge_id: str):
    return {
        "script": generate_test_script(),
        "voice_id": random.choice(["voice_1", "voice_2"]),
        "knowledge_id": knowledge_id,
        "doctor_id": "test_doctor_001",
        "name": f"Test Audio {uuid.uuid4().hex[:8]}",
        "description": "Automated test audio"
    }
```

### Cleanup Strategy

**Automatic Cleanup**:
- Track all created resource IDs in collection variables
- Execute cleanup requests in reverse order of creation
- Log cleanup failures but don't fail test suite

**Manual Cleanup** (if automatic fails):
- Provide script to list and delete test resources
- Filter by naming convention (Test_*, test_*)
- Confirm before deletion

### Continuous Integration

For CI/CD integration:
- Run tests in mock mode for fast feedback
- Run tests in real service mode nightly
- Fail build on test failures
- Generate test reports in JUnit XML format
- Upload test results to test reporting service

## Implementation Notes

### Technology Stack

- **Language**: Python 3.11+
- **Testing Framework**: pytest
- **Property Testing**: Hypothesis
- **HTTP Client**: httpx (async support)
- **Postman Integration**: Postman Kiro Power
- **Configuration**: Pydantic for validation

### File Structure

```
.kiro/specs/postman-backend-testing/
├── requirements.md          # This requirements document
├── design.md               # This design document
└── tasks.md                # Implementation tasks (to be created)

tests/
├── test_postman_unit.py           # Unit tests
├── test_postman_properties.py     # Property-based tests
├── test_postman_integration.py    # Integration tests
└── postman_test_helpers.py        # Shared test utilities

scripts/
└── postman_test_runner.py         # CLI for running tests

.postman.json                       # Postman configuration
```

### Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.11"
httpx = "^0.25.0"
pydantic = "^2.5.0"
pytest = "^7.4.0"
hypothesis = "^6.92.0"
```

### Performance Considerations

- **Parallel Execution**: Run independent test folders in parallel
- **Caching**: Cache backend health check for 30 seconds
- **Connection Pooling**: Reuse HTTP connections across tests
- **Timeout Configuration**: Set appropriate timeouts for long-running operations (script generation, audio generation)

### Security Considerations

- **API Keys**: Store in environment variables, never in code
- **Test Data**: Use clearly marked test data to avoid confusion with production
- **Cleanup**: Ensure test data is deleted to avoid accumulation
- **Rate Limiting**: Respect rate limits to avoid service disruption
