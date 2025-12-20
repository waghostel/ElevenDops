# Requirements Document

## Introduction

The Firestore Data Service specification replaces the existing MockDataService with a production-ready FirestoreDataService that works seamlessly with both the Firestore Emulator (local development) and production Cloud Firestore. This is a critical component that enables persistent data storage for the ElevenDops medical assistant system.

Based on the Phase 2 Implementation Roadmap (Spec 2), this specification:
1. Creates an abstract DataServiceInterface to define the contract for data operations
2. Implements FirestoreDataService that persists data to Firestore
3. Provides a factory function to switch between Mock and Firestore implementations based on configuration
4. Ensures zero code changes when transitioning from MVP1 (local emulator) to MVP2 (cloud production)

This specification depends on Spec 1 (Local Development Infrastructure Setup) which provides the Firestore Emulator and configuration system.

## Glossary

- **DataServiceInterface**: Abstract base class defining the contract for all data service implementations
- **FirestoreDataService**: Concrete implementation that persists data to Google Cloud Firestore
- **MockDataService**: Existing in-memory implementation used for testing and development without emulators
- **Factory_Function**: The `get_data_service()` function that returns the appropriate service implementation based on configuration
- **Collection**: A Firestore container for documents (similar to a database table)
- **Document**: A Firestore record containing fields and values
- **Subcollection**: A collection nested within a document
- **Timestamp**: Firestore's native datetime type for storing dates and times
- **Emulator_Mode**: Configuration state where the application connects to local Firestore Emulator
- **Production_Mode**: Configuration state where the application connects to Cloud Firestore

## Requirements

### Requirement 1

**User Story:** As a developer, I want an abstract DataServiceInterface, so that I can swap between Mock and Firestore implementations without changing application code.

#### Acceptance Criteria

1. WHEN the DataServiceInterface is defined THEN it SHALL include all methods currently in DataServiceProtocol
2. WHEN a class implements DataServiceInterface THEN it SHALL implement all abstract methods
3. WHEN application code uses DataServiceInterface THEN it SHALL work with both MockDataService and FirestoreDataService
4. WHEN a new method is added to DataServiceInterface THEN both implementations SHALL be updated to include it

### Requirement 2

**User Story:** As a developer, I want a factory function to get the appropriate data service, so that the correct implementation is used based on environment configuration.

#### Acceptance Criteria

1. WHEN USE_FIRESTORE_EMULATOR is true THEN get_data_service() SHALL return FirestoreDataService
2. WHEN USE_MOCK_DATA is true AND USE_FIRESTORE_EMULATOR is false THEN get_data_service() SHALL return MockDataService
3. WHEN in production mode THEN get_data_service() SHALL return FirestoreDataService
4. WHEN get_data_service() is called multiple times THEN it SHALL return the same singleton instance
5. WHEN configuration changes THEN the factory SHALL respect the new configuration on next application restart

### Requirement 3

**User Story:** As a doctor, I want my uploaded knowledge documents to persist in Firestore, so that they are available across application restarts.

#### Acceptance Criteria

1. WHEN a knowledge document is created THEN it SHALL be stored in the `/knowledge_documents/{doc_id}` collection
2. WHEN a knowledge document is stored THEN it SHALL include all fields: knowledge_id, doctor_id, disease_name, document_type, raw_content, sync_status, elevenlabs_document_id, structured_sections, created_at
3. WHEN knowledge documents are retrieved THEN they SHALL return all stored documents for the doctor
4. WHEN a knowledge document is updated THEN the changes SHALL persist in Firestore
5. WHEN a knowledge document is deleted THEN it SHALL be removed from Firestore

### Requirement 4

**User Story:** As a doctor, I want my generated audio files metadata to persist in Firestore, so that I can access them later.

#### Acceptance Criteria

1. WHEN an audio file is generated THEN its metadata SHALL be stored in the `/audio_files/{audio_id}` collection
2. WHEN audio metadata is stored THEN it SHALL include: audio_id, knowledge_id, voice_id, script, audio_url, duration_seconds, created_at
3. WHEN audio files are listed THEN they SHALL return all audio metadata for the doctor
4. WHEN an audio file is deleted THEN its metadata SHALL be removed from Firestore

### Requirement 5

**User Story:** As a doctor, I want my AI agents to persist in Firestore, so that patients can use them across sessions.

#### Acceptance Criteria

1. WHEN an agent is created THEN it SHALL be stored in the `/agents/{agent_id}` collection
2. WHEN an agent is stored THEN it SHALL include: agent_id, name, knowledge_ids, voice_id, answer_style, elevenlabs_agent_id, doctor_id, created_at
3. WHEN agents are listed THEN they SHALL return all agents for the doctor
4. WHEN an agent is updated THEN the changes SHALL persist in Firestore
5. WHEN an agent is deleted THEN it SHALL be removed from Firestore

### Requirement 6

**User Story:** As a doctor, I want patient conversations to persist in Firestore, so that I can review them later.

#### Acceptance Criteria

1. WHEN a conversation ends THEN it SHALL be stored in the `/conversations/{conversation_id}` collection
2. WHEN a conversation is stored THEN it SHALL include: conversation_id, patient_id, agent_id, agent_name, requires_attention, main_concerns, messages, answered_questions, unanswered_questions, duration_seconds, created_at
3. WHEN conversations are queried THEN they SHALL support filtering by patient_id, date range, and requires_attention flag
4. WHEN a conversation detail is requested THEN it SHALL return the full conversation with all messages
5. WHEN conversations are listed THEN they SHALL be sorted by created_at descending

### Requirement 7

**User Story:** As a doctor, I want the dashboard to show real statistics from Firestore, so that I can see accurate system status.

#### Acceptance Criteria

1. WHEN dashboard stats are requested THEN document_count SHALL reflect actual count in `/knowledge_documents` collection
2. WHEN dashboard stats are requested THEN agent_count SHALL reflect actual count in `/agents` collection
3. WHEN dashboard stats are requested THEN audio_count SHALL reflect actual count in `/audio_files` collection
4. WHEN dashboard stats are requested THEN last_activity SHALL reflect the most recent created_at timestamp across all collections

### Requirement 8

**User Story:** As a developer, I want patient sessions to persist in Firestore, so that conversation state is maintained.

#### Acceptance Criteria

1. WHEN a patient session is created THEN it SHALL be stored in the `/patient_sessions/{session_id}` collection
2. WHEN a session is stored THEN it SHALL include: session_id, patient_id, agent_id, signed_url, created_at
3. WHEN session messages are added THEN they SHALL be stored in the session document or subcollection
4. WHEN a session is retrieved THEN it SHALL return all session data including messages

### Requirement 9

**User Story:** As a developer, I want Firestore operations to handle errors gracefully, so that the application remains stable.

#### Acceptance Criteria

1. IF a Firestore write operation fails THEN the service SHALL raise an appropriate exception with error details
2. IF a Firestore read operation fails THEN the service SHALL log the error and return None or empty list as appropriate
3. IF the Firestore connection is lost THEN subsequent operations SHALL attempt to reconnect
4. IF a document is not found THEN the service SHALL return None instead of raising an exception

## Non-Functional Requirements

### Performance
- Firestore read operations SHALL complete within 500ms under normal conditions
- Firestore write operations SHALL complete within 1000ms under normal conditions
- Batch operations SHALL be used when operating on multiple documents

### Reliability
- All Firestore operations SHALL include proper error handling
- Failed operations SHALL be logged with sufficient detail for debugging
- The service SHALL gracefully handle Firestore emulator unavailability

### Compatibility
- FirestoreDataService SHALL implement the exact same interface as MockDataService
- All existing API endpoints SHALL work without modification
- Data models SHALL match the existing Pydantic schemas

### Maintainability
- Each Firestore collection SHALL have a dedicated helper method for CRUD operations
- Collection names SHALL be defined as constants
- Document field names SHALL match Pydantic model field names

## Dependencies

- Spec 1: Local Development Infrastructure Setup (provides Firestore Emulator and configuration)
- google-cloud-firestore Python package (already added in Spec 1)
- Existing backend/models/schemas.py (defines data models)
- Existing backend/config.py (provides Settings class)

## Technical Notes

### Firestore Collections Schema

```
/knowledge_documents/{doc_id}
  - knowledge_id: string
  - doctor_id: string
  - disease_name: string
  - document_type: string (enum: faq, post_care, precautions)
  - raw_content: string
  - sync_status: string (enum: pending, syncing, completed, failed)
  - elevenlabs_document_id: string | null
  - structured_sections: map | null
  - created_at: timestamp

/audio_files/{audio_id}
  - audio_id: string
  - knowledge_id: string
  - voice_id: string
  - script: string
  - audio_url: string
  - duration_seconds: number | null
  - created_at: timestamp

/agents/{agent_id}
  - agent_id: string
  - name: string
  - knowledge_ids: array<string>
  - voice_id: string
  - answer_style: string (enum: professional, friendly, educational)
  - elevenlabs_agent_id: string
  - doctor_id: string
  - created_at: timestamp

/conversations/{conversation_id}
  - conversation_id: string
  - patient_id: string
  - agent_id: string
  - agent_name: string
  - requires_attention: boolean
  - main_concerns: array<string>
  - messages: array<{role, content, timestamp, is_answered}>
  - answered_questions: array<string>
  - unanswered_questions: array<string>
  - duration_seconds: number
  - created_at: timestamp

/patient_sessions/{session_id}
  - session_id: string
  - patient_id: string
  - agent_id: string
  - signed_url: string
  - created_at: timestamp
  - messages: array<{role, content, timestamp, is_answered}> (optional subcollection)
```

### Firestore Client Initialization

The FirestoreDataService uses the FirestoreService from Spec 1 to get the Firestore client:

```python
from backend.services.firestore_service import get_firestore_service

class FirestoreDataService:
    def __init__(self):
        self._firestore = get_firestore_service()
        self._db = self._firestore.db
```

### Timestamp Handling

Firestore uses its own Timestamp type. Conversion between Python datetime and Firestore Timestamp:

```python
from google.cloud.firestore import SERVER_TIMESTAMP
from datetime import datetime

# Writing: use SERVER_TIMESTAMP for created_at
doc_data = {"created_at": SERVER_TIMESTAMP}

# Reading: Firestore returns datetime objects automatically
doc = doc_ref.get()
created_at: datetime = doc.to_dict()["created_at"]
```
