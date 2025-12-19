# Implementation Plan

## Phase 1: Interface and Configuration

- [x] 1. Create DataServiceInterface abstract base class
  - [x] 1.1 Refactor backend/services/data_service.py
    - Import ABC and abstractmethod from abc module
    - Create DataServiceInterface class extending ABC
    - Move all methods from DataServiceProtocol to DataServiceInterface as abstract methods
    - Add @abstractmethod decorator to all methods
    - Add new methods for audio and agent operations: save_audio_metadata, get_audio_files, get_audio_file, delete_audio_file, save_agent, get_agents, get_agent, delete_agent
    - Keep MockDataService class in same file, make it extend DataServiceInterface
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 1.2 Update MockDataService to implement new interface methods
    - Add _audio_files dict for in-memory audio storage
    - Add _agents dict for in-memory agent storage
    - Implement save_audio_metadata method
    - Implement get_audio_files method with optional knowledge_id filter
    - Implement get_audio_file method
    - Implement delete_audio_file method
    - Implement save_agent method
    - Implement get_agents method with optional doctor_id filter
    - Implement get_agent method
    - Implement delete_agent method
    - _Requirements: 1.2, 1.3_

- [x] 2. Update configuration for data service selection
  - [x] 2.1 Add use_mock_data setting to backend/config.py
    - Add use_mock_data boolean field with default False
    - Add description explaining when to use mock vs Firestore
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 2.2 Update factory function in data_service.py
    - Add global variables for singleton instances
    - Implement logic: if use_firestore_emulator OR not use_mock_data → FirestoreDataService
    - Implement logic: if use_mock_data AND not use_firestore_emulator → MockDataService
    - Use lazy import for FirestoreDataService to avoid circular imports
    - _Requirements: 2.1, 2.2, 2.3, 2.4_


## Phase 2: FirestoreDataService Implementation

- [x] 3. Create FirestoreDataService class structure
  - [x] 3.1 Create backend/services/firestore_data_service.py
    - Import required modules: logging, datetime, uuid, typing
    - Import firestore and SERVER_TIMESTAMP from google.cloud
    - Import DataServiceInterface from data_service
    - Import get_firestore_service from firestore_service
    - Import all schema models from backend.models.schemas
    - Define collection name constants: KNOWLEDGE_DOCUMENTS, AUDIO_FILES, AGENTS, CONVERSATIONS, PATIENT_SESSIONS
    - Create FirestoreDataService class extending DataServiceInterface
    - Implement singleton pattern with __new__ and _initialized flag
    - Initialize _db from get_firestore_service().db in __init__
    - _Requirements: 3.1, 4.1, 5.1, 6.1, 8.1_

  - [x] 3.2 Implement helper conversion methods
    - Create _doc_to_knowledge_response method to convert Firestore doc to KnowledgeDocumentResponse
    - Create _doc_to_audio_metadata method to convert Firestore doc to AudioMetadata
    - Create _doc_to_agent_response method to convert Firestore doc to AgentResponse
    - Create _doc_to_conversation_detail method to convert Firestore doc to ConversationDetailSchema
    - Create _doc_to_session_response method to convert Firestore doc to PatientSessionResponse
    - Handle enum conversions (DocumentType, SyncStatus, AnswerStyle)
    - Handle optional fields with .get() and defaults
    - _Requirements: 3.2, 4.2, 5.2, 6.2_

- [x] 4. Implement Knowledge Document operations
  - [x] 4.1 Implement create_knowledge_document method
    - Generate UUID for knowledge_id
    - Parse structured_sections from raw_content (reuse logic from MockDataService)
    - Create document dict with all fields
    - Use SERVER_TIMESTAMP for created_at
    - Write to KNOWLEDGE_DOCUMENTS collection using knowledge_id as document ID
    - Return KnowledgeDocumentResponse
    - _Requirements: 3.1, 3.2_

  - [x] 4.2 Implement get_knowledge_documents method
    - Query KNOWLEDGE_DOCUMENTS collection
    - Optionally filter by doctor_id if provided
    - Convert each document to KnowledgeDocumentResponse
    - Return list of responses
    - _Requirements: 3.3_

  - [x] 4.3 Implement get_knowledge_document method
    - Get document by knowledge_id from KNOWLEDGE_DOCUMENTS
    - Return None if document doesn't exist
    - Convert to KnowledgeDocumentResponse if exists
    - _Requirements: 3.3, 9.4_

  - [x] 4.4 Implement update_knowledge_sync_status method
    - Get document reference by knowledge_id
    - Update sync_status field
    - Optionally update elevenlabs_document_id if provided
    - Return True on success, False if document not found
    - _Requirements: 3.4_

  - [x] 4.5 Implement delete_knowledge_document method
    - Delete document by knowledge_id from KNOWLEDGE_DOCUMENTS
    - Return True on success, False if not found
    - _Requirements: 3.5_

  - [x] 4.6 Write property test for knowledge document persistence
    - **Property 3: Knowledge Document Persistence**
    - Test create → read returns equivalent document
    - Test all fields are preserved
    - **Validates: Requirements 3.1, 3.2, 3.3**


- [x] 5. Implement Audio File operations
  - [x] 5.1 Implement save_audio_metadata method
    - Write AudioMetadata to AUDIO_FILES collection using audio_id as document ID
    - Convert datetime to Firestore timestamp
    - Return saved AudioMetadata
    - _Requirements: 4.1, 4.2_

  - [x] 5.2 Implement get_audio_files method
    - Query AUDIO_FILES collection
    - Optionally filter by knowledge_id if provided
    - Convert each document to AudioMetadata
    - Return list of AudioMetadata
    - _Requirements: 4.3_

  - [x] 5.3 Implement get_audio_file method
    - Get document by audio_id from AUDIO_FILES
    - Return None if not found
    - Convert to AudioMetadata if exists
    - _Requirements: 4.3_

  - [x] 5.4 Implement delete_audio_file method
    - Delete document by audio_id from AUDIO_FILES
    - Return True on success, False if not found
    - _Requirements: 4.3_

- [x] 6. Implement Agent operations
  - [x] 6.1 Implement save_agent method
    - Write AgentResponse to AGENTS collection using agent_id as document ID
    - Convert AnswerStyle enum to string value
    - Convert datetime to Firestore timestamp
    - Return saved AgentResponse
    - _Requirements: 5.1, 5.2_

  - [x] 6.2 Implement get_agents method
    - Query AGENTS collection
    - Optionally filter by doctor_id if provided
    - Convert each document to AgentResponse
    - Return list of AgentResponse
    - _Requirements: 5.3_

  - [x] 6.3 Implement get_agent method
    - Get document by agent_id from AGENTS
    - Return None if not found
    - Convert to AgentResponse if exists
    - _Requirements: 5.3_

  - [x] 6.4 Implement delete_agent method
    - Delete document by agent_id from AGENTS
    - Return True on success, False if not found
    - _Requirements: 5.5_

- [x] 7. Implement Patient Session operations
  - [x] 7.1 Implement create_patient_session method
    - Write PatientSessionResponse to PATIENT_SESSIONS collection using session_id as document ID
    - Initialize empty messages array
    - Return saved PatientSessionResponse
    - _Requirements: 8.1, 8.2_

  - [x] 7.2 Implement get_patient_session method
    - Get document by session_id from PATIENT_SESSIONS
    - Return None if not found
    - Convert to PatientSessionResponse if exists
    - _Requirements: 8.4_

  - [x] 7.3 Implement add_session_message method
    - Get session document reference
    - Append message to messages array using array_union
    - Convert ConversationMessageSchema to dict
    - _Requirements: 8.3_

  - [x] 7.4 Implement get_session_messages method
    - Get session document by session_id
    - Extract messages array from document
    - Convert each message dict to ConversationMessageSchema
    - Return list of messages
    - _Requirements: 8.4_


- [x] 8. Implement Conversation operations
  - [x] 8.1 Implement save_conversation method
    - Write ConversationDetailSchema to CONVERSATIONS collection using conversation_id as document ID
    - Convert messages list to list of dicts
    - Convert datetime to Firestore timestamp
    - Return saved ConversationDetailSchema
    - _Requirements: 6.1, 6.2_

  - [x] 8.2 Implement get_conversation_logs method
    - Query CONVERSATIONS collection
    - Apply patient_id filter if provided (case-insensitive partial match)
    - Apply start_date filter if provided (created_at >= start_date)
    - Apply end_date filter if provided (created_at <= end_date)
    - Apply requires_attention filter if requires_attention_only is True
    - Convert each document to ConversationSummarySchema
    - Sort by created_at descending
    - Return list of summaries
    - _Requirements: 6.3, 6.5_

  - [x] 8.3 Implement get_conversation_detail method
    - Get document by conversation_id from CONVERSATIONS
    - Return None if not found
    - Convert to ConversationDetailSchema if exists
    - _Requirements: 6.4_

  - [x] 8.4 Write property test for conversation query filtering
    - **Property 4: Conversation Query Filtering**
    - Test filtering by patient_id returns only matching conversations
    - Test filtering by date range returns only conversations in range
    - Test filtering by requires_attention returns only flagged conversations
    - **Validates: Requirements 6.3, 6.5**

- [x] 9. Implement Dashboard Statistics
  - [x] 9.1 Implement get_dashboard_stats method
    - Count documents in KNOWLEDGE_DOCUMENTS collection
    - Count documents in AGENTS collection
    - Count documents in AUDIO_FILES collection
    - Query all collections for most recent created_at timestamp
    - Return DashboardStatsResponse with actual counts
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [x] 9.2 Write property test for dashboard statistics accuracy
    - **Property 5: Dashboard Statistics Accuracy**
    - Create known number of documents in each collection
    - Verify get_dashboard_stats returns exact counts
    - **Validates: Requirements 7.1, 7.2, 7.3**

## Phase 3: Testing and Validation

- [x] 10. Write interface compliance tests
  - [x] 10.1 Create tests/test_firestore_data_service_props.py
    - **Property 1: Interface Implementation Completeness**
    - Test FirestoreDataService has all DataServiceInterface methods
    - Test MockDataService has all DataServiceInterface methods
    - Test no NotImplementedError is raised when calling methods
    - **Validates: Requirements 1.1, 1.2**

  - [x] 10.2 Write factory singleton test
    - **Property 2: Factory Singleton Consistency**
    - Call get_data_service() multiple times
    - Verify same instance is returned (using `is` comparison)
    - **Validates: Requirements 2.4**

- [x] 11. Write delete operation tests
  - [x] 11.1 Write property test for delete completeness
    - **Property 6: Delete Operation Completeness**
    - Create document, verify exists
    - Delete document, verify get returns None
    - Test for all entity types: knowledge, audio, agent
    - **Validates: Requirements 3.5, 4.3, 5.5**

- [x] 12. Checkpoint - Verify all CRUD operations work
  - Start Firestore emulator with docker-compose
  - Run pytest tests/test_firestore_data_service_props.py
  - Verify all property tests pass
  - Test manual CRUD operations via API endpoints
  - Ask user if questions arise

## Phase 4: Integration and Documentation

- [x] 13. Update .env.example with new setting
  - [x] 13.1 Add USE_MOCK_DATA documentation
    - Add USE_MOCK_DATA=false to .env.example
    - Add comment explaining when to use mock vs Firestore
    - Document that emulator takes precedence over mock setting
    - _Requirements: 2.5_

- [ ] 14. Final integration testing
  - [ ] 14.1 Test complete workflow with Firestore
    - Start emulators with docker-compose
    - Create knowledge document via API
    - Verify document persists in Firestore
    - Create agent linked to knowledge
    - Create patient session
    - Save conversation
    - Query conversation logs with filters
    - Verify dashboard stats reflect actual data
    - Stop and restart emulators
    - Verify data persists across restarts
    - _Requirements: 3.1-3.5, 4.1-4.3, 5.1-5.5, 6.1-6.5, 7.1-7.4, 8.1-8.4_

- [x] 15. Final Checkpoint


  - Run full test suite with pytest
  - Verify all property tests pass
  - Verify API endpoints work with FirestoreDataService
  - Ensure MockDataService still works when USE_MOCK_DATA=true
  - Ask user if questions arise
