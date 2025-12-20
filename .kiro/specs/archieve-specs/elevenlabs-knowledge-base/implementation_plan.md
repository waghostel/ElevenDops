# Implementation Plan - ElevenLabs Knowledge Base Integration (Spec 4)

## Overview

Enable real synchronization between Firestore knowledge documents and ElevenLabs Knowledge Base API with robust error handling, retry logic, and accurate status tracking.

## Prerequisites

- ✅ Spec 2: Firestore Data Service (Completed)
- ✅ ElevenLabs API key configured in `.env`
- ✅ Firestore emulator running (for local development)

## Implementation Steps

### Step 1: Add Dependencies

```bash
poetry add tenacity
```

Add to `pyproject.toml`:
```toml
tenacity = "^8.2.0"
```

### Step 2: Enhance ElevenLabsService

#### 2.1 Add Error Classification

```python
# backend/services/elevenlabs_service.py

from enum import Enum
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

class ElevenLabsErrorType(Enum):
    RATE_LIMIT = "rate_limit"
    AUTH_ERROR = "auth_error"
    VALIDATION = "validation"
    SERVER_ERROR = "server_error"
    NETWORK = "network"
    UNKNOWN = "unknown"

class ElevenLabsSyncError(ElevenLabsServiceError):
    def __init__(
        self, 
        message: str, 
        error_type: ElevenLabsErrorType = ElevenLabsErrorType.UNKNOWN,
        original_error: Exception = None,
        is_retryable: bool = False
    ):
        super().__init__(message)
        self.error_type = error_type
        self.original_error = original_error
        self.is_retryable = is_retryable
```

#### 2.2 Add Error Classification Helper

```python
def _classify_error(self, error: Exception) -> tuple[ElevenLabsErrorType, bool]:
    """Classify error and determine if retryable."""
    error_str = str(error).lower()
    
    # Check for rate limiting
    if "429" in error_str or "rate" in error_str:
        return ElevenLabsErrorType.RATE_LIMIT, True
    
    # Check for auth errors
    if "401" in error_str or "403" in error_str or "unauthorized" in error_str:
        return ElevenLabsErrorType.AUTH_ERROR, False
    
    # Check for validation errors
    if "400" in error_str or "invalid" in error_str:
        return ElevenLabsErrorType.VALIDATION, False
    
    # Check for server errors
    if any(code in error_str for code in ["500", "502", "503", "504"]):
        return ElevenLabsErrorType.SERVER_ERROR, True
    
    # Check for network errors
    if any(term in error_str for term in ["connection", "timeout", "network"]):
        return ElevenLabsErrorType.NETWORK, True
    
    return ElevenLabsErrorType.UNKNOWN, False
```

#### 2.3 Add Retry Decorator

```python
def _should_retry(exception: Exception) -> bool:
    """Determine if exception should trigger retry."""
    if isinstance(exception, ElevenLabsSyncError):
        return exception.is_retryable
    return False

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception(_should_retry),
    before_sleep=lambda retry_state: logging.info(
        f"Retrying ElevenLabs API call, attempt {retry_state.attempt_number}"
    )
)
def create_document(self, text: str, name: str) -> str:
    """Create document with retry logic."""
    # Implementation with enhanced error handling
```

### Step 3: Update Schemas

```python
# backend/models/schemas.py

class KnowledgeDocumentResponse(BaseModel):
    # ... existing fields ...
    sync_error_message: Optional[str] = Field(
        None, description="Error message if sync failed"
    )
    last_sync_attempt: Optional[datetime] = Field(
        None, description="Timestamp of last sync attempt"
    )
    sync_retry_count: int = Field(
        default=0, description="Number of sync retry attempts"
    )
```

### Step 4: Update Data Service Interface

```python
# backend/services/data_service.py

@abstractmethod
async def update_knowledge_sync_status(
    self, 
    knowledge_id: str, 
    status: SyncStatus, 
    elevenlabs_id: Optional[str] = None,
    error_message: Optional[str] = None
) -> bool:
    """Update sync status with optional error message."""
    pass
```

### Step 5: Update Background Task

```python
# backend/api/routes/knowledge.py

async def sync_knowledge_to_elevenlabs(
    knowledge_id: str,
    content: str,
    name: str,
    data_service: DataServiceInterface,
    elevenlabs_service: ElevenLabsService,
):
    """Background task with enhanced error handling."""
    try:
        await data_service.update_knowledge_sync_status(
            knowledge_id, SyncStatus.SYNCING
        )
        
        elevenlabs_id = elevenlabs_service.create_document(
            text=content, name=name
        )
        
        await data_service.update_knowledge_sync_status(
            knowledge_id, SyncStatus.COMPLETED, elevenlabs_id
        )
        logging.info(f"Successfully synced document {knowledge_id}")
        
    except ElevenLabsSyncError as e:
        logging.error(f"Sync failed for {knowledge_id}: {e}")
        await data_service.update_knowledge_sync_status(
            knowledge_id, 
            SyncStatus.FAILED,
            error_message=str(e)
        )
    except Exception as e:
        logging.error(f"Unexpected error syncing {knowledge_id}: {e}")
        await data_service.update_knowledge_sync_status(
            knowledge_id,
            SyncStatus.FAILED,
            error_message=f"Unexpected error: {str(e)}"
        )
```

### Step 6: Update Frontend Status Display

```python
# streamlit_app/pages/2_Upload_Knowledge.py

STATUS_COLORS = {
    "pending": "orange",
    "syncing": "blue",
    "completed": "green",
    "failed": "red"
}

for doc in documents:
    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
    
    with col2:
        status = doc.sync_status
        color = STATUS_COLORS.get(status, "gray")
        st.markdown(f":{color}[{status}]")
        
        # Show error details for failed syncs
        if status == "failed" and hasattr(doc, 'sync_error_message') and doc.sync_error_message:
            with st.expander("Error Details"):
                st.error(doc.sync_error_message)
```

## Verification Plan

### Automated Tests

1. **Unit Tests** (`tests/test_elevenlabs_service_props.py`):
   - Test error classification logic
   - Test retry behavior with mocked client
   - Test successful/failed document creation

2. **Run Tests**:
   ```bash
   pytest tests/test_elevenlabs_service_props.py -v
   ```

### Manual Verification

1. **Start Services**:
   ```bash
   # Terminal 1: Firestore Emulator
   firebase emulators:start --only firestore
   
   # Terminal 2: Backend
   poetry run uvicorn backend.main:app --reload
   
   # Terminal 3: Frontend
   poetry run streamlit run streamlit_app/app.py
   ```

2. **Test Scenarios**:

   | Scenario | Expected Result |
   |----------|-----------------|
   | Upload with valid API key | Status: pending → syncing → completed |
   | Upload with invalid API key | Status: pending → syncing → failed + error message |
   | Click "Retry Sync" on failed | Status: pending → syncing → completed/failed |
   | Check Firestore data | elevenlabs_document_id populated on success |

3. **Error Simulation**:
   - Temporarily set invalid `ELEVENLABS_API_KEY`
   - Upload document → verify "failed" status with error message
   - Fix API key → click "Retry Sync" → verify "completed"

## Rollback Plan

If issues arise:
1. Revert changes to `elevenlabs_service.py`
2. Remove new schema fields (backward compatible)
3. Keep existing sync logic as fallback

## Success Criteria

- [ ] Documents sync to ElevenLabs with automatic retry on transient errors
- [ ] Sync status accurately reflects current state (pending/syncing/completed/failed)
- [ ] Error messages stored and displayed for failed syncs
- [ ] Manual retry works for failed documents
- [ ] All existing tests pass
- [ ] New tests cover error handling and retry logic
- [ ] No regression in existing functionality
