# Requirements Document

## Introduction

This specification defines the Conversation Logs Integration feature for the ElevenDops medical assistant system. The feature connects the existing Conversation Logs page UI to real Firestore data, enabling doctors to view and analyze actual patient conversations. This is a Phase 2 implementation that builds upon the existing patient conversation functionality to provide comprehensive conversation analytics and doctor review capabilities.

The feature integrates with the existing conversation data stored in Firestore from patient sessions and provides analysis tools to help doctors understand patient concerns and identify questions requiring medical attention.

## Glossary

- **Conversation_Logs_System**: The backend service responsible for querying, analyzing, and presenting conversation data to doctors
- **Conversation_Record**: A complete conversation session between a patient and an AI agent, stored in Firestore
- **Question_Analysis**: The process of categorizing patient questions as answered or unanswered based on agent responses
- **Attention_Flag**: A boolean indicator that marks conversations requiring doctor review due to unanswered questions
- **Conversation_Summary**: An aggregated view of conversation data including patient concerns, question categories, and response quality
- **Doctor_Dashboard**: The frontend interface where doctors review patient conversation logs and analytics

## Requirements

### Requirement 1

**User Story:** As a doctor, I want to view a list of all patient conversations, so that I can monitor patient interactions with the AI assistant.

#### Acceptance Criteria

1. WHEN a doctor accesses the conversation logs page THEN the Conversation_Logs_System SHALL retrieve all conversation records from Firestore ordered by creation date descending
2. WHEN displaying conversation records THEN the Conversation_Logs_System SHALL show patient_id, agent_name, conversation duration, creation timestamp, and requires_attention flag
3. WHEN no conversations exist THEN the Conversation_Logs_System SHALL display an appropriate empty state message
4. WHEN Firestore query fails THEN the Conversation_Logs_System SHALL return an error response with appropriate error details

### Requirement 2

**User Story:** As a doctor, I want to filter conversations by attention status, so that I can prioritize reviewing conversations that need medical attention.

#### Acceptance Criteria

1. WHEN a doctor selects "Requires Attention" filter THEN the Conversation_Logs_System SHALL return only conversations where requires_attention is true
2. WHEN a doctor selects "All Conversations" filter THEN the Conversation_Logs_System SHALL return all conversation records regardless of attention status
3. WHEN applying filters THEN the Conversation_Logs_System SHALL maintain the descending creation date order
4. WHEN filter results are empty THEN the Conversation_Logs_System SHALL display an appropriate filtered empty state message

### Requirement 3

**User Story:** As a doctor, I want to view detailed conversation transcripts, so that I can understand the full context of patient interactions.

#### Acceptance Criteria

1. WHEN a doctor selects a conversation record THEN the Conversation_Logs_System SHALL retrieve the complete message history from Firestore
2. WHEN displaying conversation details THEN the Conversation_Logs_System SHALL show all messages with role indicators, content, and timestamps in chronological order
3. WHEN a message has audio_data THEN the Conversation_Logs_System SHALL provide audio playback controls for the agent response
4. WHEN conversation details cannot be retrieved THEN the Conversation_Logs_System SHALL display an error message without exposing internal details

### Requirement 4

**User Story:** As a doctor, I want to see analyzed question categories, so that I can quickly identify what patients are asking about.

#### Acceptance Criteria

1. WHEN displaying conversation analysis THEN the Conversation_Logs_System SHALL categorize questions as answered or unanswered based on agent response presence
2. WHEN displaying question analysis THEN the Conversation_Logs_System SHALL show the count of answered questions and unanswered questions
3. WHEN displaying main concerns THEN the Conversation_Logs_System SHALL extract and display the primary topics from patient messages
4. WHEN no questions are found THEN the Conversation_Logs_System SHALL indicate that the conversation contained no questions

### Requirement 5

**User Story:** As a doctor, I want to see conversation statistics, so that I can understand overall patient engagement patterns.

#### Acceptance Criteria

1. WHEN displaying conversation statistics THEN the Conversation_Logs_System SHALL calculate and show total conversations, average duration, and percentage requiring attention
2. WHEN calculating statistics THEN the Conversation_Logs_System SHALL include only completed conversations with valid duration data
3. WHEN displaying duration statistics THEN the Conversation_Logs_System SHALL format durations in human-readable format (minutes and seconds)
4. WHEN no conversations exist THEN the Conversation_Logs_System SHALL display zero values for all statistics

### Requirement 6

**User Story:** As a doctor, I want conversations to be automatically analyzed when patients end sessions, so that the analysis data is available immediately for review.

#### Acceptance Criteria

1. WHEN a patient session ends THEN the Conversation_Logs_System SHALL automatically analyze the conversation for answered and unanswered questions
2. WHEN analyzing conversations THEN the Conversation_Logs_System SHALL identify messages containing question marks as questions
3. WHEN analyzing conversations THEN the Conversation_Logs_System SHALL mark questions as answered if immediately followed by an agent response
4. WHEN analysis is complete THEN the Conversation_Logs_System SHALL update the conversation record in Firestore with analysis results

### Requirement 7

**User Story:** As a system administrator, I want the conversation logs system to handle data retrieval errors gracefully, so that doctors have a reliable review experience.

#### Acceptance Criteria

1. IF Firestore query operations fail THEN the Conversation_Logs_System SHALL retry the operation once and log the failure
2. IF conversation data is corrupted or incomplete THEN the Conversation_Logs_System SHALL display available data and indicate missing information
3. WHEN database connection issues occur THEN the Conversation_Logs_System SHALL return a 503 service unavailable error with retry guidance
4. WHEN unexpected errors occur THEN the Conversation_Logs_System SHALL return a 500 error with a generic error message without exposing internal details