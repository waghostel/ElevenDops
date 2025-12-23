# Requirements Document

## Introduction

This specification defines the requirements for connecting the Doctor Dashboard to real Firestore statistics. The Doctor Dashboard currently displays mock data and needs to be updated to show actual counts of documents, agents, audio files, and the most recent activity timestamp from the Firestore database. This feature is part of MVP1 Phase 3 and depends on the Firestore Data Service (Spec 2) being implemented.

## Glossary

- **Doctor_Dashboard**: The main overview page for doctors showing system statistics and quick monitoring capabilities
- **Firestore**: Google Cloud Firestore database serving as the primary data source for the system
- **Dashboard_Statistics**: Aggregated metrics including document count, agent count, audio count, and last activity timestamp
- **Last_Activity**: The timestamp of the most recent data modification across all collections (knowledge documents, agents, audio files, conversations)
- **Data_Service**: The backend service layer that abstracts database operations and provides a unified interface for data access

## Requirements

### Requirement 1

**User Story:** As a doctor, I want to see accurate document counts on my dashboard, so that I can understand how much medical knowledge has been uploaded to the system.

#### Acceptance Criteria

1. WHEN the Doctor_Dashboard loads THEN the system SHALL display the total count of knowledge documents from Firestore
2. WHEN a new knowledge document is created THEN the Dashboard_Statistics document_count SHALL reflect the updated total within 5 seconds of page refresh
3. WHEN a knowledge document is deleted THEN the Dashboard_Statistics document_count SHALL reflect the updated total within 5 seconds of page refresh

### Requirement 2

**User Story:** As a doctor, I want to see accurate agent counts on my dashboard, so that I can track how many AI assistants have been configured.

#### Acceptance Criteria

1. WHEN the Doctor_Dashboard loads THEN the system SHALL display the total count of agents from Firestore
2. WHEN a new agent is created THEN the Dashboard_Statistics agent_count SHALL reflect the updated total within 5 seconds of page refresh
3. WHEN an agent is deleted THEN the Dashboard_Statistics agent_count SHALL reflect the updated total within 5 seconds of page refresh

### Requirement 3

**User Story:** As a doctor, I want to see accurate audio file counts on my dashboard, so that I can monitor how many education audio files have been generated.

#### Acceptance Criteria

1. WHEN the Doctor_Dashboard loads THEN the system SHALL display the total count of audio files from Firestore
2. WHEN a new audio file is generated THEN the Dashboard_Statistics audio_count SHALL reflect the updated total within 5 seconds of page refresh
3. WHEN an audio file is deleted THEN the Dashboard_Statistics audio_count SHALL reflect the updated total within 5 seconds of page refresh

### Requirement 4

**User Story:** As a doctor, I want to see when the last system activity occurred, so that I can understand how recently the system has been used.

#### Acceptance Criteria

1. WHEN the Doctor_Dashboard loads THEN the system SHALL display the most recent activity timestamp from Firestore
2. WHEN calculating last activity THEN the system SHALL consider the most recent created_at timestamp across knowledge_documents, agents, audio_files, and conversations collections
3. WHEN no data exists in any collection THEN the system SHALL display the current timestamp as last_activity
4. WHEN displaying last_activity THEN the system SHALL format the timestamp as relative time (e.g., "Just now", "5m ago", "2h ago")

### Requirement 5

**User Story:** As a doctor, I want the dashboard to handle errors gracefully, so that I can still use the system even when data retrieval fails.

#### Acceptance Criteria

1. IF the Firestore query fails THEN the system SHALL display zero counts and current timestamp as fallback values
2. IF the Firestore query fails THEN the system SHALL log the error for debugging purposes
3. WHEN an error occurs THEN the system SHALL display a user-friendly error message indicating data could not be loaded
4. WHEN the backend is unreachable THEN the Doctor_Dashboard SHALL display a connection error message with a retry button

### Requirement 6

**User Story:** As a doctor, I want to manually refresh the dashboard statistics, so that I can see the latest data without reloading the entire page.

#### Acceptance Criteria

1. WHEN the doctor clicks the refresh button THEN the system SHALL fetch fresh statistics from Firestore
2. WHEN refreshing statistics THEN the system SHALL display a loading indicator
3. WHEN the refresh completes THEN the system SHALL update all metric cards with the new values
