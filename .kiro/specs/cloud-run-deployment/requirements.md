# Requirements Document

## Introduction

This specification covers the deployment of the ElevenDops medical assistant system to Google Cloud Run. The system consists of a FastAPI backend and Streamlit frontend that will be deployed as a single container service for simplified management.

## Glossary

- **Cloud_Run**: Google Cloud's fully managed serverless platform for containerized applications
- **ElevenDops_Service**: The combined application container running both FastAPI backend and Streamlit frontend
- **Backend_Process**: The FastAPI application handling API requests, business logic, and ElevenLabs integration
- **Frontend_Process**: The Streamlit application providing the user interface
- **Secret_Manager**: Google Cloud service for securely storing and accessing sensitive configuration
- **Artifact_Registry**: Google Cloud's container image repository
- **Cloud_Build**: Google Cloud's CI/CD service for building and deploying containers
- **Service_Account**: Google Cloud identity for services to authenticate and authorize API calls
- **Firestore**: Google Cloud's NoSQL document database (already in use)
- **Cloud_Storage**: Google Cloud's object storage service (GCS)
- **Process_Manager**: A supervisor script that manages both backend and frontend processes within the container

## Requirements

### Requirement 1: Container Configuration

**User Story:** As a DevOps engineer, I want a properly configured Docker container that runs both services, so that deployment is simplified on Cloud Run.

#### Acceptance Criteria

1. THE ElevenDops_Service SHALL be containerized with a single Dockerfile containing both Backend_Process and Frontend_Process
2. WHEN building the container, THE Cloud_Build SHALL use multi-stage builds to minimize image size
3. THE container SHALL run as a non-root user for security compliance
4. WHEN the container starts, THE Process_Manager SHALL start both Backend_Process and Frontend_Process
5. THE Backend_Process SHALL listen on an internal port (default 8000)
6. THE Frontend_Process SHALL listen on the PORT environment variable provided by Cloud Run (external traffic)
7. THE Frontend_Process SHALL proxy API requests to the Backend_Process via localhost

### Requirement 2: Environment Configuration

**User Story:** As a developer, I want environment-specific configuration, so that the application behaves correctly in production.

#### Acceptance Criteria

1. WHEN deployed to Cloud Run, THE ElevenDops_Service SHALL read configuration from environment variables
2. THE Backend_Process SHALL disable emulator settings (USE_FIRESTORE_EMULATOR=false, USE_GCS_EMULATOR=false) in production
3. WHEN APP_ENV is set to "production", THE Backend_Process SHALL require critical API keys (ELEVENLABS_API_KEY, GOOGLE_API_KEY)
4. THE Frontend_Process SHALL connect to the Backend_Process via localhost (BACKEND_API_URL=http://localhost:8000)
5. WHEN CORS_ORIGINS is configured, THE Backend_Process SHALL include localhost origins for internal communication

### Requirement 3: Secret Management

**User Story:** As a security engineer, I want sensitive credentials stored securely, so that API keys are not exposed in configuration files or environment variables.

#### Acceptance Criteria

1. THE Cloud_Run service SHALL access sensitive credentials via Google Secret Manager
2. WHEN deploying, THE deployment configuration SHALL reference secrets for ELEVENLABS_API_KEY, GOOGLE_API_KEY, and LANGSMITH_API_KEY
3. THE Service_Account SHALL have secretAccessor role for required secrets
4. IF a required secret is unavailable, THEN THE Backend_Process SHALL fail startup with a clear error message

### Requirement 4: Service Deployment Configuration

**User Story:** As a DevOps engineer, I want declarative deployment configuration, so that deployments are reproducible and version-controlled.

#### Acceptance Criteria

1. THE deployment SHALL use a Cloud Run service YAML file for declarative configuration
2. THE ElevenDops_Service SHALL be configured with appropriate CPU and memory limits (minimum 2 CPU, 1GB memory for running both processes)
3. WHEN traffic increases, THE Cloud_Run service SHALL auto-scale based on concurrent requests
4. THE service SHALL have a maximum instance limit to control costs
5. THE Backend_Process SHALL have a health check endpoint at /api/health for Cloud Run health probes
6. THE Process_Manager SHALL ensure both processes are healthy before reporting container ready

### Requirement 5: CI/CD Pipeline

**User Story:** As a developer, I want automated build and deployment, so that code changes are deployed consistently.

#### Acceptance Criteria

1. THE Cloud_Build SHALL build the container image on code push to the main branch
2. WHEN a build succeeds, THE Cloud_Build SHALL push the image to Artifact Registry
3. WHEN the image is pushed, THE Cloud_Build SHALL deploy the updated service to Cloud Run
4. THE Cloud_Build configuration SHALL be defined in a cloudbuild.yaml file
5. IF a build or deployment fails, THEN THE Cloud_Build SHALL report the failure status

### Requirement 6: Networking and Security

**User Story:** As a security engineer, I want proper network configuration, so that the service is secure.

#### Acceptance Criteria

1. THE ElevenDops_Service SHALL be publicly accessible with HTTPS
2. THE Backend_Process SHALL only accept requests from localhost (internal) and the Streamlit frontend
3. THE service SHALL use HTTPS for all external communication
4. THE Service_Account SHALL have minimum required permissions (Firestore access, Cloud Storage access, Secret Manager access)

### Requirement 7: Logging and Monitoring

**User Story:** As an operations engineer, I want centralized logging and monitoring, so that I can troubleshoot issues and track performance.

#### Acceptance Criteria

1. THE Backend_Process SHALL output structured JSON logs compatible with Cloud Logging
2. THE Frontend_Process SHALL output logs compatible with Cloud Logging
3. WHEN errors occur, THE Backend_Process SHALL log error details with appropriate severity levels
4. THE Cloud_Run service SHALL expose metrics to Cloud Monitoring automatically

### Requirement 8: Database and Storage Configuration

**User Story:** As a developer, I want the application to connect to production Firestore and Cloud Storage, so that data persists correctly.

#### Acceptance Criteria

1. WHEN deployed to production, THE Backend_Process SHALL connect to Cloud Firestore (not emulator)
2. WHEN deployed to production, THE Backend_Process SHALL connect to Cloud Storage (not emulator)
3. THE Service_Account SHALL have datastore.user role for Firestore access
4. THE Service_Account SHALL have storage.objectAdmin role for the configured GCS bucket
5. THE GCS_BUCKET_NAME environment variable SHALL specify the production bucket name

### Requirement 9: Process Management

**User Story:** As a DevOps engineer, I want reliable process management within the container, so that both services run stably.

#### Acceptance Criteria

1. THE Process_Manager SHALL start the Backend_Process before the Frontend_Process
2. IF the Backend_Process crashes, THEN THE Process_Manager SHALL restart it automatically
3. IF the Frontend_Process crashes, THEN THE Process_Manager SHALL restart it automatically
4. WHEN receiving SIGTERM, THE Process_Manager SHALL gracefully shutdown both processes
5. THE Process_Manager SHALL forward logs from both processes to stdout/stderr
