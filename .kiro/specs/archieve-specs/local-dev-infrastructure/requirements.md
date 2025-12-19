# Requirements Document

## Introduction

The Local Development Infrastructure Setup establishes the foundational development environment for the ElevenDops medical assistant system. This specification focuses on setting up Firestore Emulator and fake-gcs-server to enable local development with cloud-compatible services, ensuring zero code changes when transitioning from MVP1 (local) to MVP2 (cloud deployment).

Based on the Phase 2 Implementation Roadmap, this infrastructure setup is critical because:
1. It enables persistent data storage during local development
2. It provides GCS-compatible file storage for audio files
3. It ensures the same application code works in both local and production environments
4. It eliminates the need for cloud resources during development (cost savings)

This setup follows the system's architecture principle where Firestore serves as the primary data source and GCS stores generated audio files.

## Glossary

- **Firestore_Emulator**: A local emulator that provides the same API as Google Cloud Firestore, allowing development without cloud resources
- **fake-gcs-server**: An open-source emulator that mimics Google Cloud Storage API for local development
- **Docker_Compose**: A tool for defining and running multi-container Docker applications
- **Settings_Class**: The Python configuration class that manages environment-specific settings
- **Emulator_Host**: The hostname and port where an emulator service is accessible
- **GCS_Bucket**: A container for storing objects (files) in Google Cloud Storage or its emulator
- **Environment_Variable**: A dynamic value that affects the behavior of running processes
- **Backend_API**: The FastAPI service that handles all business logic and data operations

## Requirements

### Requirement 1

**User Story:** As a developer, I want to run Firestore locally using an emulator, so that I can develop and test database operations without cloud resources.

#### Acceptance Criteria

1. WHEN Docker Compose starts THEN the Firestore_Emulator SHALL be accessible at localhost:8080
2. WHEN the Firestore_Emulator starts THEN the emulator SHALL accept connections from the Backend_API
3. WHEN the Backend_API connects to Firestore_Emulator THEN the connection SHALL use the same google-cloud-firestore Python client as production
4. WHEN data is written to Firestore_Emulator THEN the data SHALL persist until the emulator container is stopped
5. WHEN the Firestore_Emulator is not running THEN the Backend_API SHALL display a clear error message indicating the emulator is unavailable

### Requirement 2

**User Story:** As a developer, I want to run a GCS-compatible storage server locally, so that I can develop and test file upload/download operations without cloud resources.

#### Acceptance Criteria

1. WHEN Docker Compose starts THEN the fake-gcs-server SHALL be accessible at localhost:4443
2. WHEN the fake-gcs-server starts THEN the server SHALL accept connections from the Backend_API
3. WHEN the Backend_API connects to fake-gcs-server THEN the connection SHALL use the same google-cloud-storage Python client as production
4. WHEN a file is uploaded to fake-gcs-server THEN the file SHALL be retrievable via HTTP URL
5. WHEN the GCS_Bucket does not exist THEN the storage service SHALL create the bucket automatically

### Requirement 3

**User Story:** As a developer, I want a unified configuration system, so that I can switch between local emulators and production services by changing environment variables only.

#### Acceptance Criteria

1. WHEN USE_FIRESTORE_EMULATOR is set to "true" THEN the Backend_API SHALL connect to Firestore_Emulator
2. WHEN USE_FIRESTORE_EMULATOR is set to "false" THEN the Backend_API SHALL connect to production Firestore
3. WHEN USE_GCS_EMULATOR is set to "true" THEN the Backend_API SHALL connect to fake-gcs-server
4. WHEN USE_GCS_EMULATOR is set to "false" THEN the Backend_API SHALL connect to production GCS
5. WHEN environment variables are not set THEN the Settings_Class SHALL use default values suitable for local development

### Requirement 4

**User Story:** As a developer, I want a simple startup command, so that I can quickly start all required services for local development.

#### Acceptance Criteria

1. WHEN a developer runs `docker-compose -f docker-compose.dev.yml up -d` THEN both Firestore_Emulator and fake-gcs-server SHALL start
2. WHEN Docker Compose starts THEN all services SHALL be healthy within 30 seconds
3. WHEN a developer runs `docker-compose -f docker-compose.dev.yml down` THEN all emulator services SHALL stop cleanly
4. WHEN Docker is not available THEN alternative startup scripts SHALL be provided for Windows and Linux/Mac

### Requirement 5

**User Story:** As a developer, I want environment variable templates, so that I can quickly configure my local development environment.

#### Acceptance Criteria

1. WHEN a developer clones the repository THEN a .env.example file SHALL exist with all required variables documented
2. WHEN the .env.example file is copied to .env THEN the default values SHALL work with local emulators
3. WHEN ELEVENLABS_API_KEY is not set THEN the Backend_API SHALL display a warning but continue to start
4. WHEN all emulator settings are configured THEN the Backend_API SHALL start without errors

### Requirement 6

**User Story:** As a developer, I want the storage service to generate correct URLs, so that audio files can be played in the Streamlit frontend.

#### Acceptance Criteria

1. WHEN a file is uploaded to fake-gcs-server THEN the returned URL SHALL be accessible from the browser
2. WHEN USE_GCS_EMULATOR is true THEN the URL format SHALL be `http://localhost:4443/storage/v1/b/{bucket}/o/{path}?alt=media`
3. WHEN USE_GCS_EMULATOR is false THEN the URL format SHALL be `https://storage.googleapis.com/{bucket}/{path}`
4. WHEN the Streamlit frontend requests an audio file THEN the URL SHALL return the correct audio data with proper content-type

### Requirement 7

**User Story:** As a system, I want to handle emulator connection failures gracefully, so that developers receive clear feedback when services are unavailable.

#### Acceptance Criteria

1. IF the Firestore_Emulator connection fails THEN the Backend_API SHALL log a descriptive error message
2. IF the fake-gcs-server connection fails THEN the Backend_API SHALL log a descriptive error message
3. WHEN any emulator is unavailable THEN the Backend_API health endpoint SHALL return unhealthy status
4. WHEN emulators become available after initial failure THEN the Backend_API SHALL reconnect automatically on next request

## Non-Functional Requirements

### Performance
- Docker Compose startup SHALL complete within 60 seconds
- Firestore_Emulator SHALL handle at least 100 requests per second
- fake-gcs-server SHALL handle file uploads up to 50MB

### Compatibility
- Docker Compose configuration SHALL work on Windows, macOS, and Linux
- Python configuration SHALL work with Python 3.10+
- All emulators SHALL be compatible with their production counterparts' APIs

### Developer Experience
- Documentation SHALL include step-by-step setup instructions
- Error messages SHALL clearly indicate which service is failing
- Default configuration SHALL work out-of-the-box after copying .env.example

## Dependencies

- Docker and Docker Compose installed on developer machine
- Python 3.10+ with poetry for dependency management
- google-cloud-firestore Python package
- google-cloud-storage Python package
- pnpm (for firebase-tools if using manual setup)

## Technical Notes

### Firestore Emulator Connection
The Python client connects to the emulator by setting the `FIRESTORE_EMULATOR_HOST` environment variable before initializing the client:
```python
import os
os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
from google.cloud import firestore
db = firestore.Client(project="elevenlabs-local")
```

### fake-gcs-server Connection
The Python client connects to fake-gcs-server by overriding the API endpoint:
```python
from google.cloud import storage
from google.auth.credentials import AnonymousCredentials

client = storage.Client(
    credentials=AnonymousCredentials(),
    project="elevenlabs-local",
)
client._http._base_url = "http://localhost:4443"
```
