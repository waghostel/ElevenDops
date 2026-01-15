# Requirements Document: Comprehensive Backend API Testing with Postman

## Introduction

This specification defines a comprehensive testing strategy for the ElevenDops backend API using the Postman Kiro Power. The goal is to create an automated, maintainable test suite that validates all backend endpoints, ensuring API correctness, reliability, and proper error handling.

## Glossary

- **Postman_Power**: Kiro Power that provides programmatic access to Postman API for collection management and test execution
- **Test_Collection**: A Postman collection containing organized API requests with test assertions
- **Environment**: Postman environment containing variables like base_url, API keys, and dynamic values
- **Test_Assertion**: JavaScript test script that validates response status, structure, and data
- **Backend_Server**: FastAPI application running on http://localhost:8000
- **Mock_Mode**: Testing mode where backend uses mock data services instead of real Firestore/GCS
- **Property_Test**: Test that validates universal properties across multiple inputs
- **Integration_Test**: Test that validates multiple endpoints working together in a workflow

## Requirements

### Requirement 1: Test Environment Setup

**User Story:** As a developer, I want to set up a complete Postman testing environment, so that I can run automated tests against the backend API.

#### Acceptance Criteria

1. WHEN the testing environment is initialized, THE System SHALL verify the backend server is running and accessible
2. WHEN the Postman Power is activated, THE System SHALL load existing configuration from .postman.json
3. WHEN environment variables are configured, THE System SHALL include base_url, authentication tokens, and dynamic test data
4. THE System SHALL support both mock mode and real service mode testing
5. WHEN the backend is not running, THE System SHALL provide clear instructions to start it

### Requirement 2: Health and Infrastructure Endpoints Testing

**User Story:** As a developer, I want to test health check and infrastructure endpoints, so that I can verify the backend is operational.

#### Acceptance Criteria

1. WHEN testing GET /, THE System SHALL verify response contains API title and version
2. WHEN testing GET /api/health, THE System SHALL verify all services report healthy status
3. WHEN testing GET /api/health/ready, THE System SHALL verify readiness probe returns ready status
4. WHEN testing GET /api/dashboard/stats, THE System SHALL verify response contains document_count, agent_count, audio_count, and last_activity
5. THE System SHALL validate response schemas match the defined Pydantic models

### Requirement 3: Knowledge Document API Testing

**User Story:** As a developer, I want to test knowledge document CRUD operations, so that I can ensure document management works correctly.

#### Acceptance Criteria

1. WHEN testing POST /api/knowledge, THE System SHALL create a document and verify sync_status is PENDING
2. WHEN testing GET /api/knowledge, THE System SHALL list all documents with correct pagination
3. WHEN testing GET /api/knowledge/{knowledge_id}, THE System SHALL retrieve a specific document
4. WHEN testing PUT /api/knowledge/{knowledge_id}, THE System SHALL update document fields and trigger re-sync if needed
5. WHEN testing DELETE /api/knowledge/{knowledge_id}, THE System SHALL remove the document from both database and ElevenLabs
6. WHEN testing POST /api/knowledge/{knowledge_id}/retry-sync, THE System SHALL retry failed synchronization
7. THE System SHALL validate structured_sections are parsed correctly from raw_content
8. THE System SHALL verify ElevenLabs document names follow the format "{disease_name}_{tag1_tag2}"

### Requirement 4: Audio Generation API Testing

**User Story:** As a developer, I want to test audio generation endpoints, so that I can ensure TTS and script generation work correctly.

#### Acceptance Criteria

1. WHEN testing GET /api/audio/voices/list, THE System SHALL return available voice options
2. WHEN testing POST /api/audio/generate-script, THE System SHALL generate a script from knowledge content
3. WHEN testing POST /api/audio/generate-script-stream, THE System SHALL stream script generation events
4. WHEN testing POST /api/audio/generate, THE System SHALL create audio from script and return audio_url
5. WHEN testing GET /api/audio/list, THE System SHALL list audio files with optional filters
6. WHEN testing GET /api/audio/stream/{audio_id}, THE System SHALL stream audio content
7. WHEN testing PUT /api/audio/{audio_id}, THE System SHALL update audio metadata
8. WHEN testing DELETE /api/audio/{audio_id}, THE System SHALL remove audio file and metadata
9. THE System SHALL validate rate limiting is enforced on audio generation endpoints

### Requirement 5: Agent Management API Testing

**User Story:** As a developer, I want to test agent configuration endpoints, so that I can ensure AI agents are properly managed.

#### Acceptance Criteria

1. WHEN testing POST /api/agent, THE System SHALL create an agent with specified configuration
2. WHEN testing GET /api/agent, THE System SHALL list all configured agents
3. WHEN testing PUT /api/agent/{agent_id}, THE System SHALL update agent configuration
4. WHEN testing DELETE /api/agent/{agent_id}, THE System SHALL remove the agent
5. WHEN testing GET /api/agent/system-prompts, THE System SHALL return available system prompts by style
6. THE System SHALL verify agents are linked to knowledge documents correctly
7. THE System SHALL validate rate limiting is enforced on agent creation

### Requirement 6: Patient Session API Testing

**User Story:** As a developer, I want to test patient conversation endpoints, so that I can ensure patient interactions work correctly.

#### Acceptance Criteria

1. WHEN testing POST /api/patient/session, THE System SHALL create a new conversation session
2. WHEN testing POST /api/patient/session/{session_id}/message, THE System SHALL send a message and receive audio response
3. WHEN testing POST /api/patient/session/{session_id}/end, THE System SHALL end the session and save conversation log
4. THE System SHALL verify session_id is returned and can be used for subsequent requests
5. THE System SHALL validate chat_mode parameter affects response behavior

### Requirement 7: Conversation Logs API Testing

**User Story:** As a developer, I want to test conversation log endpoints, so that I can ensure conversation history is properly tracked.

#### Acceptance Criteria

1. WHEN testing GET /api/conversations, THE System SHALL list conversations with optional filters
2. WHEN testing GET /api/conversations/statistics, THE System SHALL return conversation statistics
3. WHEN testing GET /api/conversations/{conversation_id}, THE System SHALL retrieve detailed conversation view
4. THE System SHALL verify filtering by patient_id, requires_attention_only, start_date, and end_date works correctly
5. THE System SHALL validate conversation analysis results are included in responses

### Requirement 8: Template Management API Testing

**User Story:** As a developer, I want to test prompt template endpoints, so that I can ensure template management works correctly.

#### Acceptance Criteria

1. WHEN testing GET /api/templates, THE System SHALL list all available templates
2. WHEN testing POST /api/templates, THE System SHALL create a custom template
3. WHEN testing GET /api/templates/{template_id}, THE System SHALL retrieve template content
4. WHEN testing PUT /api/templates/{template_id}, THE System SHALL update custom template
5. WHEN testing DELETE /api/templates/{template_id}, THE System SHALL remove custom template
6. WHEN testing GET /api/templates/system-prompt, THE System SHALL return base system prompt
7. WHEN testing POST /api/templates/preview, THE System SHALL preview combined prompt without generation

### Requirement 9: Debug API Testing (Non-Production Only)

**User Story:** As a developer, I want to test debug endpoints, so that I can ensure LangSmith tracing and debugging work correctly.

#### Acceptance Criteria

1. WHEN testing GET /api/debug/health, THE System SHALL verify LangSmith configuration status
2. WHEN testing POST /api/debug/script-generation, THE System SHALL execute workflow with full tracing
3. WHEN testing GET /api/debug/sessions, THE System SHALL list all debug sessions
4. WHEN testing POST /api/debug/sessions, THE System SHALL create a new debug session
5. WHEN testing GET /api/debug/sessions/{session_id}, THE System SHALL retrieve session details
6. WHEN testing POST /api/debug/sessions/{session_id}/end, THE System SHALL end the debug session
7. THE System SHALL verify debug endpoints are disabled in production environment

### Requirement 10: Integration Workflow Testing

**User Story:** As a developer, I want to test complete workflows, so that I can ensure multiple endpoints work together correctly.

#### Acceptance Criteria

1. WHEN testing the knowledge-to-audio workflow, THE System SHALL create document, generate script, and create audio
2. WHEN testing the agent setup workflow, THE System SHALL create document, create agent, and link knowledge
3. WHEN testing the patient conversation workflow, THE System SHALL create session, send messages, and end session
4. THE System SHALL verify data consistency across related endpoints
5. THE System SHALL validate that created resources can be retrieved and deleted

### Requirement 11: Error Handling and Edge Cases Testing

**User Story:** As a developer, I want to test error scenarios, so that I can ensure the API handles failures gracefully.

#### Acceptance Criteria

1. WHEN testing with invalid IDs, THE System SHALL return 404 Not Found
2. WHEN testing with malformed request bodies, THE System SHALL return 400 Bad Request
3. WHEN testing with missing required fields, THE System SHALL return 422 Unprocessable Entity
4. WHEN testing rate-limited endpoints excessively, THE System SHALL return 429 Too Many Requests
5. WHEN testing with ElevenLabs service failures, THE System SHALL return 502 Bad Gateway
6. THE System SHALL verify error responses include descriptive error messages
7. THE System SHALL validate error response schemas match ErrorResponse model

### Requirement 12: Test Collection Organization and Maintenance

**User Story:** As a developer, I want well-organized test collections, so that I can easily maintain and extend tests.

#### Acceptance Criteria

1. THE System SHALL organize tests into folders by API domain (health, knowledge, audio, agent, patient, conversations, templates, debug)
2. THE System SHALL use descriptive request names that indicate what is being tested
3. THE System SHALL include pre-request scripts for setup (e.g., creating test data)
4. THE System SHALL include test scripts with clear assertions and error messages
5. THE System SHALL use collection variables for shared test data (e.g., created IDs)
6. THE System SHALL include cleanup requests to remove test data after execution
7. THE System SHALL document each request with description and expected behavior

### Requirement 13: Automated Test Execution and Reporting

**User Story:** As a developer, I want automated test execution, so that I can run tests efficiently and get clear results.

#### Acceptance Criteria

1. WHEN running the test collection, THE System SHALL execute all requests in the correct order
2. WHEN tests complete, THE System SHALL generate a summary report with pass/fail counts
3. WHEN tests fail, THE System SHALL provide detailed failure information
4. THE System SHALL update .postman.json with test results and timestamps
5. THE System SHALL support running specific test folders independently
6. THE System SHALL allow configuring iteration count and timeout values
7. THE System SHALL continue execution on failure to run all tests

### Requirement 14: Environment Variable Management

**User Story:** As a developer, I want proper environment variable management, so that I can test against different configurations.

#### Acceptance Criteria

1. THE System SHALL maintain separate environments for mock mode and real service mode
2. THE System SHALL support dynamic variables that are set during test execution
3. THE System SHALL include variables for base_url, api_keys, and test data IDs
4. THE System SHALL allow easy switching between local and deployed environments
5. THE System SHALL validate required environment variables are set before running tests

### Requirement 15: Test Data Generation and Cleanup

**User Story:** As a developer, I want automated test data management, so that tests are repeatable and don't leave orphaned data.

#### Acceptance Criteria

1. WHEN tests create resources, THE System SHALL store their IDs in collection variables
2. WHEN tests complete, THE System SHALL clean up created resources
3. THE System SHALL generate realistic test data for each request
4. THE System SHALL handle cleanup failures gracefully
5. THE System SHALL support running tests multiple times without conflicts
