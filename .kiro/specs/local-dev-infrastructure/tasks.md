# Implementation Plan

- [x] 1. Create Docker Compose configuration for emulators
  - [x] 1.1 Create docker-compose.dev.yml file
    - Add Firestore Emulator service using google/cloud-sdk:emulators image
    - Configure port mapping 8080:8080 for Firestore
    - Add fake-gcs-server service using fsouza/fake-gcs-server image
    - Configure port mapping 4443:4443 for GCS
    - Add health checks for both services
    - _Requirements: 1.1, 2.1, 4.1_

  - [x]* 1.2 Write integration test for Docker Compose startup
    - **Property 5: Docker Compose Service Availability**
    - Verify both services start and become healthy within 60 seconds
    - **Validates: Requirements 4.1, 4.2**

- [x] 2. Create Settings configuration class
  - [x] 2.1 Update backend/config.py with Settings class
    - Add USE_FIRESTORE_EMULATOR boolean setting with default true
    - Add FIRESTORE_EMULATOR_HOST string setting with default localhost:8080
    - Add GOOGLE_CLOUD_PROJECT string setting with default elevenlabs-local
    - Add USE_GCS_EMULATOR boolean setting with default true
    - Add GCS_EMULATOR_HOST string setting with default http://localhost:4443
    - Add GCS_BUCKET_NAME string setting with default elevenlabs-audio
    - Add ELEVENLABS_API_KEY string setting
    - Use pydantic-settings for environment variable loading
    - Add get_settings() factory function with caching
    - _Requirements: 3.1, 3.3, 3.5, 5.2_

  - [x] 2.2 Write property test for configuration defaults
    - **Property 3: Configuration Default Values**
    - Test that missing environment variables use correct defaults
    - Test that defaults enable local development with emulators
    - **Validates: Requirements 3.5, 5.2**

- [x] 3. Create Firestore service wrapper
  - [x] 3.1 Create backend/services/firestore_service.py
    - Implement FirestoreService class with singleton pattern
    - Set FIRESTORE_EMULATOR_HOST environment variable when USE_FIRESTORE_EMULATOR is true
    - Initialize google.cloud.firestore.Client with project from settings
    - Add db property to access Firestore client
    - Add health_check() method to verify connectivity
    - Add logging for connection status
    - _Requirements: 1.2, 1.3, 1.5, 3.1_

  - [x] 3.2 Write property test for Firestore data persistence
    - **Property 1: Emulator Connection Consistency**
    - Test write and read operations return consistent data
    - Test data persists across multiple operations
    - **Validates: Requirements 1.3, 1.4, 3.1**

- [x] 4. Create Storage service wrapper
  - [x] 4.1 Create backend/services/storage_service.py
    - Implement StorageService class with singleton pattern
    - Use AnonymousCredentials for emulator connection
    - Override _http._base_url for emulator endpoint
    - Implement _ensure_bucket_exists() for auto-creation
    - Implement upload_file() method returning correct URL format
    - Implement upload_audio() convenience method
    - Implement delete_file() method
    - Add health_check() method to verify connectivity
    - Add logging for connection status
    - _Requirements: 2.2, 2.3, 2.4, 2.5, 3.3, 6.1, 6.2, 6.3_

  - [x] 4.2 Write property test for storage URL format
    - **Property 2: Storage URL Format Correctness**
    - Test emulator URL format matches expected pattern
    - Test production URL format matches expected pattern
    - Test uploaded files are retrievable via returned URL
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**

- [x] 5. Checkpoint - Verify emulator services work
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Enhance health check endpoint
  - [x] 6.1 Update backend/api/health.py with comprehensive checks
    - Add /health endpoint that checks both Firestore and Storage
    - Return service status for each component
    - Include emulator flag in response
    - Include error messages when services are unhealthy
    - Add /health/ready endpoint for simple readiness check
    - _Requirements: 7.1, 7.2, 7.3_

  - [x] 6.2 Write property test for health check accuracy
    - **Property 4: Health Check Accuracy**
    - Test health endpoint returns unhealthy when emulator is down
    - Test health endpoint returns healthy when emulator is up
    - **Validates: Requirements 7.3**

- [x] 7. Create startup scripts
  - [x] 7.1 Create scripts/start_emulators.bat for Windows
    - Check if Docker is running
    - Start docker-compose with dev configuration
    - Wait for services to be healthy
    - Display service URLs and status
    - _Requirements: 4.1, 4.4_

  - [x] 7.2 Create scripts/start_emulators.sh for Linux/Mac
    - Check if Docker is running
    - Start docker-compose with dev configuration
    - Wait for services to be healthy
    - Display service URLs and status
    - Make script executable
    - _Requirements: 4.1, 4.4_

- [x] 8. Create environment configuration template
  - [x] 8.1 Update .env.example with all required variables
    - Add Firestore configuration section with comments
    - Add GCS configuration section with comments
    - Add ElevenLabs configuration section with comments
    - Add application configuration section
    - Document each variable with description
    - _Requirements: 5.1, 5.2_

  - [x] 8.2 Update .gitignore to exclude .env
    - Add .env to .gitignore if not already present
    - Ensure .env.example is NOT in .gitignore
    - _Requirements: 5.1_

- [x] 9. Add Python dependencies
  - [x] 9.1 Update pyproject.toml with required packages
    - Add google-cloud-firestore ^2.16.0
    - Add google-cloud-storage ^2.14.0
    - Add pydantic-settings ^2.1.0
    - Run poetry lock to update lock file
    - _Requirements: 1.3, 2.3_

- [x] 10. Create documentation
  - [x] 10.1 Create docs/LOCAL_DEVELOPMENT.md
    - Document prerequisites (Docker, Python, pnpm)
    - Document step-by-step setup instructions
    - Document how to start emulators
    - Document how to verify services are running
    - Document troubleshooting common issues
    - _Requirements: 4.4, 5.1_

- [x] 11. Final integration testing
  - [x] 11.1 Test complete local development workflow
    - Start emulators with Docker Compose
    - Verify health endpoint returns healthy
    - Test Firestore write/read operations
    - Test Storage upload/download operations
    - Verify URLs are accessible from browser
    - Stop emulators and verify clean shutdown
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 4.1, 4.3_

- [x] 12. Final Checkpoint - Ensure all tests pass
  - Run full test suite with pytest
  - Verify all emulator services work correctly
  - Ensure documentation is complete
  - Ask the user if questions arise
