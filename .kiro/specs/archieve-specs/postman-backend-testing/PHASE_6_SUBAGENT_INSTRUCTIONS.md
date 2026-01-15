# Phase 6: Sub-Agent Execution Instructions

**Status**: Ready for Parallel Execution
**Date**: January 15, 2026
**Total Sub-Agents**: 9 (one per task)

---

## General Instructions for All Sub-Agents

### Before Starting

1. Read this entire document
2. Read the task-specific section for your assigned task
3. Review the dependency graph (no dependencies for Phase 6)
4. Verify Phase 5 checkpoint passed
5. Load existing components from Phase 4

### During Execution

1. Create test requests for your API endpoints
2. Generate test scripts using TestScriptGenerator
3. Generate test data using TestDataGenerator
4. Write comprehensive unit tests
5. Write property-based tests (100+ iterations)
6. Document any improvements in needImprovement.md
7. Add requests to CollectionBuilder
8. Run tests to verify all pass

### After Completion

1. Verify all tests pass (100%)
2. Verify no warnings or errors
3. Verify property tests complete 100+ iterations
4. Document improvements found
5. Report completion status to main agent

---

## Shared Resources

### Available Components (from Phase 4)

**EnvironmentManager** (`backend/services/environment_manager.py`)
- Create and manage Postman environments
- Set/get/delete variables
- Validate required variables
- Build environment JSON

**TestScriptGenerator** (`backend/services/test_script_generator.py`)
- Generate JavaScript test scripts
- Status code assertions
- Schema validation
- Field checks
- Value assertions
- Variable saving

**TestDataGenerator** (`backend/services/test_data_generator.py`)
- Generate realistic test data
- Knowledge documents
- Audio requests
- Agent configurations
- Patient sessions
- Templates
- Conversations

**CollectionBuilder** (`backend/services/collection_builder.py`)
- Build Postman collections
- Create folders
- Add requests
- Attach test scripts
- Attach pre-request scripts
- Generate collection JSON

### Test Utilities

**File**: `tests/postman_test_helpers.py`
- HTTP client utilities
- Test data helpers
- Assertion utilities
- Mock utilities

---

## Task-Specific Instructions

### Task 11: Health & Infrastructure Tests

**Assigned Sub-Agent**: Agent 1

**Endpoints to Test**:
- GET / (root endpoint)
- GET /api/health
- GET /api/health/ready
- GET /api/dashboard/stats

**Requirements**: 2.1, 2.2, 2.3, 2.4, 2.5

**Property Tests**:
- Property 4: Universal Response Schema Validation

**Steps**:
1. Create test requests for each endpoint
2. Generate test scripts for response validation
3. Generate test data for requests
4. Write unit tests for each endpoint
5. Write property test for schema validation
6. Run all tests (verify 100% pass)
7. Document improvements

**Output Files**:
- `tests/postman/task_11_test.py`
- Collection requests (added to CollectionBuilder)

---

### Task 12: Knowledge API Tests

**Assigned Sub-Agent**: Agent 2

**Endpoints to Test**:
- POST /api/knowledge (create)
- GET /api/knowledge (list)
- GET /api/knowledge/{knowledge_id} (read)
- PUT /api/knowledge/{knowledge_id} (update)
- DELETE /api/knowledge/{knowledge_id} (delete)
- POST /api/knowledge/{knowledge_id}/retry-sync

**Requirements**: 3.1-3.8, 4.7-4.8, 5.3-5.4, 8.3-8.5, 9.5

**Property Tests**:
- Property 5: CRUD Round-Trip Consistency
- Property 6: Update Persistence
- Property 7: Deletion Verification
- Property 8: Structured Content Parsing
- Property 9: ElevenLabs Naming Convention

**Steps**:
1. Create test requests for each endpoint
2. Generate test scripts for CRUD operations
3. Generate test data for knowledge documents
4. Write unit tests for each endpoint
5. Write 5 property tests
6. Run all tests (verify 100% pass)
7. Document improvements

**Output Files**:
- `tests/postman/task_12_test.py`
- Collection requests (added to CollectionBuilder)

---

### Task 13: Audio API Tests

**Assigned Sub-Agent**: Agent 3

**Endpoints to Test**:
- GET /api/audio/voices/list
- POST /api/audio/generate-script
- POST /api/audio/generate-script-stream
- POST /api/audio/generate
- GET /api/audio/list (with filters)
- GET /api/audio/stream/{audio_id}
- PUT /api/audio/{audio_id}
- DELETE /api/audio/{audio_id}

**Requirements**: 4.1-4.9, 5.7, 7.1, 7.4, 11.4

**Property Tests**:
- Property 10: Script Generation from Knowledge
- Property 11: SSE Streaming Format
- Property 12: Audio Generation from Script
- Property 13: Universal Filtering Behavior
- Property 14: Rate Limiting Enforcement

**Steps**:
1. Create test requests for each endpoint
2. Generate test scripts for audio operations
3. Generate test data for audio requests
4. Write unit tests for each endpoint
5. Write 5 property tests
6. Run all tests (verify 100% pass)
7. Document improvements

**Output Files**:
- `tests/postman/task_13_test.py`
- Collection requests (added to CollectionBuilder)

---

### Task 14: Agent API Tests

**Assigned Sub-Agent**: Agent 4

**Endpoints to Test**:
- POST /api/agent (create)
- GET /api/agent (list)
- PUT /api/agent/{agent_id} (update)
- DELETE /api/agent/{agent_id} (delete)
- GET /api/agent/system-prompts

**Requirements**: 5.1-5.6

**Property Tests**:
- Property 15: Agent-Knowledge Relationship Integrity

**Steps**:
1. Create test requests for each endpoint
2. Generate test scripts for agent operations
3. Generate test data for agent configurations
4. Write unit tests for each endpoint
5. Write 1 property test
6. Run all tests (verify 100% pass)
7. Document improvements

**Output Files**:
- `tests/postman/task_14_test.py`
- Collection requests (added to CollectionBuilder)

---

### Task 15: Patient API Tests

**Assigned Sub-Agent**: Agent 5

**Endpoints to Test**:
- POST /api/patient/session (create session)
- POST /api/patient/session/{session_id}/message (send message)
- POST /api/patient/session/{session_id}/end (end session)

**Requirements**: 6.1-6.5, 7.3

**Property Tests**:
- Property 16: Session ID Continuity
- Property 17: Chat Mode Parameter Effect
- Property 18: Conversation Retrieval After Session End

**Steps**:
1. Create test requests for each endpoint
2. Generate test scripts for patient operations
3. Generate test data for patient sessions
4. Write unit tests for each endpoint
5. Write 3 property tests
6. Run all tests (verify 100% pass)
7. Document improvements

**Output Files**:
- `tests/postman/task_15_test.py`
- Collection requests (added to CollectionBuilder)

---

### Task 16: Conversations API Tests

**Assigned Sub-Agent**: Agent 6

**Endpoints to Test**:
- GET /api/conversations (list with filters)
- GET /api/conversations/statistics
- GET /api/conversations/{conversation_id}

**Requirements**: 7.1-7.5

**Property Tests**:
- Property 19: Conversation Analysis Inclusion

**Steps**:
1. Create test requests for each endpoint
2. Generate test scripts for conversation operations
3. Generate test data for conversations
4. Write unit tests for each endpoint
5. Write 1 property test
6. Run all tests (verify 100% pass)
7. Document improvements

**Output Files**:
- `tests/postman/task_16_test.py`
- Collection requests (added to CollectionBuilder)

---

### Task 17: Templates API Tests

**Assigned Sub-Agent**: Agent 7

**Endpoints to Test**:
- GET /api/templates (list)
- POST /api/templates (create)
- GET /api/templates/{template_id} (read)
- PUT /api/templates/{template_id} (update)
- DELETE /api/templates/{template_id} (delete)
- GET /api/templates/system-prompt
- POST /api/templates/preview

**Requirements**: 8.1-8.7

**Property Tests**:
- Property 20: Template Preview Accuracy

**Steps**:
1. Create test requests for each endpoint
2. Generate test scripts for template operations
3. Generate test data for templates
4. Write unit tests for each endpoint
5. Write 1 property test
6. Run all tests (verify 100% pass)
7. Document improvements

**Output Files**:
- `tests/postman/task_17_test.py`
- Collection requests (added to CollectionBuilder)

---

### Task 18: Debug API Tests

**Assigned Sub-Agent**: Agent 8

**Endpoints to Test**:
- GET /api/debug/health
- POST /api/debug/script-generation
- GET /api/debug/sessions
- POST /api/debug/sessions
- GET /api/debug/sessions/{session_id}
- POST /api/debug/sessions/{session_id}/end

**Requirements**: 9.1-9.7

**Property Tests**:
- Property 21: Debug Trace Completeness
- Property 22: Debug Session State Transitions

**Steps**:
1. Create test requests for each endpoint
2. Generate test scripts for debug operations
3. Generate test data for debug sessions
4. Write unit tests for each endpoint
5. Write 2 property tests
6. Run all tests (verify 100% pass)
7. Document improvements

**Output Files**:
- `tests/postman/task_18_test.py`
- Collection requests (added to CollectionBuilder)

---

### Task 19: Error Handling Tests

**Assigned Sub-Agent**: Agent 9

**Error Scenarios to Test**:
- Invalid ID tests (404)
- Malformed body tests (400)
- Missing field tests (422)
- Rate limiting tests (429)
- Service failure tests (502)

**Requirements**: 11.1-11.7

**Property Tests**:
- Property 28: Invalid ID Error Handling
- Property 29: Malformed Request Error Handling
- Property 30: Missing Field Validation
- Property 31: Error Message Descriptiveness
- Property 32: Error Response Schema Consistency

**Steps**:
1. Create test requests for error scenarios
2. Generate test scripts for error validation
3. Generate test data for error cases
4. Write unit tests for each error scenario
5. Write 5 property tests
6. Run all tests (verify 100% pass)
7. Document improvements

**Output Files**:
- `tests/postman/task_19_test.py`
- Collection requests (added to CollectionBuilder)

---

## Common Patterns

### Creating Test Requests

```python
# Example: Create a test request
request = {
    "name": "Create Knowledge Document",
    "request": {
        "method": "POST",
        "header": [
            {"key": "Content-Type", "value": "application/json"}
        ],
        "body": {
            "mode": "raw",
            "raw": json.dumps(test_data)
        },
        "url": {
            "raw": "{{base_url}}/api/knowledge",
            "protocol": "http",
            "host": ["{{base_url}}"],
            "path": ["api", "knowledge"]
        }
    },
    "tests": test_script
}
```

### Generating Test Scripts

```python
# Example: Generate test script
script = test_script_generator.generate_status_check(200)
script += test_script_generator.generate_schema_validation(
    {"id": "string", "title": "string"}
)
script += test_script_generator.generate_variable_save("knowledge_id", "$.id")
```

### Writing Property Tests

```python
# Example: Property test
@given(knowledge_data=st.fixed_dictionaries({
    "title": st.text(min_size=1),
    "content": st.text(min_size=10)
}))
def test_knowledge_crud_roundtrip(knowledge_data):
    # Create
    created = create_knowledge(knowledge_data)
    assert created["title"] == knowledge_data["title"]
    
    # Read
    retrieved = get_knowledge(created["id"])
    assert retrieved["title"] == knowledge_data["title"]
    
    # Delete
    delete_knowledge(created["id"])
    with pytest.raises(NotFound):
        get_knowledge(created["id"])
```

---

## Improvement Documentation

When you find improvements, document them in:

**File**: `.kiro/specs/postman-backend-testing/needImprovement.md`

**Format**:
```markdown
### [Task Number]: [Component Name]

**Category**: [Performance/Code Quality/Robustness/Observability/Concurrency/Security/Testing]
**Severity**: [Very Low/Low/Medium/High]
**Location**: [File path]

**Issue**: [Description of the issue]

**Suggested Improvement**: [What could be improved]

**Impact**: [What would improve]
```

**Do NOT fix improvements** - just document them for future optimization.

---

## Success Criteria

For each sub-agent to complete successfully:

✅ All test requests created
✅ All test scripts generated
✅ All unit tests written and passing
✅ All property tests written and passing (100+ iterations)
✅ All tests pass (100% pass rate)
✅ No warnings or errors
✅ Improvements documented
✅ Requirements traceability verified

---

## Troubleshooting

### If Tests Fail

1. Check test data generation
2. Verify API endpoints are correct
3. Check test script syntax
4. Verify property test generators
5. Check error handling

### If Property Tests Fail

1. Review the failing example
2. Check if it's a test issue or code issue
3. Adjust test or code accordingly
4. Re-run with 100+ iterations

### If You Get Stuck

1. Review the task-specific section
2. Check the shared resources
3. Review existing test patterns
4. Ask main agent for help

---

## Completion Checklist

- [ ] Read all instructions
- [ ] Understand your assigned task
- [ ] Review existing components
- [ ] Create test requests
- [ ] Generate test scripts
- [ ] Generate test data
- [ ] Write unit tests
- [ ] Write property tests
- [ ] Run all tests (100% pass)
- [ ] Document improvements
- [ ] Report completion

---

**Document Status**: Ready for Sub-Agent Execution
**Last Updated**: January 15, 2026
**Prepared By**: Kiro Agent

