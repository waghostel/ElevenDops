# Implementation Plan

- [x] 1. Enhance ElevenLabs Service for Conversational AI

  - [x] 1.1 Implement real signed URL retrieval from ElevenLabs API

    - Update `get_signed_url()` to call ElevenLabs `/v1/convai/conversation/get_signed_url` endpoint
    - Handle authentication and error responses
    - Return actual signed WebSocket URL instead of simulated one
    - _Requirements: 1.2, 1.4_

  - [x] 1.2 Implement real text message handling with ElevenLabs Conversational AI

    - Update `send_text_message()` to use ElevenLabs Conversational AI for generating responses
    - Integrate with agent's knowledge base for context-aware responses
    - Use agent's configured voice for TTS conversion
    - _Requirements: 2.1, 2.2_

  - [x] 1.3 Write property test for signed URL format

    - **Property 2: Session creation includes signed_url**
    - **Validates: Requirements 1.2**

  - [x] 1.4 Write property test for message response format

    - **Property 4: Message response contains text and audio**
    - **Validates: Requirements 2.2, 2.3**

- [x] 2. Implement Session Management in Patient Service

  - [x] 2.1 Enhance session creation with Firestore persistence

    - Ensure `create_session()` persists session data to Firestore via DataService
    - Include patient_id, agent_id, session_id, signed_url, and created_at

    - Handle ElevenLabs signed URL failures gracefully

    - _Requirements: 1.1, 1.3, 1.4_

  - [x] 2.2 Enhance message handling with Firestore persistence
    - Update `send_message()` to persist both patient and agent messages
    - Store message role, content, timestamp, and audio_data (for agent)
    - Validate session exists before processing message
    - _Requirements: 2.3, 2.4, 2.5_
  - [x] 2.3 Write property test for session creation uniqueness

    - **Property 1: Session creation returns unique session_id**
    - **Validates: Requirements 1.1**

  - [x] 2.4 Write property test for session data round-trip

    - **Property 3: Session data round-trip to Firestore**
    - **Validates: Requirements 1.3**

  - [x] 2.5 Write property test for message exchange round-trip

    - **Property 5: Message exchange round-trip to Firestore**

    - **Validates: Requirements 2.4**

  - [x] 2.6 Write property test for response timestamp
    - **Property 11: Response includes timestamp**
    - **Validates: Requirements 5.1**

- [x] 3. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement Conversation Analysis and End Session

  - [x] 4.1 Implement question categorization logic

    - Identify messages containing question marks as questions
    - Mark question as "answered" if immediately followed by agent response

    - Mark question as "unanswered" otherwise
    - _Requirements: 3.1, 4.2_

  - [x] 4.2 Implement requires_attention flag logic

    - Set requires_attention to true if unanswered_questions list is non-empty
    - _Requirements: 4.1_

  - [x] 4.3 Implement duration calculation

    - Calculate duration as difference between last and first message timestamps
    - Handle edge case of single message (duration = 0)
    - _Requirements: 3.2_

  - [x] 4.4 Implement end session with conversation log persistence

    - Persist complete conversation log to Firestore via ConversationService
    - Include all messages, analysis results, and metadata
    - Return summary with session_id, patient_id, duration, message_count
    - _Requirements: 3.3, 3.4, 4.3_

  - [x] 4.5 Write property test for question categorization

    - **Property 6: Question categorization correctness**
    - **Validates: Requirements 3.1, 4.2**

  - [x] 4.6 Write property test for requires_attention flag

    - **Property 7: Requires attention flag correctness**

    - **Validates: Requirements 4.1**

  - [x] 4.7 Write property test for duration calculation
    - **Property 8: Duration calculation correctness**
    - **Validates: Requirements 3.2**
  - [x] 4.8 Write property test for end session summary

    - **Property 9: End session summary completeness**

    - **Validates: Requirements 3.4**

  - [x] 4.9 Write property test for conversation log round-trip

    - **Property 10: Conversation log round-trip**
    - **Validates: Requirements 3.3, 4.3**

- [x] 5. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement Error Handling and Graceful Degradation

  - [x] 6.1 Implement TTS failure graceful degradation

    - Return text response without audio when TTS fails

    - Log TTS error for monitoring
    - _Requirements: 6.1_

  - [x] 6.2 Implement Firestore retry logic

    - Add retry mechanism for Firestore write operations
    - Log failures for monitoring

    - _Requirements: 6.2_

  - [x] 6.3 Implement generic error handling

    - Return 500 error with generic message for unexpected errors

    - Do not expose internal error details to client
    - _Requirements: 6.3_

  - [x] 6.4 Write unit tests for error handling scenarios

    - Test TTS failure returns text without audio

    - Test invalid session_id returns 404
    - Test generic errors return 500 without internal details

    - _Requirements: 6.1, 6.2, 6.3_

- [x] 7. Update Frontend Patient Test Page

  - [x] 7.1 Update conversation display with audio playback

    - Display messages with role indicators (patient/agent)
    - Show timestamps for each message
    - Add audio playback controls for agent responses with audio_data
    - _Requirements: 5.2, 5.3_

  - [x] 7.2 Improve error handling in frontend
    - Display user-friendly error messages
    - Handle connection failures gracefully
    - _Requirements: 6.3_

- [x] 8. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
