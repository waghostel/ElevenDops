# Tasks - ElevenLabs Knowledge Base Integration (Spec 4)

## Phase 1: Backend Service Enhancement

### Task 1.1: Add Retry Library Dependency

- [x] Add `tenacity` to `pyproject.toml` dependencies
- [x] Run `poetry install` to install

### Task 1.2: Enhance ElevenLabsService Error Handling

- [x] Create `ElevenLabsErrorType` enum for error classification
- [x] Update `ElevenLabsSyncError` with error_type, is_retryable, original_error
- [x] Add `_classify_error()` helper method to categorize API errors
- [x] Update `create_document()` with detailed error handling and logging
- [x] Update `delete_document()` with detailed error handling and logging

### Task 1.3: Implement Retry Logic

- [x] Add `@retry` decorator from tenacity to `create_document()`
- [x] Configure exponential backoff: initial=1s, max=10s, attempts=3
- [x] Add `before_sleep` callback for logging retry attempts
- [x] Only retry on retryable error types (rate_limit, server_error, network)

### Task 1.4: Add Detailed Logging

- [x] Log API request details (document name, content length)
- [x] Log API response (document_id on success)
- [x] Log error details with stack trace on failure
- [x] Log retry attempts with delay information

## Phase 2: Schema & Data Service Updates

### Task 2.1: Update Pydantic Schemas

- [x] Add `sync_error_message: Optional[str]` to `KnowledgeDocumentResponse`
- [x] Add `last_sync_attempt: Optional[datetime]` to `KnowledgeDocumentResponse`
- [x] Add `sync_retry_count: int` to `KnowledgeDocumentResponse`

### Task 2.2: Update DataServiceInterface

- [x] Extend `update_knowledge_sync_status()` signature to accept `error_message`
- [x] Update `MockDataService` implementation
- [x] Update `FirestoreDataService` implementation

## Phase 3: API Route Updates

### Task 3.1: Enhance Background Sync Task

- [x] Update `sync_knowledge_to_elevenlabs()` to catch `ElevenLabsSyncError`
- [x] Pass error message to `update_knowledge_sync_status()` on failure
- [x] Update `last_sync_attempt` timestamp
- [x] Increment `sync_retry_count` on retry

### Task 3.2: Update Retry Endpoint

- [x] Reset `sync_retry_count` on manual retry (or increment)
- [x] Clear previous `sync_error_message` before retry
- [x] Log retry initiation

## Phase 4: Frontend Updates

### Task 4.1: Update Status Display

- [x] Add "syncing" status with blue color indicator
- [x] Show error details in expandable section for failed docs
- [x] Add loading spinner during sync operations

### Task 4.2: Enhance Retry Functionality

- [x] Show retry count if > 0
- [x] Disable retry button while syncing
- [x] Show success toast after successful retry

## Phase 5: Testing

### Task 5.1: Unit Tests for ElevenLabsService

- [x] Create `tests/test_elevenlabs_service_props.py`
- [x] Test `_classify_error()` with different error types
- [x] Test retry behavior with mocked client
- [x] Test successful document creation
- [x] Test permanent error handling (no retry)

### Task 5.2: Integration Tests

- [x] Test full sync flow with Firestore emulator
- [x] Test retry mechanism end-to-end
- [x] Test status transitions (pending → syncing → completed/failed)

### Task 5.3: Manual Verification

- [x] Upload document with valid API key → verify "completed"
- [x] Upload document with invalid API key → verify "failed" + error message
- [x] Click "Retry Sync" → verify status updates
- [x] Check Firestore emulator for correct data

## Acceptance Criteria

- [x] Documents sync to ElevenLabs with retry on transient errors
- [x] Sync status accurately reflects current state
- [x] Error messages are stored and displayed for failed syncs
- [x] Retry mechanism works for failed documents
- [x] All existing tests pass
- [x] New tests cover error handling and retry logic

## Files to Modify

| File                                         | Changes                     |
| -------------------------------------------- | --------------------------- |
| `pyproject.toml`                             | Add tenacity dependency     |
| `backend/services/elevenlabs_service.py`     | Error handling, retry logic |
| `backend/models/schemas.py`                  | Add sync error fields       |
| `backend/services/data_service.py`           | Update interface            |
| `backend/services/firestore_data_service.py` | Update implementation       |
| `backend/api/routes/knowledge.py`            | Enhanced background task    |
| `streamlit_app/pages/2_Upload_Knowledge.py`  | Status display updates      |

## Estimated Effort

| Phase                    | Effort                  |
| ------------------------ | ----------------------- |
| Phase 1: Backend Service | 4 hours                 |
| Phase 2: Schema Updates  | 1 hour                  |
| Phase 3: API Routes      | 1 hour                  |
| Phase 4: Frontend        | 1 hour                  |
| Phase 5: Testing         | 2 hours                 |
| **Total**                | **~9 hours (1-2 days)** |
