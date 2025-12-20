# Implementation Plan

- [x] 1. Update System Prompt Templates

  - [x] 1.1 Add Traditional Chinese system prompt constants to AgentService
    - Define SYSTEM_PROMPTS dictionary with AnswerStyle enum keys
    - Include Traditional Chinese prompts for professional, friendly, and educational styles
    - Each prompt must include instruction to respond in Traditional Chinese
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  - [x] 1.2 Write property test for system prompt generation
    - **Property 1: System Prompt Language Consistency**
    - **Validates: Requirements 1.1, 1.2**

- [x] 2. Implement Knowledge Base Filtering Logic

  - [x] 2.1 Add method to filter synced knowledge documents
    - Create `_get_synced_knowledge_ids()` method in AgentService
    - Query knowledge documents by provided IDs
    - Filter to only include documents with sync_status == COMPLETED
    - Return list of elevenlabs_document_id values
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - [x] 2.2 Write property test for knowledge base filtering
    - **Property 2: Knowledge Base Filtering by Sync Status**
    - **Validates: Requirements 2.1, 2.2, 2.3**

- [x] 3. Update AgentService with Dependency Injection

  - [x] 3.1 Refactor AgentService constructor for dependency injection
    - Accept optional elevenlabs_service and data_service parameters
    - Use get_elevenlabs_service() and get_data_service() as defaults
    - Remove in-memory \_agents dictionary
    - _Requirements: 7.1, 7.2_
  - [x] 3.2 Update create_agent method to use Firestore
    - Generate system prompt from answer style
    - Filter knowledge IDs to synced documents only
    - Call ElevenLabs API to create agent
    - Save agent metadata to Firestore via data_service
    - Implement rollback on Firestore save failure
    - _Requirements: 4.1, 4.2, 4.3_
  - [x] 3.3 Write property test for voice ID passthrough
    - **Property 3: Voice ID Passthrough**
    - **Validates: Requirements 3.1**
  - [x] 3.4 Write property test for agent metadata persistence
    - **Property 4: Agent Metadata Persistence Completeness**
    - **Validates: Requirements 4.1, 4.2**

- [x] 4. Update Agent Retrieval Methods

  - [x] 4.1 Update get_agents to use FirestoreDataService
    - Replace in-memory lookup with data_service.get_agents()
    - Support optional doctor_id filtering
    - _Requirements: 4.4_
  - [x] 4.2 Add get_agent method for single agent retrieval
    - Implement data_service.get_agent() call
    - Return None if agent not found
    - _Requirements: 4.4_
  - [x] 4.3 Write property test for agent retrieval
    - **Property 5: Agent Retrieval from Firestore**
    - **Validates: Requirements 4.4**

- [x] 5. Implement Agent Deletion with ElevenLabs Sync

  - [x] 5.1 Update delete_agent method
    - Retrieve agent from Firestore first
    - Attempt ElevenLabs deletion using elevenlabs_agent_id
    - Delete from Firestore regardless of ElevenLabs result
    - Log errors but continue on ElevenLabs failure
    - Return false if agent not found in Firestore
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  - [x] 5.2 Write property test for deletion order
    - **Property 6: Deletion Order Consistency**
    - **Validates: Requirements 5.1, 5.2**

- [x] 6. Update ElevenLabsService Agent Creation

  - [x] 6.1 Refine create_agent method for correct API structure
    - Update conversation_config structure per ElevenLabs API docs
    - Include knowledge_base array in agent.prompt section
    - Set first_message in Traditional Chinese
    - Configure language as "zh" for Chinese
    - _Requirements: 2.2, 3.1_
  - [x] 6.2 Add voice ID validation
    - Validate voice_id is not empty before API call
    - Raise ElevenLabsAgentError for invalid voice ID
    - _Requirements: 3.2, 3.3_
  - [x] 6.3 Enhance error handling with retry logic
    - Use existing \_classify_error method for error classification
    - Apply @retry decorator for retryable errors
    - Return specific error messages for validation errors
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 7. Checkpoint - Ensure all tests pass

  - [x] Ensure all tests pass, ask the user if questions arise.

- [x] 8. Write Property Test for Enum Serialization

  - [x] 8.1 Write property test for Firestore enum serialization
    - **Property 7: Enum Serialization for Firestore**
    - **Validates: Requirements 7.4**

- [x] 9. Write Unit Tests for Error Scenarios

  - [x] 9.1 Write unit tests for error handling
    - Test rate limit retry behavior
    - Test authentication error handling
    - Test validation error propagation
    - Test rollback on Firestore failure
    - _Requirements: 6.1, 6.2, 6.3, 4.3_

- [x] 10. Final Checkpoint - Ensure all tests pass
  - [x] Ensure all tests pass, ask the user if questions arise.
