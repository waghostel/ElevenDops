# Implementation Plan: Cloud Run Deployment

## Overview

This plan implements the Cloud Run deployment for ElevenDops using a single-container approach with both FastAPI backend and Streamlit frontend. Tasks are organized to build incrementally, starting with configuration files, then the process manager, and finally CI/CD automation.

## Tasks

- [x] 1. Create production Dockerfile for Cloud Run
  - [x] 1.1 Create Dockerfile.cloudrun with multi-stage build
    - Use python:3.11-slim as base
    - Install dependencies with Poetry in builder stage
    - Copy only production dependencies to final stage
    - Set production environment variables (USE_FIRESTORE_EMULATOR=false, etc.)
    - Install curl for health checks
    - Create non-root user (appuser)
    - _Requirements: 1.1, 1.2, 1.3, 2.2_

  - [x] 1.2 Write property test for production configuration disables emulators
    - **Property 1: Production Configuration Disables Emulators**
    - **Validates: Requirements 2.2, 8.1, 8.2**

- [x] 2. Create process manager script
  - [x] 2.1 Create scripts/start.sh process manager
    - Start FastAPI backend on port 8000
    - Wait for backend health check before starting frontend
    - Start Streamlit on Cloud Run's PORT environment variable
    - Implement SIGTERM trap for graceful shutdown
    - Implement process monitoring and auto-restart
    - _Requirements: 1.4, 1.5, 1.6, 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 3. Create Cloud Run service configuration
  - [x] 3.1 Create deploy/service.yaml for Cloud Run
    - Configure 2 CPU, 1GB memory limits
    - Set auto-scaling (min 0, max 10 instances)
    - Configure service account reference
    - Add secret references for API keys
    - Configure startup and liveness probes
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [x] 3.2 Write property test for health endpoint returns valid response
    - **Property 4: Health Endpoint Returns Valid Response**
    - **Validates: Requirements 4.5**

- [x] 4. Create Cloud Build CI/CD configuration
  - [x] 4.1 Create cloudbuild.yaml for automated deployment
    - Build Docker image with commit SHA tag
    - Push to Artifact Registry
    - Deploy to Cloud Run
    - Configure substitution variables for region and project
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 5. Update backend configuration for production
  - [x] 5.1 Update backend/config.py for Cloud Run compatibility
    - Ensure BACKEND_API_URL defaults to localhost:8000 in production
    - Add validation for production API key requirements
    - Ensure CORS includes localhost for internal communication
    - _Requirements: 2.1, 2.3, 2.4, 2.5, 3.4_

  - [x] 5.2 Write property test for production configuration requires API keys
    - **Property 2: Production Configuration Requires Critical API Keys**
    - **Validates: Requirements 2.3, 3.4**

  - [x] 5.3 Write property test for configuration reads from environment
    - **Property 6: Configuration Reads From Environment**
    - **Validates: Requirements 2.1, 8.5**

- [x] 6. Checkpoint - Verify configuration files
  - Ensure Dockerfile.cloudrun builds successfully
  - Ensure start.sh is executable and has correct syntax
  - Ensure service.yaml is valid YAML
  - Ensure cloudbuild.yaml is valid YAML
  - Ask the user if questions arise.

- [x] 7. Create deployment documentation
  - [x] 7.1 Create deploy/README.md with deployment instructions
    - Document prerequisites (GCP project, APIs enabled)
    - Document secret setup commands
    - Document service account setup commands
    - Document manual deployment commands
    - Document Cloud Build trigger setup
    - _Requirements: 3.1, 3.2, 3.3, 6.4, 8.3, 8.4_

- [x] 8. Update Streamlit configuration for production
  - [x] 8.1 Update .streamlit/config.toml for Cloud Run
    - Disable browser auto-open
    - Configure headless mode
    - Disable usage stats collection
    - _Requirements: 1.6, 7.2_

- [x] 9. Add structured logging for Cloud Logging
  - [x] 9.1 Update backend logging configuration for JSON output
    - Configure Python logging to output JSON format
    - Include severity levels compatible with Cloud Logging
    - Ensure error logs include stack traces
    - _Requirements: 7.1, 7.3_

  - [x] 9.2 Write property test for error logging produces structured output
    - Test that logged errors are valid JSON
    - Test that severity levels are correct
    - _Requirements: 7.1, 7.3_

- [x] 10. Final checkpoint - Complete deployment verification
  - Ensure all configuration files are created
  - Ensure all property tests pass
  - Review deployment documentation
  - Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- The deployment can be tested locally using `docker build` before pushing to Cloud Run
