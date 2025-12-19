# Requirements Document

## Introduction

This document specifies the requirements for the Agent Setup page (4_Agent_Setup.py) in the ElevenDops medical assistant system. The Agent Setup page enables doctors to create and configure AI agents that will interact with patients, linking them to knowledge bases and customizing their behavior through voice selection and answer style settings.

## Glossary

- **Agent**: An ElevenLabs Conversational AI entity configured with a system prompt, knowledge base, and voice settings to interact with patients
- **Knowledge Base**: A collection of medical documents uploaded by doctors that the agent references when answering patient questions
- **Voice Model**: An ElevenLabs voice configuration used for text-to-speech output
- **Answer Style**: A predefined personality/tone configuration for the agent (professional, friendly, or educational)
- **System Prompt**: Instructions that define how the agent should behave and respond
- **Backend API**: The FastAPI service that handles business logic and ElevenLabs API integration
- **Streamlit**: The frontend framework used for the MVP user interface

## Requirements

### Requirement 1

**User Story:** As a doctor, I want to create a new AI agent with a custom name, so that I can identify and manage multiple agents for different purposes.

#### Acceptance Criteria

1. WHEN a doctor enters an agent name and submits the form THEN the System SHALL create a new agent with the specified name
2. WHEN a doctor attempts to create an agent with an empty name THEN the System SHALL prevent creation and display a validation error
3. WHEN a doctor attempts to create an agent with a name containing only whitespace THEN the System SHALL prevent creation and display a validation error
4. WHEN an agent is successfully created THEN the System SHALL display the agent ID and a success message

### Requirement 2

**User Story:** As a doctor, I want to link knowledge documents to my agent, so that the agent can reference medical information when answering patient questions.

#### Acceptance Criteria

1. WHEN the agent setup page loads THEN the System SHALL display a list of available knowledge documents with checkboxes for selection
2. WHEN a doctor selects one or more knowledge documents THEN the System SHALL associate the selected documents with the agent configuration
3. WHEN no knowledge documents exist THEN the System SHALL display an informational message directing the doctor to upload documents first
4. WHEN an agent is created with linked documents THEN the System SHALL store the knowledge document IDs in the agent configuration

### Requirement 3

**User Story:** As a doctor, I want to select a voice for my agent, so that patients hear a consistent and appropriate voice during conversations.

#### Acceptance Criteria

1. WHEN the agent setup page loads THEN the System SHALL fetch and display available voices from ElevenLabs
2. WHEN a doctor selects a voice THEN the System SHALL include the voice ID in the agent configuration
3. WHERE a voice has a preview URL THEN the System SHALL provide an audio preview option
4. WHEN voice fetching fails THEN the System SHALL display an error message and allow retry

### Requirement 4

**User Story:** As a doctor, I want to choose an answer style for my agent, so that the agent's responses match the appropriate tone for my patients.

#### Acceptance Criteria

1. WHEN the agent setup page loads THEN the System SHALL display three answer style options: Professional, Friendly, and Educational
2. WHEN a doctor selects "Professional" style THEN the System SHALL configure the agent with a formal, accurate, and objective system prompt
3. WHEN a doctor selects "Friendly" style THEN the System SHALL configure the agent with a warm, approachable, and easy-to-understand system prompt
4. WHEN a doctor selects "Educational" style THEN the System SHALL configure the agent with an informative, teaching-focused system prompt

### Requirement 5

**User Story:** As a doctor, I want to view and manage my existing agents, so that I can update or delete agents as needed.

#### Acceptance Criteria

1. WHEN the agent setup page loads THEN the System SHALL display a list of existing agents with their names and creation dates
2. WHEN a doctor clicks delete on an agent THEN the System SHALL remove the agent from ElevenLabs and Firestore
3. WHEN an agent is deleted THEN the System SHALL update the agent list without requiring a page refresh
4. WHEN agent list fetching fails THEN the System SHALL display an error message and provide a refresh option

### Requirement 6

**User Story:** As a doctor, I want the agent configuration to be persisted to both Firestore and ElevenLabs, so that the agent is available for patient interactions.

#### Acceptance Criteria

1. WHEN an agent is created THEN the System SHALL store agent metadata in Firestore including agent_id, name, linked_knowledge_ids, voice_id, answer_style, and created_at
2. WHEN an agent is created THEN the System SHALL create the agent in ElevenLabs with the configured system prompt and knowledge base
3. IF agent creation in ElevenLabs fails THEN the System SHALL display an error message and not persist incomplete data to Firestore
4. WHEN an agent is deleted THEN the System SHALL remove the agent from both ElevenLabs and Firestore

### Requirement 7

**User Story:** As a developer, I want the Agent Setup page to follow the established architecture patterns, so that the codebase remains maintainable and consistent.

#### Acceptance Criteria

1. WHEN implementing the Agent Setup page THEN the Streamlit page SHALL only handle UI rendering and backend API calls
2. WHEN implementing agent operations THEN all ElevenLabs API calls SHALL be routed through the backend service layer
3. WHEN implementing the backend API THEN the System SHALL expose RESTful endpoints at /api/agent for agent operations
4. WHEN implementing data models THEN the System SHALL use Pydantic schemas for request/response validation
