# Design Document: Dashboard Real Statistics

## Overview

This design document describes the implementation for connecting the Doctor Dashboard to real Firestore statistics. The feature replaces mock data with actual counts from Firestore collections and calculates the most recent activity timestamp across all data collections.

The implementation leverages the existing `FirestoreDataService` which already has a `get_dashboard_stats()` method. The primary work involves ensuring the dashboard API uses the Firestore service when configured, and enhancing the last activity calculation to consider all relevant collections.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           1_Doctor_Dashboard.py                          │   │
│  │  - Calls BackendAPIClient.get_dashboard_stats()         │   │
│  │  - Renders metric cards (documents, agents, audio, time)│   │
│  │  - Handles errors with retry button                      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP GET /api/dashboard/stats
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           backend/api/dashboard.py                       │   │
│  │  - GET /api/dashboard/stats endpoint                     │   │
│  │  - Injects DataServiceInterface via Depends()            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           backend/services/data_service.py               │   │
│  │  - get_data_service() factory function                   │   │
│  │  - Returns FirestoreDataService or MockDataService       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │     backend/services/firestore_data_service.py           │   │
│  │  - get_dashboard_stats() implementation                  │   │
│  │  - Aggregation queries for counts                        │   │
│  │  - Last activity calculation across collections          │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Firestore Database                           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ knowledge_   │ │   agents     │ │ audio_files  │            │
│  │ documents    │ │              │ │              │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│  ┌──────────────┐                                               │
│  │conversations │                                               │
│  └──────────────┘                                               │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Dashboard API Endpoint

**File**: `backend/api/dashboard.py`

The existing endpoint already uses dependency injection for the data service. No changes needed to the endpoint itself - it will automatically use `FirestoreDataService` when configured.

```python
@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    data_service: DataServiceInterface = Depends(get_data_service),
) -> DashboardStatsResponse:
    return await data_service.get_dashboard_stats()
```

### 2. FirestoreDataService.get_dashboard_stats()

**File**: `backend/services/firestore_data_service.py`

The existing implementation needs enhancement to:
1. Query counts from all four collections using aggregation queries
2. Calculate last_activity by finding the maximum created_at across all collections

```python
async def get_dashboard_stats(self) -> DashboardStatsResponse:
    """Get dashboard statistics using collection counts."""
    try:
        # Use aggregation queries for counts
        doc_count = self._db.collection(KNOWLEDGE_DOCUMENTS).count().get()[0][0].value
        agent_count = self._db.collection(AGENTS).count().get()[0][0].value
        audio_count = self._db.collection(AUDIO_FILES).count().get()[0][0].value
        
        # Calculate last_activity across all collections
        last_activity = await self._get_last_activity_timestamp()
        
        return DashboardStatsResponse(
            document_count=doc_count,
            agent_count=agent_count,
            audio_count=audio_count,
            last_activity=last_activity,
        )
    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {e}")
        # Fallback to zero counts
        return DashboardStatsResponse(
            document_count=0,
            agent_count=0,
            audio_count=0,
            last_activity=datetime.now(),
        )
```

### 3. Last Activity Calculation

**File**: `backend/services/firestore_data_service.py`

New helper method to find the most recent timestamp across all collections:

```python
async def _get_last_activity_timestamp(self) -> datetime:
    """Get the most recent created_at timestamp across all collections."""
    collections = [KNOWLEDGE_DOCUMENTS, AGENTS, AUDIO_FILES, CONVERSATIONS]
    latest = datetime.now()
    found_any = False
    
    for collection_name in collections:
        docs = (
            self._db.collection(collection_name)
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(1)
            .stream()
        )
        for doc in docs:
            timestamp = doc.to_dict().get("created_at")
            if timestamp:
                found_any = True
                if not found_any or timestamp > latest:
                    latest = timestamp
    
    return latest if found_any else datetime.now()
```

### 4. Frontend Dashboard Page

**File**: `streamlit_app/pages/1_Doctor_Dashboard.py`

The existing implementation already:
- Calls `BackendAPIClient.get_dashboard_stats()`
- Renders metric cards with counts
- Formats last_activity as relative time
- Handles errors with retry button

No changes needed - the frontend will automatically display real data once the backend is configured to use Firestore.

## Data Models

### DashboardStatsResponse

**File**: `backend/models/schemas.py`

```python
class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response."""
    document_count: int
    agent_count: int
    audio_count: int
    last_activity: datetime
```

### Firestore Collections Schema

| Collection | Count Field | Timestamp Field |
|------------|-------------|-----------------|
| knowledge_documents | (count aggregation) | created_at |
| agents | (count aggregation) | created_at |
| audio_files | (count aggregation) | created_at |
| conversations | (count aggregation) | created_at |

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Dashboard counts match collection sizes

*For any* state of the Firestore database, the dashboard statistics SHALL return counts that exactly match the number of documents in each respective collection (knowledge_documents, agents, audio_files).

**Validates: Requirements 1.1, 2.1, 3.1**

### Property 2: Count increases after creation

*For any* entity type (document, agent, or audio file), creating a new entity SHALL increase the corresponding dashboard count by exactly 1.

**Validates: Requirements 1.2, 2.2, 3.2**

### Property 3: Count decreases after deletion

*For any* entity type (document, agent, or audio file), deleting an existing entity SHALL decrease the corresponding dashboard count by exactly 1.

**Validates: Requirements 1.3, 2.3, 3.3**

### Property 4: Last activity is maximum timestamp

*For any* set of entities across all collections, the last_activity timestamp SHALL equal the maximum created_at timestamp among all entities, or the current time if no entities exist.

**Validates: Requirements 4.1, 4.2, 4.3**

### Property 5: Error fallback returns valid response

*For any* Firestore query failure, the dashboard statistics SHALL return a valid response with zero counts and current timestamp.

**Validates: Requirements 5.1**

## Error Handling

### Backend Error Handling

1. **Firestore Query Failures**
   - Catch all exceptions in `get_dashboard_stats()`
   - Log error with full exception details
   - Return fallback response: `{document_count: 0, agent_count: 0, audio_count: 0, last_activity: now()}`

2. **Individual Collection Failures**
   - If one collection query fails, continue with others
   - Use 0 as fallback for failed collection count
   - Log which collection failed

### Frontend Error Handling

1. **API Connection Errors**
   - Display "Cannot connect to backend" message
   - Show retry button

2. **API Timeout Errors**
   - Display "Request timed out" message
   - Show retry button

3. **API Response Errors**
   - Display "API Error" with message
   - Show retry button

## Testing Strategy

### Property-Based Testing

The implementation will use **Hypothesis** for property-based testing, as it's already configured in the project.

Each property test will:
1. Generate random test data using Hypothesis strategies
2. Set up the test state in Firestore (or mock)
3. Call the dashboard stats endpoint
4. Verify the property holds

**Test Configuration**:
- Minimum 100 iterations per property test
- Use `@settings(max_examples=100)` decorator

**Test File**: `tests/properties/test_dashboard_stats_props.py`

### Unit Tests

Unit tests will cover:
1. `_get_last_activity_timestamp()` helper method
2. Error handling paths
3. Fallback behavior

**Test File**: `tests/test_dashboard_stats_unit.py`

### Integration Tests

Integration tests will verify:
1. End-to-end flow from frontend to Firestore
2. Refresh button functionality
3. Error message display

**Test File**: `tests/test_dashboard_integration.py`

### Test Annotations

Each property-based test MUST include a comment referencing the correctness property:
```python
# **Feature: dashboard-real-statistics, Property 1: Dashboard counts match collection sizes**
```
