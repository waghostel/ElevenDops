# Implementation Plan

- [x] 1. Enhance AudioService with dependency injection and storage integration

  - [x] 1.1 Refactor AudioService constructor to accept injected dependencies

    - Add optional parameters for ElevenLabsService, StorageService, and FirestoreDataService
    - Initialize default instances if not provided
    - Remove in-memory `_AUDIO_STORE` list
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 1.2 Implement generate_audio method with storage persistence

    - Call ElevenLabsService.text_to_speech() to get audio bytes
    - Generate unique filename using UUID
    - Upload audio bytes to StorageService
    - Create AudioMetadata with returned URL
    - Save metadata to FirestoreDataService
    - Return AudioMetadata
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.1, 3.2, 3.3_

  - [x] 1.3 Write property test for audio generation metadata completeness

    - **Property 1: Audio generation produces complete metadata**
    - **Validates: Requirements 1.4**

  - [x] 1.4 Write property test for upload failure preventing metadata save
    - **Property 7: Upload failure prevents metadata persistence**
    - **Validates: Requirements 6.2**

- [x] 2. Implement audio file retrieval from Firestore

  - [x] 2.1 Update get_audio_files method to use FirestoreDataService

    - Replace in-memory query with FirestoreDataService.get_audio_files()
    - Handle async/sync conversion if needed
    - _Requirements: 3.4_

  - [x] 2.2 Write property test for audio query by knowledge_id
    - **Property 5: Audio query by knowledge_id returns all matching records**
    - **Validates: Requirements 3.4**

- [x] 3. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement voice list fetching

  - [x] 4.1 Verify get_available_voices method works correctly

    - Ensure ElevenLabsService.get_voices() is called
    - Map response to VoiceOption list
    - Handle errors appropriately
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 4.2 Write property test for voice list structure
    - **Property 2: Voice list contains required fields**
    - **Validates: Requirements 2.2**

- [x] 5. Implement script generation

  - [x] 5.1 Enhance generate_script method

    - Fetch knowledge document content from FirestoreDataService
    - Generate template-based script for MVP
    - Return formatted script text
    - _Requirements: 4.1, 4.2_

  - [x] 5.2 Write property test for script generation response
    - **Property 6: Script generation response structure**
    - **Validates: Requirements 4.1, 4.2**

- [x] 6. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Add storage URL validation

  - [x] 7.1 Verify StorageService returns valid URLs

    - Ensure URL format matches environment (emulator vs production)
    - _Requirements: 3.1, 3.2_

  - [x] 7.2 Write property test for storage URL format
    - **Property 3: Storage upload returns valid URL**
    - **Validates: Requirements 3.1, 3.2**

- [x] 8. Add audio metadata persistence verification
- [x] 8.1 Write property test for metadata round trip

  - **Property 4: Audio metadata persistence round trip**
  - **Validates: Requirements 3.3**

- [x] 9. Update frontend Education Audio page

  - [x] 9.1 Verify audio playback works with GCS URLs

    - Test audio playback with real URLs from storage
    - Ensure audio history displays correctly
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 9.2 Add error handling with English messages
    - Display user-friendly error messages in English
    - Handle API errors gracefully
    - _Requirements: 6.4_

- [x] 10. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
