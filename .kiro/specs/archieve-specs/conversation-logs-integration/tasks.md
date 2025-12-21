# Implementation Plan

- [x] 1. Enhance Data Service for Conversation Queries
  - Create new methods in DataServiceInterface for conversation log operations
  - Implement Firestore queries for conversation retrieval with filtering and ordering
  - Add error handling and retry logic for database operations
  - _Requirements: 1.1, 1.4, 7.1_

- [x] 1.1 Implement conversation listing with ordering
  - Add `get_all_conversations()` method to DataServiceInterface
  - Implement Firestore query with descending creation date ordering
  - Support optional attention status filtering
  - _Requirements: 1.1, 2.1, 2.2_

- [x] 1.2 Write property test for conversation ordering
  - **Property 1: Conversation list ordering**
  - **Validates: Requirements 1.1**

- [x] 1.3 Implement conversation detail retrieval
  - Add `get_conversation_by_id()` method to DataServiceInterface
  - Add `get_conversation_messages()` method for message history
  - Handle missing conversation gracefully with appropriate error responses
  - _Requirements: 3.1, 3.4_

- [x] 1.4 Write property test for message history completeness
  - **Property 6: Message history completeness**
  - **Validates: Requirements 3.1**

- [x] 1.5 Implement conversation statistics queries
  - Add methods for conversation count, average duration, and attention percentage
  - Implement aggregation queries in Firestore
  - Filter out invalid duration data for statistics
  - _Requirements: 5.1, 5.2_

- [x] 1.6 Write property test for statistics calculation
  - **Property 12: Statistics calculation accuracy**
  - **Validates: Requirements 5.1**

- [x] 2. Create Analysis Service for Question Categorization
  - Implement question identification and categorization logic
  - Create main concerns extraction from patient messages
  - Add duration formatting utilities
  - _Requirements: 4.1, 4.2, 4.3, 5.3_

- [x] 2.1 Implement question categorization logic
  - Create `categorize_questions()` method to identify questions by question marks
  - Implement answered/unanswered logic based on agent response presence
  - Handle edge cases like multiple consecutive questions
  - _Requirements: 4.1, 6.2, 6.3_

- [x] 2.2 Write property test for question categorization
  - **Property 9: Question categorization accuracy**
  - **Validates: Requirements 4.1**

- [x] 2.3 Write property test for question identification
  - **Property 16: Question identification accuracy**
  - **Validates: Requirements 6.2**

- [x] 2.4 Implement main concerns extraction
  - Create `extract_main_concerns()` method to identify key topics from patient messages
  - Use simple keyword extraction or pattern matching for MVP
  - Return list of concern strings from patient message content
  - _Requirements: 4.3_

- [x] 2.5 Write property test for main concerns extraction
  - **Property 11: Main concerns extraction**
  - **Validates: Requirements 4.3**

- [x] 2.6 Implement duration formatting utility
  - Create `format_duration()` method to convert seconds to "Xm Ys" format
  - Handle edge cases like zero duration and very long durations
  - Ensure consistent formatting across all duration displays
  - _Requirements: 5.3_

- [x] 2.7 Write property test for duration formatting
  - **Property 14: Duration formatting consistency**
  - **Validates: Requirements 5.3**

- [x] 3. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Create Conversation Service for Business Logic
  - Implement high-level conversation operations using Data Service and Analysis Service
  - Add conversation filtering and sorting logic
  - Integrate automatic analysis for ended conversations
  - _Requirements: 2.3, 6.1, 6.4_

- [x] 4.1 Implement conversation listing with filtering
  - Create `get_conversations()` method with optional filter parameter
  - Support "attention" filter and "all" filter modes
  - Maintain ordering after filtering operations
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 4.2 Write property test for attention filter
  - **Property 3: Attention filter accuracy**
  - **Validates: Requirements 2.1**

- [x] 4.3 Write property test for filter ordering preservation
  - **Property 5: Filter ordering preservation**
  - **Validates: Requirements 2.3**

- [x] 4.4 Implement conversation details with analysis
  - Create `get_conversation_details()` method combining conversation and message data
  - Apply question analysis to generate answered/unanswered categorization
  - Format response with all required fields and proper message ordering
  - _Requirements: 3.2, 4.1, 4.2_

- [x] 4.5 Write property test for message ordering
  - **Property 7: Message chronological ordering**
  - **Validates: Requirements 3.2**

- [x] 4.6 Write property test for question count accuracy
  - **Property 10: Question count accuracy**
  - **Validates: Requirements 4.2**

- [x] 4.7 Implement conversation statistics aggregation
  - Create `get_conversation_statistics()` method combining multiple data sources
  - Calculate total conversations, average duration, and attention percentage
  - Handle empty conversation list gracefully
  - _Requirements: 5.1, 5.4_

- [x] 4.8 Write property test for valid duration filtering
  - **Property 13: Valid duration filtering**
  - **Validates: Requirements 5.2**

- [x] 4.9 Implement automatic conversation analysis
  - Create analysis trigger when patient sessions end
  - Persist analysis results to conversation record in Firestore
  - Ensure analysis is available immediately for doctor review
  - _Requirements: 6.1, 6.4_

- [x] 4.10 Write property test for analysis persistence
  - **Property 18: Analysis persistence**
  - **Validates: Requirements 6.4**

- [x] 5. Create Conversation API Routes
  - Implement REST endpoints for conversation log operations
  - Add proper error handling and HTTP status codes
  - Integrate with Conversation Service for business logic
  - _Requirements: 1.4, 3.4, 7.3, 7.4_

- [x] 5.1 Implement conversation listing endpoint
  - Create `GET /api/conversations` endpoint with optional filter query parameter
  - Return conversation summaries with all required fields
  - Handle empty results with appropriate response
  - _Requirements: 1.1, 1.2, 1.3, 2.4_

- [x] 5.2 Write property test for conversation record completeness
  - **Property 2: Conversation record completeness**
  - **Validates: Requirements 1.2**

- [x] 5.3 Implement conversation details endpoint
  - Create `GET /api/conversations/{id}` endpoint for detailed conversation view
  - Return complete conversation with messages and analysis
  - Handle missing conversations with 404 response
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 5.4 Write property test for audio availability indication
  - **Property 8: Audio availability indication**
  - **Validates: Requirements 3.3**

- [x] 5.5 Implement conversation statistics endpoint
  - Create `GET /api/conversations/statistics` endpoint for dashboard metrics
  - Return aggregated statistics with proper formatting
  - Handle edge cases like no conversations gracefully
  - _Requirements: 5.1, 5.4_

- [x] 5.6 Add comprehensive error handling
  - Implement retry logic for Firestore failures
  - Return appropriate HTTP status codes for different error types
  - Log errors without exposing internal details to clients
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 5.7 Write unit tests for error handling scenarios
  - Test Firestore connection failures return 503
  - Test missing conversations return 404
  - Test corrupted data handling with graceful degradation
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Update Frontend Conversation Logs Page
  - Connect existing UI to real backend API endpoints
  - Replace mock data with actual API calls
  - Add error handling and loading states
  - _Requirements: 1.3, 2.4, 4.4_

- [x] 7.1 Implement real conversation listing
  - Replace mock data service calls with backend API calls
  - Add loading states while fetching conversation data
  - Display real conversation summaries with all required fields
  - _Requirements: 1.1, 1.2_

- [x] 7.2 Implement conversation filtering
  - Connect filter controls to backend API with query parameters
  - Update UI to show filtered results and empty states
  - Maintain user-friendly filter interface
  - _Requirements: 2.1, 2.2, 2.4_

- [x] 7.3 Implement conversation details view
  - Connect conversation selection to backend details API
  - Display complete message history with proper formatting
  - Add audio playback controls for messages with audio data
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 7.4 Implement statistics dashboard
  - Connect statistics display to backend statistics API
  - Show real-time conversation metrics and percentages
  - Handle empty state when no conversations exist
  - _Requirements: 5.1, 5.4_

- [x] 7.5 Add comprehensive error handling to frontend
  - Display user-friendly error messages for API failures
  - Handle network errors and timeout scenarios gracefully
  - Provide retry options for failed operations
  - _Requirements: 1.4, 3.4, 7.3, 7.4_

- [x] 8. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.