# Requirements Document

## Introduction

This specification defines the MVP foundation architecture for the ElevenDops intelligent medical assistant system, including the Streamlit main application entry point (app.py) and the Doctor Dashboard page (1_Doctor_Dashboard.py). The system uses Streamlit as a rapid prototyping frontend, FastAPI as the backend API service, and Poetry for package management. This architecture is designed to support future migration to a React/TypeScript Next.js project.

## Glossary

- **ElevenDops**: An intelligent medical assistant system integrating ElevenLabs voice technology
- **Streamlit**: A Python rapid prototyping framework used to build the MVP user interface
- **FastAPI**: A high-performance Python web API framework providing backend services
- **Poetry**: A Python package management tool
- **Doctor Dashboard**: A dashboard providing system status overview and quick monitoring capabilities for doctors
- **Firestore**: Google Cloud's NoSQL database serving as the primary data source
- **Backend API Client**: A service module for Streamlit frontend to communicate with FastAPI backend
- **MVP**: Minimum Viable Product

## Requirements

### Requirement 1

**User Story:** As a developer, I want to set up the project structure with Poetry package management, so that I can manage dependencies consistently and prepare for Cloud Run deployment.

#### Acceptance Criteria

1. WHEN the project is initialized THEN the System SHALL contain a pyproject.toml file with Poetry configuration including project metadata and dependencies
2. WHEN Poetry dependencies are defined THEN the System SHALL include streamlit, fastapi, uvicorn, google-cloud-firestore, httpx, and python-dotenv as core dependencies
3. WHEN the project structure is created THEN the System SHALL follow the directory layout: streamlit_app/app.py, streamlit_app/pages/, streamlit_app/services/, and backend/ directories
4. WHEN environment configuration is needed THEN the System SHALL use a .env.example file to document required environment variables without exposing sensitive values

### Requirement 2

**User Story:** As a developer, I want to create the FastAPI backend foundation, so that the Streamlit frontend can consume RESTful APIs that will be reusable in future Next.js integration.

#### Acceptance Criteria

1. WHEN the FastAPI application starts THEN the System SHALL expose a health check endpoint at GET /api/health returning status and timestamp
2. WHEN the dashboard data is requested THEN the System SHALL provide GET /api/dashboard/stats endpoint returning document count, agent count, audio count, and last activity timestamp
3. WHEN API responses are generated THEN the System SHALL use Pydantic models for request/response validation with proper type hints
4. WHEN the backend is configured THEN the System SHALL support CORS for local development with configurable origins
5. WHEN Firestore integration is needed THEN the System SHALL provide a mock data layer that can be replaced with actual Firestore client

### Requirement 3

**User Story:** As a developer, I want to create the Streamlit main application entry point (app.py), so that users can access the system with proper navigation and branding.

#### Acceptance Criteria

1. WHEN the Streamlit application loads THEN the System SHALL display the ElevenDops branding with system title and description in the main area
2. WHEN the sidebar is rendered THEN the System SHALL show navigation links to all available pages with appropriate icons
3. WHEN the main page is accessed THEN the System SHALL display a welcome message explaining the system purpose for medical education assistance
4. WHEN the application configuration is set THEN the System SHALL configure page title, icon, and wide layout mode via st.set_page_config
5. WHEN the footer is rendered THEN the System SHALL display version information and copyright notice

### Requirement 4

**User Story:** As a doctor, I want to view a dashboard with system statistics, so that I can quickly monitor the status of uploaded documents, agents, audio files, and recent patient activities.

#### Acceptance Criteria

1. WHEN the Doctor Dashboard page loads THEN the System SHALL display four metric cards showing: uploaded document count, active agent count, generated audio count, and last patient activity time
2. WHEN dashboard data is fetched THEN the System SHALL call the backend API endpoint GET /api/dashboard/stats through the backend_api service module
3. WHEN the API call fails THEN the System SHALL display an error message with retry option and maintain the previous data state if available
4. WHEN the dashboard is displayed THEN the System SHALL provide a manual refresh button to update statistics on demand
5. WHEN metric values are zero THEN the System SHALL display appropriate empty state messages guiding the doctor to relevant actions

### Requirement 5

**User Story:** As a developer, I want to implement a backend API client service module, so that Streamlit pages can communicate with FastAPI backend without direct API logic in the UI layer.

#### Acceptance Criteria

1. WHEN the backend_api service is initialized THEN the System SHALL configure the base URL from environment variables with localhost default for development
2. WHEN API calls are made THEN the System SHALL use httpx async client with configurable timeout settings
3. WHEN API errors occur THEN the System SHALL raise custom exceptions with meaningful error messages for UI handling
4. WHEN the dashboard stats are requested THEN the System SHALL provide a get_dashboard_stats() method returning typed DashboardStats dataclass
5. WHEN the service module is imported THEN the System SHALL not execute any side effects until methods are explicitly called

### Requirement 6

**User Story:** As a developer, I want to configure the application for local development and future Cloud Run deployment, so that the system can run in both environments seamlessly.

#### Acceptance Criteria

1. WHEN running locally THEN the System SHALL support concurrent execution of Streamlit and FastAPI using a single entry point or documented commands
2. WHEN environment variables are missing THEN the System SHALL provide sensible defaults for local development while logging warnings
3. WHEN the application starts THEN the System SHALL validate required configurations and fail fast with clear error messages if critical settings are missing
4. WHEN Docker deployment is prepared THEN the System SHALL include a Dockerfile configured for Cloud Run with proper port exposure and health checks
