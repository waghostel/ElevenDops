# Implementation Plan: Page-Based API Testing Script

## Overview

This plan implements a Python testing script that validates all backend API endpoints organized by Streamlit page. The script will be located at `scripts/test_apis_by_page.py` and can be run from the command line.

## Tasks

- [ ] 1. Set up project structure and core data classes
  - Create `scripts/test_apis_by_page.py` with imports and data classes
  - Implement TestStatus enum, TestResult, PageTestResults, TestReport, TestContext dataclasses
  - Include computed properties for counts and pass rate
  - _Requirements: 3.1, 3.2, 4.1, 4.4_

- [ ] 2. Implement TestDataManager
  - [ ] 2.1 Create TestDataManager class with setup/teardown
    - Implement async HTTP client management
    - Define TEST_PREFIX constant
    - _Requirements: 5.3_
  
  - [ ] 2.2 Implement test data creation methods
    - `create_knowledge_document()` - creates test knowledge doc
    - `create_agent(knowledge_id)` - creates test agent
    - Track created resources in context
    - _Requirements: 5.1, 5.3_
  
  - [ ] 2.3 Implement cleanup method
    - Delete all tracked resources (agents, knowledge docs)
    - Handle cleanup errors gracefully (log warning, don't fail)
    - _Requirements: 5.2, 5.4_

- [ ] 3. Implement BasePageTests and request helper
  - [ ] 3.1 Create BasePageTests abstract base class
    - Define abstract `page_name` property and `run_tests()` method
    - Implement `_make_request()` helper with timing and error handling
    - Handle connection errors, timeouts, HTTP errors
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [ ] 3.2 Write property test for connection error handling
    - **Property 4: Connection Error Graceful Handling**
    - **Validates: Requirements 3.3**

- [ ] 4. Implement page test classes
  - [ ] 4.1 Implement HealthTests
    - Test GET /api/health
    - Test GET /api/health/ready
    - _Requirements: 2.1_
  
  - [ ] 4.2 Implement DashboardTests
    - Test GET /api/dashboard/stats
    - _Requirements: 2.2_
  
  - [ ] 4.3 Implement KnowledgeTests
    - Test POST /api/knowledge (create)
    - Test GET /api/knowledge (list)
    - Test GET /api/knowledge/{id}
    - Test POST /api/knowledge/{id}/retry-sync
    - Handle dependency: skip if create fails
    - _Requirements: 2.3, 7.1, 7.2_
  
  - [ ] 4.4 Implement AudioTests
    - Test GET /api/audio/voices/list
    - Test POST /api/audio/generate-script
    - Test GET /api/audio/{knowledge_id}
    - Handle dependency: need knowledge_id
    - _Requirements: 2.4, 7.1, 7.2_
  
  - [ ] 4.5 Implement AgentTests
    - Test POST /api/agent (create)
    - Test GET /api/agent (list)
    - Handle dependency: need knowledge_id
    - _Requirements: 2.5, 7.1, 7.2_
  
  - [ ] 4.6 Implement PatientTests
    - Test POST /api/patient/session
    - Test POST /api/patient/session/{id}/message
    - Test POST /api/patient/session/{id}/end
    - Handle dependency: need agent_id
    - _Requirements: 2.6, 7.1, 7.2_
  
  - [ ] 4.7 Implement ConversationTests
    - Test GET /api/conversations
    - Test GET /api/conversations/statistics
    - Test GET /api/conversations/{id}
    - _Requirements: 2.7_

- [ ] 5. Checkpoint - Verify page tests work individually
  - Ensure all page test classes can be instantiated
  - Verify _make_request returns proper TestResult objects
  - Ask the user if questions arise

- [ ] 6. Implement TestRunner
  - [ ] 6.1 Create TestRunner class
    - Define PAGE_ORDER constant
    - Map page names to test classes
    - Implement `run()` method with page iteration
    - _Requirements: 1.1, 1.2, 1.3_
  
  - [ ] 6.2 Add page filter support
    - Filter pages when --page argument provided
    - Only run tests for specified page
    - _Requirements: 6.2_
  
  - [ ] 6.3 Add verbose output during execution
    - Print page headers when verbose
    - Print test results with status icons
    - _Requirements: 6.3_
  
  - [ ] 6.4 Write property test for execution order
    - **Property 2: Test Execution Order Preservation**
    - **Validates: Requirements 1.2**
  
  - [ ] 6.5 Write property test for page filter isolation
    - **Property 8: Page Filter Isolation**
    - **Validates: Requirements 6.2**

- [ ] 7. Implement ReportGenerator
  - [ ] 7.1 Implement console output
    - Print summary with totals and pass rate
    - Print per-page breakdown
    - Highlight failed tests with error details
    - _Requirements: 4.1, 4.2, 4.3, 4.5_
  
  - [ ] 7.2 Implement Markdown export
    - Generate Markdown table format
    - Include summary table
    - Include per-page sections with result tables
    - _Requirements: 4.5, 4.6_
  
  - [ ] 7.3 Write property test for report structure
    - **Property 5: TestReport Structure Completeness**
    - **Validates: Requirements 4.1, 4.2, 4.4**
  
  - [ ] 7.4 Write property test for failed test visibility
    - **Property 6: Failed Test Error Visibility**
    - **Validates: Requirements 4.3**

- [ ] 8. Implement CLI interface
  - [ ] 8.1 Create argument parser
    - Add --url argument (default: http://localhost:8000)
    - Add --timeout argument (default: 10)
    - Add --output argument (optional file path)
    - Add --page argument (optional page filter)
    - Add --verbose flag
    - _Requirements: 6.1_
  
  - [ ] 8.2 Implement main() function
    - Parse arguments
    - Create TestContext
    - Run TestRunner
    - Generate report (console and/or file)
    - _Requirements: 6.1, 6.3_

- [ ] 9. Checkpoint - Full integration test
  - Run script against local backend
  - Verify report output is correct
  - Test --page filter works
  - Test --output generates Markdown file
  - Ask the user if questions arise

- [ ] 10. Write remaining property tests
  - [ ] 10.1 Write property test for API mapping completeness
    - **Property 1: API-to-Page Mapping Completeness**
    - **Validates: Requirements 1.1, 1.3, 2.1-2.7**
  
  - [ ] 10.2 Write property test for TestResult field completeness
    - **Property 3: TestResult Field Completeness**
    - **Validates: Requirements 3.1, 3.2**
  
  - [ ] 10.3 Write property test for test data prefix
    - **Property 7: Test Data Prefix Consistency**
    - **Validates: Requirements 5.1, 5.3**
  
  - [ ] 10.4 Write property test for dependency skip propagation
    - **Property 9: Dependency Skip Propagation**
    - **Validates: Requirements 7.1, 7.2**
  
  - [ ] 10.5 Write property test for skipped test reporting
    - **Property 10: Skipped Test Distinct Reporting**
    - **Validates: Requirements 7.3**

- [ ] 11. Final checkpoint - All tests pass
  - Run all property tests
  - Run script against backend
  - Verify cleanup works correctly
  - Ensure all tests pass, ask the user if questions arise

## Notes

- All tasks are required including property tests
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- The script uses httpx for async HTTP requests
- Test data uses "TEST_API_" prefix for easy identification and cleanup
