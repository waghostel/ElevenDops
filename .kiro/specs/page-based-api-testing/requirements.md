# Requirements Document

## Introduction

This feature provides a comprehensive backend API testing script that tests all APIs organized by Streamlit page. The script will execute tests against the FastAPI backend and generate a report showing which APIs passed or failed, grouped by the frontend page that uses them.

## Glossary

- **Test_Script**: The Python testing script that executes API tests
- **API_Endpoint**: A specific backend route that can be called via HTTP
- **Page_Group**: A logical grouping of APIs based on which Streamlit page uses them
- **Test_Report**: The output document showing test results organized by page
- **Test_Result**: The outcome of a single API test (success/failure with details)

## Requirements

### Requirement 1: Page-Based API Organization

**User Story:** As a developer, I want APIs organized by Streamlit page, so that I can quickly identify which page functionality is affected by API failures.

#### Acceptance Criteria

1. THE Test_Script SHALL organize API tests into the following page groups:
   - Doctor Dashboard (1_Doctor_Dashboard.py)
   - Upload Knowledge (2_Upload_Knowledge.py)
   - Education Audio (3_Education_Audio.py)
   - Agent Setup (4_Agent_Setup.py)
   - Patient Test (5_Patient_Test.py)
   - Conversation Logs (6_Conversation_Logs.py)
   - Shared/Health (common APIs)

2. WHEN executing tests, THE Test_Script SHALL test APIs in page group order

3. THE Test_Script SHALL map each API endpoint to its corresponding page based on BackendAPIClient usage

### Requirement 2: API Endpoint Coverage

**User Story:** As a developer, I want all backend APIs tested, so that I can verify the entire backend is functioning correctly.

#### Acceptance Criteria

1. THE Test_Script SHALL test the following Health/Shared APIs:
   - GET /api/health
   - GET /api/health/ready

2. THE Test_Script SHALL test the following Dashboard APIs:
   - GET /api/dashboard/stats

3. THE Test_Script SHALL test the following Knowledge APIs:
   - POST /api/knowledge (create document)
   - GET /api/knowledge (list documents)
   - GET /api/knowledge/{id} (get single document)
   - DELETE /api/knowledge/{id} (delete document)
   - POST /api/knowledge/{id}/retry-sync (retry sync)

4. THE Test_Script SHALL test the following Audio APIs:
   - POST /api/audio/generate-script
   - POST /api/audio/generate
   - GET /api/audio/{knowledge_id}
   - GET /api/audio/voices/list

5. THE Test_Script SHALL test the following Agent APIs:
   - POST /api/agent (create agent)
   - GET /api/agent (list agents)
   - DELETE /api/agent/{id} (delete agent)

6. THE Test_Script SHALL test the following Patient APIs:
   - POST /api/patient/session (create session)
   - POST /api/patient/session/{id}/message (send message)
   - POST /api/patient/session/{id}/end (end session)

7. THE Test_Script SHALL test the following Conversation APIs:
   - GET /api/conversations (list with filters)
   - GET /api/conversations/statistics
   - GET /api/conversations/{id} (get detail)

### Requirement 3: Test Execution and Result Capture

**User Story:** As a developer, I want clear test results with timing information, so that I can diagnose issues quickly.

#### Acceptance Criteria

1. WHEN a test executes successfully, THE Test_Script SHALL record:
   - API endpoint tested
   - HTTP status code
   - Response time in milliseconds
   - Success indicator

2. WHEN a test fails, THE Test_Script SHALL record:
   - API endpoint tested
   - HTTP status code (if available)
   - Error message
   - Response time (if available)
   - Failure indicator

3. THE Test_Script SHALL handle connection errors gracefully and record them as failures

4. THE Test_Script SHALL support configurable timeout for API calls

5. THE Test_Script SHALL support configurable backend URL via environment variable or parameter

### Requirement 4: Report Generation

**User Story:** As a developer, I want a clear report showing test results by page, so that I can quickly assess system health.

#### Acceptance Criteria

1. WHEN all tests complete, THE Test_Script SHALL generate a report containing:
   - Overall summary (total tests, passed, failed, pass rate)
   - Per-page breakdown with pass/fail counts
   - Detailed results for each API test

2. THE Test_Report SHALL display results grouped by page with clear visual separation

3. THE Test_Report SHALL highlight failed tests with error details

4. THE Test_Report SHALL include execution timestamp and total duration

5. THE Test_Report SHALL be output to console with optional file export

6. WHEN exporting to file, THE Test_Script SHALL support Markdown format

### Requirement 5: Test Data Management

**User Story:** As a developer, I want the test script to manage its own test data, so that tests are repeatable and don't pollute production data.

#### Acceptance Criteria

1. THE Test_Script SHALL create necessary test data before tests that require it

2. THE Test_Script SHALL clean up test data after tests complete

3. THE Test_Script SHALL use identifiable prefixes for test data (e.g., "TEST_" prefix)

4. IF cleanup fails, THEN THE Test_Script SHALL log a warning but not fail the overall test run

### Requirement 6: Command Line Interface

**User Story:** As a developer, I want to run tests from the command line with options, so that I can integrate testing into my workflow.

#### Acceptance Criteria

1. THE Test_Script SHALL accept the following command line arguments:
   - `--url`: Backend URL (default: http://localhost:8000)
   - `--timeout`: Request timeout in seconds (default: 10)
   - `--output`: Output file path for report (optional)
   - `--page`: Run tests for specific page only (optional)
   - `--verbose`: Show detailed output during execution

2. WHEN `--page` is specified, THE Test_Script SHALL only run tests for that page group

3. THE Test_Script SHALL display progress during execution when `--verbose` is enabled

### Requirement 7: Dependency Handling

**User Story:** As a developer, I want tests to handle dependencies correctly, so that dependent tests don't fail due to missing prerequisites.

#### Acceptance Criteria

1. WHEN a test depends on data created by a previous test, THE Test_Script SHALL execute tests in correct order

2. IF a prerequisite test fails, THEN THE Test_Script SHALL skip dependent tests and mark them as skipped

3. THE Test_Script SHALL report skipped tests separately from passed and failed tests
