# Requirements Document

## Introduction

The Conversation Logs Page (6_Conversation_Logs.py) is a Streamlit-based interface that enables doctors to review and analyze patient conversation history with AI agents. This page is a critical component of the ElevenDops system, providing doctors with insights into patient concerns before appointments.

Based on the user requirements document (Section 4.3), this feature allows doctors to:
1. View patient conversation summaries with filtering capabilities
2. Identify questions that were answered vs. unanswered by the AI
3. See which conversations require doctor attention
4. Review detailed conversation transcripts

This page follows the system's separation of concerns principle where Streamlit handles UI only, while all data retrieval and business logic are routed through the backend API.

## Glossary

- **Conversation_Logs_Page**: The Streamlit page component that provides the doctor-facing interface for reviewing patient conversations
- **Conversation_Summary**: A condensed view of a patient conversation including key metrics and extracted data
- **Patient_ID**: The unique identifier of the patient who had the conversation
- **Agent_ID**: The identifier of the AI agent that handled the conversation
- **Requires_Attention**: A boolean flag indicating if the conversation contains questions or concerns that need doctor follow-up
- **Answered_Question**: A patient question that the AI agent was able to address using its knowledge base
- **Unanswered_Question**: A patient question that the AI agent could not adequately answer, requiring doctor attention
- **Main_Concerns**: Key topics or issues extracted from the patient's questions during the conversation
- **Conversation_Transcript**: The complete record of messages exchanged between patient and agent
- **Backend_API**: The FastAPI service that handles all data retrieval and business logic

## Requirements

### Requirement 1

**User Story:** As a doctor, I want to see a list of patient conversations, so that I can review what patients have been asking about.

#### Acceptance Criteria

1. WHEN the Conversation_Logs_Page loads THEN the page SHALL display a title "對話記錄查詢" (Conversation Logs)
2. WHEN the page loads THEN the page SHALL fetch conversation summaries from the Backend_API
3. WHEN conversations exist THEN the page SHALL display a list of Conversation_Summary items
4. WHEN no conversations exist THEN the page SHALL display an informative message "目前沒有對話記錄" (No conversation logs available)
5. WHEN displaying each conversation THEN the page SHALL show: Patient_ID, conversation date/time, Agent name, and Requires_Attention status

### Requirement 2

**User Story:** As a doctor, I want to filter conversations by patient ID, so that I can focus on specific patients before their appointments.

#### Acceptance Criteria

1. WHEN the page loads THEN the page SHALL display a text input field for Patient_ID filtering
2. WHEN a doctor enters a Patient_ID filter THEN the page SHALL filter the conversation list to show only matching patients
3. WHEN the filter is cleared THEN the page SHALL display all conversations
4. WHEN no conversations match the filter THEN the page SHALL display "找不到符合條件的對話記錄" (No matching conversation logs found)

### Requirement 3

**User Story:** As a doctor, I want to filter conversations by date range, so that I can review recent patient interactions.

#### Acceptance Criteria

1. WHEN the page loads THEN the page SHALL display date picker inputs for start and end date filtering
2. WHEN a doctor selects a date range THEN the page SHALL filter conversations to show only those within the range
3. WHEN only start date is selected THEN the page SHALL show conversations from that date onwards
4. WHEN only end date is selected THEN the page SHALL show conversations up to that date
5. WHEN date filters are cleared THEN the page SHALL display all conversations

### Requirement 4

**User Story:** As a doctor, I want to quickly identify conversations that need my attention, so that I can prioritize patient concerns.

#### Acceptance Criteria

1. WHEN the page loads THEN the page SHALL display a checkbox filter "僅顯示需關注" (Show attention required only)
2. WHEN the attention filter is enabled THEN the page SHALL show only conversations where Requires_Attention is true
3. WHEN displaying conversations THEN the page SHALL visually highlight conversations that Require_Attention (e.g., warning icon or colored badge)
4. WHEN the page loads THEN the page SHALL display a summary count of conversations requiring attention

### Requirement 5

**User Story:** As a doctor, I want to see summary statistics, so that I can understand overall patient interaction patterns.

#### Acceptance Criteria

1. WHEN the page loads THEN the page SHALL display summary statistics in a metrics section
2. WHEN displaying statistics THEN the page SHALL show: total conversation count, attention required count, and total questions asked
3. WHEN filters are applied THEN the statistics SHALL update to reflect the filtered data
4. WHEN no data is available THEN the statistics SHALL display zero values

### Requirement 6

**User Story:** As a doctor, I want to view conversation details, so that I can understand the full context of patient questions.

#### Acceptance Criteria

1. WHEN a doctor clicks on a conversation summary THEN the page SHALL expand to show detailed information
2. WHEN showing details THEN the page SHALL display: Main_Concerns list, full Conversation_Transcript, and conversation duration
3. WHEN displaying the transcript THEN the page SHALL clearly distinguish between patient messages and agent responses
4. WHEN the conversation has audio THEN the page SHALL provide audio playback capability for agent responses

### Requirement 7

**User Story:** As a doctor, I want to see which questions were answered vs. unanswered, so that I can identify knowledge gaps.

#### Acceptance Criteria

1. WHEN viewing conversation details THEN the page SHALL categorize questions as Answered_Question or Unanswered_Question
2. WHEN displaying questions THEN the page SHALL visually distinguish answered (✓) from unanswered (✗) questions
3. WHEN unanswered questions exist THEN the page SHALL highlight them for doctor attention
4. WHEN viewing the summary THEN the page SHALL show counts of answered vs. unanswered questions

### Requirement 8

**User Story:** As a system, I want to handle errors gracefully, so that doctors have a reliable experience.

#### Acceptance Criteria

1. IF the Backend_API connection fails THEN the page SHALL display a user-friendly error message in Traditional Chinese
2. IF data loading fails THEN the page SHALL display "載入對話記錄時發生錯誤，請稍後再試" (Error loading conversation logs, please try again later)
3. WHEN any error occurs THEN the page SHALL log the error details for debugging without exposing technical details to the doctor
4. WHEN data is loading THEN the page SHALL display a loading indicator to provide feedback

## Non-Functional Requirements

### Performance
- The page SHALL load initial conversation list within 3 seconds
- Filter operations SHALL complete within 1 second
- Conversation detail expansion SHALL complete within 500ms

### Security
- The page SHALL only display conversations associated with the logged-in doctor (when authentication is implemented)
- Patient data SHALL be handled in compliance with medical data privacy requirements

### Usability
- All UI text SHALL be in Traditional Chinese (繁體中文)
- The page SHALL be responsive and work on desktop browsers
- Error messages SHALL be clear and actionable

## Dependencies

- Backend API endpoints for conversation data retrieval
- Data models for conversation summaries and transcripts
- Patient session data from 5_Patient_Test.py conversations
