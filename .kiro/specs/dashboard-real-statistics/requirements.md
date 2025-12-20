# Requirements Document

## Introduction

This specification defines the requirements for connecting the Doctor Dashboard to real Firestore statistics instead of mock data. The dashboard currently displays mock statistics including document count, agent count, audio count, and last activity timestamp. This feature will integrate with the Firestore data service to provide accurate, real-time statistics for doctors monitoring their ElevenDops system.

## Glossary

- **Dashboard**: The main monitoring interface for doctors showing system statistics
- **Firestore**: Google Cloud Firestore database service used for data persistence
- **MockDataService**: Current in-memory data service used for development
- **FirestoreDataService**: Production data service that connects to Firestore
- **Statistics**: Numerical metrics including counts and timestamps displayed on dashboard
- **Last Activity**: The most recent timestamp when any system activity occurred

## Requirements

### Requirement 1

**User Story:** As a doctor, I want to see accurate document counts on my dashboard, so that I can monitor how many medical documents I have uploaded to the system.

#### Acceptance Criteria

1. WHEN the dashboard loads THEN the system SHALL query Firestore to count knowledge documents
2. WHEN displaying document count THEN the system SHALL show the actual number of documents stored in Firestore
3. WHEN no documents exist THEN the system SHALL display zero as the document count
4. WHEN documents are filtered by doctor ID THEN the system SHALL count only documents belonging to that doctor

### Requirement 2

**User Story:** As a doctor, I want to see accurate agent counts on my dashboard, so that I can monitor how many AI agents I have configured.

#### Acceptance Criteria

1. WHEN the dashboard loads THEN the system SHALL query Firestore to count active agents
2. WHEN displaying agent count THEN the system SHALL show the actual number of agents stored in Firestore
3. WHEN no agents exist THEN the system SHALL display zero as the agent count
4. WHEN agents are filtered by doctor ID THEN the system SHALL count only agents belonging to that doctor

### Requirement 3

**User Story:** As a doctor, I want to see accurate audio file counts on my dashboard, so that I can monitor how many audio files have been generated.

#### Acceptance Criteria

1. WHEN the dashboard loads THEN the system SHALL query Firestore to count audio files
2. WHEN displaying audio count THEN the system SHALL show the actual number of audio files stored in Firestore
3. WHEN no audio files exist THEN the system SHALL display zero as the audio count
4. WHEN audio files are filtered by knowledge ID THEN the system SHALL count all audio files across all knowledge documents

### Requirement 4

**User Story:** As a doctor, I want to see the actual last activity timestamp on my dashboard, so that I can monitor when the system was last used.

#### Acceptance Criteria

1. WHEN the dashboard loads THEN the system SHALL calculate the most recent activity timestamp from Firestore
2. WHEN determining last activity THEN the system SHALL check creation timestamps across all collections
3. WHEN no activity exists THEN the system SHALL display the current timestamp as last activity
4. WHEN multiple activities exist THEN the system SHALL display the most recent timestamp

### Requirement 5

**User Story:** As a system administrator, I want the dashboard to use the FirestoreDataService instead of MockDataService, so that statistics reflect real data persistence.

#### Acceptance Criteria

1. WHEN the dashboard API is called THEN the system SHALL use FirestoreDataService for data queries
2. WHEN FirestoreDataService is unavailable THEN the system SHALL return appropriate error responses
3. WHEN switching from mock to real data THEN the system SHALL maintain the same API interface
4. WHEN Firestore emulator is configured THEN the system SHALL connect to the emulator for local development

### Requirement 6

**User Story:** As a developer, I want efficient Firestore queries for dashboard statistics, so that the dashboard loads quickly without impacting system performance.

#### Acceptance Criteria

1. WHEN querying document counts THEN the system SHALL use Firestore count queries instead of fetching all documents
2. WHEN querying agent counts THEN the system SHALL use Firestore count queries instead of fetching all agents
3. WHEN querying audio counts THEN the system SHALL use Firestore count queries instead of fetching all audio metadata
4. WHEN calculating last activity THEN the system SHALL use indexed timestamp queries for optimal performance