# Implementation Plan

- [x] 1. Add dependencies and extend backend schemas

  - [x] 1.1 Add elevenlabs SDK to pyproject.toml

    - Add `elevenlabs = "^1.59.0"` to dependencies
    - Run `poetry install` to update lock file
    - _Requirements: 3.1, 3.2, 3.3_

  - [x] 1.2 Create knowledge document schemas in backend/models/schemas.py

    - Add DocumentType enum (FAQ, POST_CARE, PRECAUTIONS)
    - Add SyncStatus enum (PENDING, SYNCING, COMPLETED, FAILED)
    - Add KnowledgeDocumentCreate request model with validation
    - Add KnowledgeDocumentResponse model with structured_sections
    - Add KnowledgeDocumentListResponse model
    - _Requirements: 6.4, 2.1, 2.2_

  - [x] 1.3 Write property test for schema validation
    - **Property 3: Required Field Validation**
    - **Validates: Requirements 1.4**

- [x] 2. Create ElevenLabs service

  - [x] 2.1 Create backend/services/elevenlabs_service.py

    - Implement ElevenLabsService class with ElevenLabs client initialization
    - Implement create_document() using add_to_knowledge_base()
    - Implement delete_document() method using delete_knowledge_base_document()
    - Add error handling with custom exceptions
    - _Requirements: 3.2, 3.3, 5.3_

  - [x] 2.2 Write property test for ElevenLabs service
    - **Property 5: Sync Workflow Integrity**
    - **Property 6: Sync Failure Handling**
    - **Validates: Requirements 3.2, 3.3, 3.4**

- [x] 3. Extend data service for knowledge documents

  - [x] 3.1 Add knowledge document methods to backend/services/data_service.py

    - Add create_knowledge_document() method with unique ID generation and markdown parsing for structured_sections
    - Add get_knowledge_documents() method
    - Add get_knowledge_document() method
    - Add update_knowledge_sync_status() method
    - Add delete_knowledge_document() method
    - _Requirements: 6.3, 6.4, 4.1_

  - [x] 3.2 Write property test for data service
    - **Property 4: Document Metadata Persistence**
    - **Property 8: Unique Knowledge ID Generation**
    - **Property 9: Document Schema Completeness**
    - **Validates: Requirements 2.3, 6.3, 6.4**

- [x] 4. Create Knowledge API router

  - [x] 4.1 Create backend/api/knowledge.py

    - Implement POST /api/knowledge endpoint (create and sync) with naming convention
    - Implement GET /api/knowledge endpoint (list documents)
    - Implement GET /api/knowledge/{id} endpoint (get single document)
    - Implement DELETE /api/knowledge/{id} endpoint (delete document)
    - Implement POST /api/knowledge/{id}/retry-sync endpoint
    - Wire up ElevenLabsService and DataService
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [x] 4.2 Register knowledge router in backend/main.py

    - Import and include knowledge_router
    - _Requirements: 7.1_

  - [x] 4.3 Write property tests for Knowledge API
    - **Property 7: Document List Completeness**
    - **Property 10: Deletion Cascade**
    - **Property 11: Firestore Deletion Priority**
    - **Validates: Requirements 4.1, 4.2, 5.2, 5.3, 5.4**

- [x] 5. Checkpoint - Ensure all backend tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Extend Streamlit frontend services

  - [x] 6.1 Add KnowledgeDocument model to streamlit_app/services/models.py

    - Create KnowledgeDocument dataclass with all required fields including structured_sections
    - _Requirements: 6.4_

  - [x] 6.2 Extend BackendAPIClient in streamlit_app/services/backend_api.py

    - Add upload_knowledge() method
    - Add get_knowledge_documents() method with parsing for structured_sections
    - Add delete_knowledge_document() method
    - Add retry_knowledge_sync() method
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [x] 6.3 Update streamlit_app/services/**init**.py exports
    - Export KnowledgeDocument model
    - _Requirements: 6.4_

- [x] 7. Create Upload Knowledge Streamlit page

  - [x] 7.1 Create streamlit_app/pages/2_Upload_Knowledge.py

    - Implement page configuration and header
    - Implement file uploader with type and size validation
    - Implement metadata form (disease name, document type)
    - Implement content preview section
    - Implement Save & Sync button with backend API call
    - Implement document list table with status indicators
    - Implement delete functionality with confirmation dialog
    - Implement retry sync functionality for failed documents
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 3.5, 4.1, 4.2, 4.3, 4.4, 4.5, 5.1_

  - [x] 7.2 Write property tests for file validation
    - **Property 1: File Type Validation**
    - **Property 2: File Size Validation**
    - **Validates: Requirements 1.1, 1.2**

- [x] 8. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
