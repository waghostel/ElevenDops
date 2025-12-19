# Implementation Plan

- [x] 1. Set up project structure and Poetry configuration

  - [x] 1.1 Create pyproject.toml with Poetry configuration
    - Define project metadata (name: elevendops, version: 0.1.0)
    - Add core dependencies: streamlit, fastapi, uvicorn, google-cloud-firestore, httpx, python-dotenv, pydantic
    - Add dev dependencies: pytest, pytest-asyncio, hypothesis, httpx
    - Configure Python version requirement (>=3.10)
    - _Requirements: 1.1, 1.2_
  - [x] 1.2 Create directory structure
    - Create backend/ directory with **init**.py, main.py, api/, models/, services/ subdirectories
    - Create streamlit_app/ directory with app.py placeholder, pages/, services/, components/ subdirectories
    - Create all necessary **init**.py files
    - _Requirements: 1.3_
  - [x] 1.3 Create environment configuration files
    - Create .env.example with BACKEND_API_URL, ELEVENLABS_API_KEY, GOOGLE_CLOUD_PROJECT placeholders
    - Create .gitignore to exclude .env, **pycache**, .pytest_cache
    - _Requirements: 1.4_

- [x] 2. Implement FastAPI backend foundation

  - [x] 2.1 Create Pydantic models and schemas
    - Implement HealthResponse model with status, timestamp, version fields
    - Implement DashboardStatsResponse model with document_count, agent_count, audio_count, last_activity fields
    - Implement ErrorResponse model with detail and error_code fields
    - _Requirements: 2.3_
  - [x]\* 2.2 Write property test for Pydantic model validation
    - **Property 3: Pydantic model validation**
    - Test that invalid input data raises ValidationError
    - **Validates: Requirements 2.3**
  - [x] 2.3 Implement mock data service layer
    - Create DataService class with get_dashboard_stats() method
    - Return mock data: document_count=5, agent_count=2, audio_count=10, last_activity=now
    - Design for easy replacement with Firestore client
    - _Requirements: 2.5_
  - [x] 2.4 Implement health check endpoint
    - Create GET /api/health route returning HealthResponse
    - Include status="healthy", current timestamp, and version from config
    - _Requirements: 2.1_
  - [x]\* 2.5 Write property test for health endpoint
    - **Property 1: Health endpoint response structure**
    - Test response always contains status, timestamp, version with correct types
    - **Validates: Requirements 2.1**
  - [x] 2.6 Implement dashboard stats endpoint
    - Create GET /api/dashboard/stats route returning DashboardStatsResponse
    - Inject DataService dependency
    - _Requirements: 2.2_
  - [x]\* 2.7 Write property test for dashboard stats endpoint
    - **Property 2: Dashboard stats response completeness**
    - Test response contains all required fields with correct types
    - **Validates: Requirements 2.2**
  - [x] 2.8 Configure FastAPI application with CORS
    - Create main.py with FastAPI app instance
    - Configure CORS middleware with configurable origins
    - Include API routers
    - _Requirements: 2.4_

- [x] 3. Checkpoint - Ensure backend tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement Backend API client service module

  - [x] 4.1 Create APIError custom exception class
    - Implement APIError with message and status_code attributes
    - Implement ConnectionError and TimeoutError subclasses
    - _Requirements: 5.3_
  - [x] 4.2 Create DashboardStats dataclass
    - Define dataclass with document_count, agent_count, audio_count, last_activity fields
    - Add type hints for all fields
    - _Requirements: 5.4_
  - [x] 4.3 Implement BackendAPIClient class
    - Initialize with base_url from environment variable or default
    - Configure httpx async client with timeout settings
    - Implement health_check() method
    - Implement get_dashboard_stats() method returning DashboardStats
    - _Requirements: 5.1, 5.2, 5.4_
  - [x]\* 4.4 Write property test for client configuration
    - **Property 4: Backend API client configuration**
    - Test client uses environment variable or default URL
    - **Validates: Requirements 5.1**
  - [x]\* 4.5 Write property test for API error handling
    - **Property 5: API error handling**
    - Test APIError is raised for failed calls with meaningful messages
    - **Validates: Requirements 4.3, 5.3**
  - [x]\* 4.6 Write property test for dashboard stats return type
    - **Property 6: Dashboard stats return type**
    - Test get_dashboard_stats() returns DashboardStats dataclass
    - **Validates: Requirements 5.4**

- [x] 5. Checkpoint - Ensure service module tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement Streamlit main application (app.py)

  - [x] 6.1 Create app.py with page configuration
    - Configure st.set_page_config with title="ElevenDops", icon="🏥", layout="wide"
    - _Requirements: 3.4_
  - [x] 6.2 Implement main page content
    - Display ElevenDops branding with title and logo placeholder
    - Show welcome message explaining system purpose for medical education
    - Display system description and key features
    - _Requirements: 3.1, 3.3_
  - [x] 6.3 Implement sidebar navigation
    - Add navigation section with links to available pages
    - Include appropriate icons for each page link
    - _Requirements: 3.2_
  - [x] 6.4 Add footer with version info
    - Display version number and copyright notice
    - _Requirements: 3.5_

- [x] 7. Implement Doctor Dashboard page (1_Doctor_Dashboard.py)

  - [x] 7.1 Create dashboard page structure
    - Set page title and header
    - Initialize BackendAPIClient
    - _Requirements: 4.1_
  - [x] 7.2 Implement metric cards display
    - Create four columns for metric cards
    - Display document_count, agent_count, audio_count, last_activity
    - Use st.metric for each statistic
    - _Requirements: 4.1_
  - [x] 7.3 Implement data fetching with error handling
    - Call backend API through backend_api service
    - Handle APIError with error message display
    - Implement retry button on error
    - _Requirements: 4.2, 4.3_
  - [x] 7.4 Implement refresh functionality
    - Add manual refresh button
    - Trigger data reload on button click
    - _Requirements: 4.4_
  - [x] 7.5 Implement empty state handling
    - Display guidance messages when counts are zero
    - Link to relevant actions (upload knowledge, create agent, etc.)
    - _Requirements: 4.5_

- [x] 8. Implement configuration and deployment setup

  - [x] 8.1 Create configuration module
    - Implement Settings class with environment variable loading
    - Provide sensible defaults for local development
    - Log warnings for missing non-critical variables
    - _Requirements: 6.2_
  - [x]\* 8.2 Write property test for environment defaults
    - **Property 7: Environment variable defaults**
    - Test defaults are used when env vars missing
    - **Validates: Requirements 6.2**
  - [x] 8.3 Implement startup validation
    - Validate critical configurations on startup
    - Fail fast with clear error messages for missing critical settings
    - _Requirements: 6.3_
  - [x]\* 8.4 Write property test for critical config validation
    - **Property 8: Critical configuration validation**
    - Test application fails fast for missing critical config
    - **Validates: Requirements 6.3**
  - [x] 8.5 Create Dockerfile for Cloud Run
    - Use Python 3.10+ base image
    - Install Poetry and dependencies
    - Configure port exposure (8501 for Streamlit, 8000 for FastAPI)
    - Add health check configuration
    - _Requirements: 6.4_
  - [x] 8.6 Create run scripts for local development
    - Create script to run both Streamlit and FastAPI concurrently
    - Document commands in README
    - _Requirements: 6.1_

- [x] 9. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
