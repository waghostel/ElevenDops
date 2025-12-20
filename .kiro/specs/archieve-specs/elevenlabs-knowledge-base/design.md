# Design - ElevenLabs Knowledge Base Integration (Spec 4)

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Streamlit     │────▶│   FastAPI        │────▶│   ElevenLabs    │
│   Frontend      │     │   Backend        │     │   API           │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │   Firestore      │
                        │   (Source of     │
                        │    Truth)        │
                        └──────────────────┘
```

## Data Flow

### Upload & Sync Flow
```
1. User uploads document via Streamlit
2. Backend creates document in Firestore (status: pending)
3. Background task starts sync to ElevenLabs (status: syncing)
4. On success: Update status to completed, store elevenlabs_document_id
5. On failure: Update status to failed, store error_message
6. Frontend polls/refreshes to show updated status
```

### Retry Flow
```
1. User clicks "Retry Sync" for failed document
2. Backend resets status to pending
3. Background task retries sync with exponential backoff
4. Same success/failure handling as initial sync
```

## Component Design

### 1. ElevenLabsService Enhancements

#### Error Classification
```python
class ElevenLabsErrorType(Enum):
    RATE_LIMIT = "rate_limit"      # 429 - Retry with backoff
    AUTH_ERROR = "auth_error"       # 401/403 - No retry
    VALIDATION = "validation"       # 400 - No retry
    SERVER_ERROR = "server_error"   # 5xx - Retry
    NETWORK = "network"             # Connection errors - Retry
    UNKNOWN = "unknown"             # Other - Log and fail
```

#### Retry Configuration
```python
RETRY_CONFIG = {
    "max_attempts": 3,
    "initial_delay": 1.0,  # seconds
    "max_delay": 10.0,     # seconds
    "exponential_base": 2,
    "retryable_errors": [
        ElevenLabsErrorType.RATE_LIMIT,
        ElevenLabsErrorType.SERVER_ERROR,
        ElevenLabsErrorType.NETWORK,
    ]
}
```

#### Enhanced Exception
```python
class ElevenLabsSyncError(ElevenLabsServiceError):
    def __init__(self, message: str, error_type: ElevenLabsErrorType, 
                 original_error: Exception = None, is_retryable: bool = False):
        super().__init__(message)
        self.error_type = error_type
        self.original_error = original_error
        self.is_retryable = is_retryable
```

### 2. Knowledge API Route Updates

#### Background Task Enhancement
```python
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
        
        # create_document now has internal retry logic
        elevenlabs_id = elevenlabs_service.create_document(
            text=content, name=name
        )
        
        await data_service.update_knowledge_sync_status(
            knowledge_id, SyncStatus.COMPLETED, elevenlabs_id
        )
        
    except ElevenLabsSyncError as e:
        logger.error(f"Sync failed for {knowledge_id}: {e.message}")
        await data_service.update_knowledge_sync_status(
            knowledge_id, 
            SyncStatus.FAILED,
            error_message=str(e.message)
        )
```

### 3. Schema Updates

#### Extended Sync Status Tracking
```python
# Add to KnowledgeDocumentResponse
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

### 4. Frontend Status Display

#### Status Color Mapping
```python
STATUS_COLORS = {
    "pending": "orange",
    "syncing": "blue", 
    "completed": "green",
    "failed": "red"
}
```

#### Status Display Component
```python
def display_sync_status(doc):
    status = doc.sync_status
    color = STATUS_COLORS.get(status, "gray")
    
    st.markdown(f":{color}[{status}]")
    
    if status == "failed" and doc.sync_error_message:
        with st.expander("Error Details"):
            st.error(doc.sync_error_message)
```

## API Contracts

### POST /api/knowledge
Request unchanged. Response includes sync status fields.

### POST /api/knowledge/{id}/retry-sync
Triggers retry for failed document. Returns updated document.

### GET /api/knowledge/{id}
Returns document with current sync status and error details.

## Error Handling Strategy

| Error Type | HTTP Status | Retry? | User Message |
|------------|-------------|--------|--------------|
| Rate Limit | 429 | Yes (backoff) | "Service busy, retrying..." |
| Auth Error | 401/403 | No | "API key invalid" |
| Validation | 400 | No | "Document format invalid" |
| Server Error | 5xx | Yes | "Service unavailable, retrying..." |
| Network | N/A | Yes | "Connection failed, retrying..." |

## Testing Strategy

### Unit Tests
- Mock ElevenLabs client responses
- Test error classification logic
- Test retry behavior with different error types

### Integration Tests
- Test full sync flow with Firestore emulator
- Test retry mechanism end-to-end

### Manual Tests
- Upload document and verify sync
- Simulate failures and verify retry
- Check status display in frontend
