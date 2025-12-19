# Requirements Document

## Introduction

The Patient Test Page (5_Patient_Test.py) is a Streamlit-based interface that allows patients to interact with AI medical assistants. This page serves as a validation and testing platform for the ElevenDops system, enabling patients to:
1. Identify themselves with a patient ID
2. Select a disease type/AI agent for consultation
3. Listen to pre-recorded educational audio
4. Engage in voice conversations with AI agents (text input with voice output in Phase 1)

The page follows the system's separation of concerns principle where Streamlit handles UI only, while all business logic and ElevenLabs API calls are routed through the backend.

## Glossary

- **Patient_Test_Page**: The Streamlit page component that provides the patient-facing interface for testing AI agent interactions
- **Patient_ID**: A unique identifier entered by the patient to track their session and conversation history
- **Agent**: An ElevenLabs Conversational AI assistant configured with medical knowledge and voice settings
- **Education_Audio**: Pre-recorded TTS audio files containing medical education content
- **Conversation_Session**: A real-time interaction session between a patient and an AI agent
- **Signed_URL**: A time-limited, secure URL for establishing WebSocket connections without exposing API keys
- **Backend_API**: The FastAPI service that handles all ElevenLabs API calls and business logic

## Requirements

### Requirement 1

**User Story:** As a patient, I want to enter my patient ID, so that my consultation session can be tracked and reviewed by my doctor.

#### Acceptance Criteria

1. WHEN the Patient_Test_Page loads THEN the Patient_Test_Page SHALL display a text input field for Patient_ID entry
2. WHEN a patient enters a Patient_ID THEN the Patient_Test_Page SHALL validate that the Patient_ID is non-empty and contains only alphanumeric characters
3. WHEN a patient submits an invalid Patient_ID THEN the Patient_Test_Page SHALL display an error message and prevent session start
4. WHEN a valid Patient_ID is submitted THEN the Patient_Test_Page SHALL store the Patient_ID in session state for the duration of the session

### Requirement 2

**User Story:** As a patient, I want to select a disease type or AI agent, so that I can receive relevant medical information and consultation.

#### Acceptance Criteria

1. WHEN a valid Patient_ID is entered THEN the Patient_Test_Page SHALL display a list of available agents fetched from the Backend_API
2. WHEN agents are displayed THEN the Patient_Test_Page SHALL show each agent's name and associated disease/knowledge area
3. WHEN no agents are available THEN the Patient_Test_Page SHALL display an informative message indicating no agents are configured
4. WHEN a patient selects an agent THEN the Patient_Test_Page SHALL store the selected agent information in session state

### Requirement 3

**User Story:** As a patient, I want to listen to educational audio about my condition, so that I can learn basic medical information before consulting the AI.

#### Acceptance Criteria

1. WHEN an agent is selected THEN the Patient_Test_Page SHALL fetch available education audio files associated with the agent's knowledge documents from the Backend_API
2. WHEN education audio files exist THEN the Patient_Test_Page SHALL display an audio player for each available file
3. WHEN no education audio files exist THEN the Patient_Test_Page SHALL display a message indicating no audio is available
4. WHEN a patient plays an audio file THEN the Patient_Test_Page SHALL use the native Streamlit audio component for playback

### Requirement 4

**User Story:** As a patient, I want to have a conversation with the AI agent, so that I can ask questions about my medical condition.

#### Acceptance Criteria

1. WHEN a patient initiates a conversation THEN the Patient_Test_Page SHALL request a signed URL from the Backend_API for secure WebSocket connection
2. WHEN a signed URL is obtained THEN the Patient_Test_Page SHALL establish a conversation session with the selected agent
3. WHEN the conversation is active THEN the Patient_Test_Page SHALL display a text input field for patient questions (Phase 1 limitation: text input only)
4. WHEN a patient submits a question THEN the Patient_Test_Page SHALL send the question to the agent and display the response
5. WHEN the agent responds THEN the Patient_Test_Page SHALL play the audio response using the Streamlit audio component

### Requirement 5

**User Story:** As a patient, I want to see my conversation history, so that I can review what was discussed during the session.

#### Acceptance Criteria

1. WHILE a conversation is active THEN the Patient_Test_Page SHALL display a scrollable conversation history showing all exchanges
2. WHEN a new message is sent or received THEN the Patient_Test_Page SHALL append the message to the conversation history display
3. WHEN displaying messages THEN the Patient_Test_Page SHALL clearly distinguish between patient questions and agent responses
4. WHEN the conversation ends THEN the Patient_Test_Page SHALL preserve the conversation history until the page is refreshed

### Requirement 6

**User Story:** As a patient, I want to end my conversation session, so that my consultation data can be saved for doctor review.

#### Acceptance Criteria

1. WHILE a conversation is active THEN the Patient_Test_Page SHALL display an "End Conversation" button
2. WHEN a patient clicks "End Conversation" THEN the Patient_Test_Page SHALL call the Backend_API to end the session and trigger data collection
3. WHEN the session ends successfully THEN the Patient_Test_Page SHALL display a confirmation message
4. WHEN the session ends THEN the Patient_Test_Page SHALL reset the conversation state while preserving the Patient_ID

### Requirement 7

**User Story:** As a system, I want to handle errors gracefully, so that patients have a smooth experience even when issues occur.

#### Acceptance Criteria

1. IF the Backend_API connection fails THEN the Patient_Test_Page SHALL display a user-friendly error message in Traditional Chinese
2. IF the conversation session fails to start THEN the Patient_Test_Page SHALL display an error and allow retry
3. IF a message fails to send THEN the Patient_Test_Page SHALL notify the patient and preserve the unsent message for retry
4. WHEN any error occurs THEN the Patient_Test_Page SHALL log the error details for debugging without exposing technical details to the patient
