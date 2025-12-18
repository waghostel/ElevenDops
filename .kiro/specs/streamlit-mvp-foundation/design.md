# Design Document: ElevenDops Streamlit MVP Foundation

## Overview

This design document outlines the architecture and implementation details for the ElevenDops Streamlit MVP foundation. The system consists of a Streamlit frontend for rapid prototyping and a FastAPI backend that provides RESTful APIs. This architecture ensures clean separation of concerns and enables future migration to React/TypeScript Next.js while maintaining API compatibility.

The MVP foundation includes:
- Project structure with Poetry package management
- FastAPI backend with health check and dashboard statistics endpoints
- Streamlit main application (app.py) with branding and navigation
- Doctor Dashboard page (1_Doctor_Dashboard.py) with system metrics
- Backend API client service module for frontend-backend communication

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Cloud Run Container                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐    ┌─────────────────────────────────┐ │
│  │   Streamlit App     │    │        FastAPI Backend          │ │
│  │   (Port 8501)       │    │        (Port 8000)              │ │
│  │                     │    │                                 │ │
│  │  ┌───────────────┐  │    │  ┌───────────────────────────┐  │ │
│  │  │    app.py     │  │    │  │    /api/health            │  │ │
│  │  │  (Main Page)  │  │    │  │    /api/dashboard/stats   │  │ │
│  │  └───────────────┘  │    │  └───────────────────────────┘  │ │
│  │                     │    │                                 │ │
│  │  ┌───────────────┐  │    │  ┌───────────────────────────┐  │ │
│  │  │    pages/     │  │    │  │    Data Layer (Mock)      │  │ │
│  │  │  Dashboard    │──┼────┼──│    → Firestore (Future)   │  │ │
│  │  └───────────────┘  │    │  └───────────────────────────┘  │ │
│  │                     │    │                                 │ │
│  │  ┌───────────────┐  │    └─────────────────────────────────┘ │
│  │  │   services/   │  │                                        │
│  │  │ backend_api.py│  │                                        │
│  │  └───────────────┘  │                                        │
│  └─────────────────────┘                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Project Structure

```
📦 ElevenDops/
├── pyproject.toml              # Poetry configuration
├── poetry.lock                 # Locked dependencies
├── .env.example                # Environment variable template
├── Dockerfile                  # Cloud Run deployment
├── README.md                   # Project documentation
│
├── backend/                    # FastAPI backend
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── health.py       # Health check endpoint
│   │   │   └── dashboard.py    # Dashboard stats endpoint
│   │   └── deps.py             # Dependency injection
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   └── services/
│       ├── __init__.py
│       └── data_service.py     # Mock data layer
│
└── streamlit_app/              # Streamlit frontend
    ├── app.py                  # Main application entry
    ├── pages/
    │   └── 1_Doctor_Dashboard.py
    ├── services/
    │   ├── __init__.py
    │   └── backend_api.py      # API client service
    └── components/
        ├── __init__.py
        └── metrics.py          # Reusable UI components
```

### 2. FastAPI Backend Interfaces

#### Health Check Endpoint
```python
# GET /api/health
class HealthResponse(BaseModel):
    status: str  # "healthy" | "unhealthy"
    timestamp: datetime
    version: str
```

#### Dashboard Stats Endpoint
```python
# GET /api/dashboard/stats
class DashboardStatsResponse(BaseModel):
    document_count: int
    agent_count: int
    audio_count: int
    last_activity: Optional[datetime]
```

### 3. Backend API Client Interface

```python
# streamlit_app/services/backend_api.py
@dataclass
class DashboardStats:
    document_count: int
    agent_count: int
    audio_count: int
    last_activity: Optional[datetime]

class BackendAPIClient:
    def __init__(self, base_url: str = None, timeout: float = 10.0):
        """Initialize client with configurable base URL and timeout."""
        
    async def health_check(self) -> dict:
        """Check backend health status."""
        
    async def get_dashboard_stats(self) -> DashboardStats:
        """Fetch dashboard statistics from backend."""

class APIError(Exception):
    """Custom exception for API errors."""
    def __init__(self, message: str, status_code: int = None):
        pass
```

## Data Models

### Pydantic Schemas (Backend)

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str

class DashboardStatsResponse(BaseModel):
    document_count: int
    agent_count: int  
    audio_count: int
    last_activity: Optional[datetime]

class ErrorResponse(BaseModel):
    detail: str
    error_code: str
```

### Dataclasses (Frontend Service)

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class DashboardStats:
    document_count: int
    agent_count: int
    audio_count: int
    last_activity: Optional[datetime]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Based on the prework analysis, the following properties have been identified for property-based testing:

### Property 1: Health endpoint response structure
*For any* valid request to GET /api/health, the response SHALL always contain status, timestamp, and version fields with correct types (string, datetime, string respectively).
**Validates: Requirements 2.1**

### Property 2: Dashboard stats response completeness
*For any* valid request to GET /api/dashboard/stats, the response SHALL always contain document_count, agent_count, audio_count as non-negative integers and last_activity as optional datetime.
**Validates: Requirements 2.2**

### Property 3: Pydantic model validation
*For any* invalid input data to Pydantic models, the System SHALL raise ValidationError with descriptive error messages.
**Validates: Requirements 2.3**

### Property 4: Backend API client configuration
*For any* initialization of BackendAPIClient without explicit base_url, the client SHALL use the BACKEND_API_URL environment variable or default to "http://localhost:8000".
**Validates: Requirements 5.1**

### Property 5: API error handling
*For any* failed API call (network error, timeout, non-2xx response), the BackendAPIClient SHALL raise APIError with meaningful message and status code.
**Validates: Requirements 4.3, 5.3**

### Property 6: Dashboard stats return type
*For any* successful call to get_dashboard_stats(), the method SHALL return a DashboardStats dataclass instance with all fields populated.
**Validates: Requirements 5.4**

### Property 7: Environment variable defaults
*For any* missing non-critical environment variable, the System SHALL use sensible defaults and log a warning without crashing.
**Validates: Requirements 6.2**

### Property 8: Critical configuration validation
*For any* missing critical configuration (e.g., in production mode), the System SHALL fail fast with clear error message during startup.
**Validates: Requirements 6.3**

## Error Handling

### Backend Error Handling

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

# Standard error response format
{
    "detail": "Human-readable error message",
    "error_code": "MACHINE_READABLE_CODE"
}

# Error codes
ERROR_CODES = {
    "INTERNAL_ERROR": 500,
    "NOT_FOUND": 404,
    "VALIDATION_ERROR": 422,
    "SERVICE_UNAVAILABLE": 503
}
```

### Frontend Error Handling

```python
class APIError(Exception):
    """Raised when API call fails."""
    
class ConnectionError(APIError):
    """Raised when backend is unreachable."""
    
class TimeoutError(APIError):
    """Raised when request times out."""
```

### Streamlit Error Display

```python
try:
    stats = await client.get_dashboard_stats()
except APIError as e:
    st.error(f"Failed to load dashboard: {e.message}")
    if st.button("Retry"):
        st.rerun()
```

## Testing Strategy

### Dual Testing Approach

This project employs both unit testing and property-based testing for comprehensive coverage:

1. **Unit Tests**: Verify specific examples, edge cases, and integration points
2. **Property-Based Tests**: Verify universal properties that should hold across all inputs

### Testing Framework

- **pytest**: Primary testing framework
- **hypothesis**: Property-based testing library for Python
- **pytest-asyncio**: Async test support
- **httpx**: For testing FastAPI endpoints

### Unit Test Coverage

1. **Backend API Endpoints**
   - Health check returns correct structure
   - Dashboard stats returns mock data correctly
   - CORS headers are present

2. **Frontend Service Module**
   - Client initialization with defaults
   - Successful API calls return correct types
   - Error handling for various failure modes

3. **Streamlit Pages**
   - Page configuration is set correctly
   - Components render without errors

### Property-Based Test Coverage

Each property-based test will be tagged with the format:
`**Feature: streamlit-mvp-foundation, Property {number}: {property_text}**`

```python
# Example property test structure
from hypothesis import given, strategies as st

@given(st.integers(min_value=0), st.integers(min_value=0))
def test_dashboard_stats_non_negative(doc_count, agent_count):
    """
    **Feature: streamlit-mvp-foundation, Property 2: Dashboard stats response completeness**
    """
    # Test implementation
```

### Test Configuration

- Minimum 100 iterations for property-based tests
- Async test support enabled
- Mock data layer for isolated testing
