# Requirements Document

## Introduction

This specification defines the requirements for implementing real ElevenLabs Agent creation functionality in the ElevenDops medical assistant system. The feature enables doctors to create AI conversational agents that are linked to medical knowledge bases, configured with appropriate voice personalities and answer styles, and synchronized with the ElevenLabs platform. This replaces the current mock implementation with actual ElevenLabs API integration and Firestore persistence.

## Glossary

- **Agent**: A conversational AI assistant configured in ElevenLabs that can interact with patients using voice
- **ElevenLabs**: Third-party voice AI platform providing text-to-speech and conversational AI capabilities
- **Knowledge Base**: A collection of medical documents uploaded to ElevenLabs that agents can reference when answering questions
- **System Prompt**: Instructions that define the agent's behavior, personality, and response style
- **Answer Style**: Predefined personality templates (professional, friendly, educational) that determine how the agent communicates
- **Voice ID**: Unique identifier for a voice model in ElevenLabs
- **Firestore**: Google Cloud database used as the primary data store for the system
- **Sync Status**: State tracking for synchronization between local data and ElevenLabs (pending, syncing, completed, failed)

## Requirements

### Requirement 1

**User Story:** As a doctor, I want to create an AI agent with a specific answer style, so that patients receive responses that match my preferred communication approach.

#### Acceptance Criteria

1. WHEN a doctor selects an answer style (professional, friendly, or educational) THEN the System SHALL generate a corresponding system prompt in Traditional Chinese
2. WHEN the System generates a system prompt THEN the System SHALL include instructions for the agent to respond in Traditional Chinese
3. WHEN a doctor creates an agent with the professional style THEN the System SHALL configure the agent to provide accurate, objective, and formal responses
4. WHEN a doctor creates an agent with the friendly style THEN the System SHALL configure the agent to provide warm, approachable, and easy-to-understand responses
5. WHEN a doctor creates an agent with the educational style THEN the System SHALL configure the agent to focus on teaching and explaining medical information

### Requirement 2

**User Story:** As a doctor, I want to link knowledge base documents to my agent, so that the agent can answer patient questions based on my uploaded medical content.

#### Acceptance Criteria

1. WHEN a doctor selects knowledge documents during agent creation THEN the System SHALL retrieve the corresponding ElevenLabs document IDs from Firestore
2. WHEN the System creates an agent in ElevenLabs THEN the System SHALL include all selected knowledge base document IDs in the agent configuration
3. WHEN a knowledge document has not been synced to ElevenLabs (sync_status is not "completed") THEN the System SHALL exclude that document from the agent's knowledge base configuration
4. WHEN no knowledge documents are selected THEN the System SHALL create the agent without knowledge base references

### Requirement 3

**User Story:** As a doctor, I want to select a voice for my agent, so that patients hear responses in a voice that suits my practice.

#### Acceptance Criteria

1. WHEN a doctor selects a voice during agent creation THEN the System SHALL configure the ElevenLabs agent with the selected voice ID
2. WHEN the System creates an agent THEN the System SHALL validate that the voice ID exists before making the API call
3. WHEN the voice ID is invalid or missing THEN the System SHALL return a validation error before attempting agent creation

### Requirement 4

**User Story:** As a doctor, I want my agent configuration to be saved persistently, so that I can manage and use my agents across sessions.

#### Acceptance Criteria

1. WHEN the System successfully creates an agent in ElevenLabs THEN the System SHALL save the agent metadata to Firestore
2. WHEN saving agent metadata THEN the System SHALL store: agent_id, name, knowledge_ids, voice_id, answer_style, elevenlabs_agent_id, doctor_id, and created_at
3. WHEN the ElevenLabs API call succeeds but Firestore save fails THEN the System SHALL attempt to delete the created ElevenLabs agent to maintain consistency
4. WHEN retrieving agents THEN the System SHALL load agent data from Firestore instead of in-memory storage

### Requirement 5

**User Story:** As a doctor, I want to delete agents I no longer need, so that I can manage my agent inventory effectively.

#### Acceptance Criteria

1. WHEN a doctor requests agent deletion THEN the System SHALL delete the agent from ElevenLabs first
2. WHEN the ElevenLabs deletion succeeds THEN the System SHALL delete the agent record from Firestore
3. WHEN the ElevenLabs deletion fails THEN the System SHALL log the error and still attempt to delete the local Firestore record
4. WHEN the agent does not exist in Firestore THEN the System SHALL return a not-found response

### Requirement 6

**User Story:** As a system administrator, I want agent creation errors to be handled gracefully, so that the system remains stable and provides useful feedback.

#### Acceptance Criteria

1. WHEN the ElevenLabs API returns a rate limit error THEN the System SHALL retry the request with exponential backoff up to 3 attempts
2. WHEN the ElevenLabs API returns an authentication error THEN the System SHALL return an appropriate error message without retrying
3. WHEN the ElevenLabs API returns a validation error THEN the System SHALL return the specific validation error to the user
4. WHEN any agent operation fails THEN the System SHALL log the error with sufficient context for debugging

### Requirement 7

**User Story:** As a developer, I want the agent creation API to follow consistent patterns, so that the codebase remains maintainable.

#### Acceptance Criteria

1. WHEN the agent service is initialized THEN the System SHALL use dependency injection for the data service and ElevenLabs service
2. WHEN creating an agent THEN the System SHALL use the FirestoreDataService when configured for Firestore mode
3. WHEN the System serializes agent data for API responses THEN the System SHALL use the existing AgentResponse schema
4. WHEN the System serializes agent data for Firestore THEN the System SHALL convert enum values to strings
