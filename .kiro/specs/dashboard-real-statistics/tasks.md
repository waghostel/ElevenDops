# Implementation Plan

- [x] 1. Enhance FirestoreDataService dashboard statistics

  - [x] 1.1 Implement _get_last_activity_timestamp helper method

    - Add helper method to query most recent created_at across all collections
    - Query knowledge_documents, agents, audio_files, and conversations collections
    - Return maximum timestamp or current time if no data exists
    - _Requirements: 4.1, 4.2, 4.3_
  - [x] 1.2 Write property test for last activity calculation

    - **Property 4: Last activity is maximum timestamp**
    - **Validates: Requirements 4.1, 4.2, 4.3**
  - [x] 1.3 Update get_dashboard_stats to use enhanced last activity calculation

    - Replace current single-collection query with _get_last_activity_timestamp call
    - Ensure error handling wraps the new method
    - _Requirements: 4.1, 4.2_
  - [x] 1.4 Write property test for dashboard counts accuracy

    - **Property 1: Dashboard counts match collection sizes**
    - **Validates: Requirements 1.1, 2.1, 3.1**

- [x] 2. Verify data service factory configuration

  - [x] 2.1 Verify get_data_service returns FirestoreDataService when configured

    - Check USE_FIRESTORE_EMULATOR and USE_MOCK_DATA settings
    - Ensure dashboard API uses injected data service correctly
    - _Requirements: 1.1, 2.1, 3.1_
  - [x] 2.2 Write property test for count changes on creation

    - **Property 2: Count increases after creation**
    - **Validates: Requirements 1.2, 2.2, 3.2**
  - [x] 2.3 Write property test for count changes on deletion

    - **Property 3: Count decreases after deletion**
    - **Validates: Requirements 1.3, 2.3, 3.3**

- [x] 3. Enhance error handling and fallback behavior

  - [x] 3.1 Improve error logging in get_dashboard_stats

    - Add detailed error logging with collection context
    - Log which specific operation failed
    - _Requirements: 5.2_
  - [x] 3.2 Verify fallback response on Firestore failures

    - Ensure zero counts and current timestamp returned on error
    - Test error handling path
    - _Requirements: 5.1_
  - [x] 3.3 Write property test for error fallback

    - **Property 5: Error fallback returns valid response**
    - **Validates: Requirements 5.1**

- [x] 4. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Verify frontend integration


  - [x] 5.1 Verify Doctor Dashboard displays real statistics

    - Test with Firestore emulator running
    - Verify document, agent, and audio counts display correctly
    - Verify last activity timestamp displays in relative format
    - _Requirements: 1.1, 2.1, 3.1, 4.4_
  - [x] 5.2 Verify refresh button fetches fresh data

    - Click refresh and verify new API call is made
    - Verify metric cards update with new values
    - _Requirements: 6.1, 6.3_
  - [x] 5.3 Verify error handling displays correctly

    - Test with backend stopped to verify connection error message
    - Verify retry button is displayed
    - _Requirements: 5.3, 5.4_

- [x] 6. Final Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.
