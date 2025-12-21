# Requirements Document

## Introduction

This specification defines the Patient Conversation (Text Mode) feature for the ElevenDops medical assistant system. The feature enables text-based patient conversations with AI agents, where patients input questions via text and receive audio responses generated through ElevenLabs TTS. This is a Phase 1 implementation that focuses on text input only (no voice input), with audio output for agent responses.

The feature integrates with ElevenLabs Conversational AI for intelligent responses and TTS for audio generation, while storing all conversation data in Firestore for doctor review.

## Glossary

- **Patient_Conversation_System**: The backend service responsible for managing patient conversation sessions, processing messages, and generating responses
- **Session**: A conversation instance between a patient and an AI agent, identified by a unique session_id
- **Agent**: An ElevenLabs Conversational AI agent configured with medical knowledge and voice settings
- **TTS (Text-to-Speech)**: ElevenLabs service that converts text responses into audio
- **Firestore**: Google Cloud database used as the primary data store for conversation records
- **Signed_URL**: A time-limited authenticated URL for secure WebSocket connections to ElevenLabs
- **Conversation_Message**: A single message exchange containing role (patient/agent), content, timestamp, and optional audio data

## Requirements

### Requirement 1

**User Story:** As a patient, I want to start a conversation session with an AI medical assistant, so that I can ask questions about my health condition.

#### Acceptance Criteria

1. WHEN a patient provides a valid patient_id and agent_id THEN the Patient_Conversation_System SHALL create a new session with a unique session_id
2. WHEN a session is created THEN the Patient_Conversation_System SHALL request a signed URL from ElevenLabs for secure communication
3. WHEN a session is created THEN the Patient_Conversation_System SHALL persist the session data to Firestore with patient_id, agent_id, session_id, and created_at timestamp
4. IF the ElevenLabs signed URL request fails THEN the Patient_Conversation_System SHALL return an error response with appropriate error details

### Requirement 2

**User Story:** As a patient, I want to send text messages to the AI assistant and receive audio responses, so that I can get answers to my medical questions in a natural voice.

#### Acceptance Criteria

1. WHEN a patient sends a text message in an active session THEN the Patient_Conversation_System SHALL forward the message to the ElevenLabs Conversational AI
2. WHEN the ElevenLabs agent generates a text response THEN the Patient_Conversation_System SHALL convert the response to audio using ElevenLabs TTS
3. WHEN a response is generated THEN the Patient_Conversation_System SHALL return both the text response and base64-encoded audio data to the patient
4. WHEN a message exchange occurs THEN the Patient_Conversation_System SHALL store both patient message and agent response in Firestore
5. IF the session_id is invalid or expired THEN the Patient_Conversation_System SHALL return a 404 error with session not found message

### Requirement 3

**User Story:** As a patient, I want to end my conversation session, so that my questions are saved for doctor review.

#### Acceptance Criteria

1. WHEN a patient ends a session THEN the Patient_Conversation_System SHALL analyze the conversation to identify answered and unanswered questions
2. WHEN a session ends THEN the Patient_Conversation_System SHALL calculate the conversation duration in seconds
3. WHEN a session ends THEN the Patient_Conversation_System SHALL persist the complete conversation log to Firestore with all messages, analysis results, and metadata
4. WHEN a session ends THEN the Patient_Conversation_System SHALL return a summary containing session_id, patient_id, duration, and message_count

### Requirement 4

**User Story:** As a doctor, I want patient conversations to be stored with analysis data, so that I can review patient concerns before appointments.

#### Acceptance Criteria

1. WHEN a conversation is stored THEN the Patient_Conversation_System SHALL include a requires_attention flag based on unanswered questions
2. WHEN a conversation is stored THEN the Patient_Conversation_System SHALL categorize questions as answered or unanswered based on agent response presence
3. WHEN a conversation is stored THEN the Patient_Conversation_System SHALL preserve the complete message history with timestamps and roles

### Requirement 5

**User Story:** As a patient, I want to see my conversation history during the session, so that I can follow the discussion context.

#### Acceptance Criteria

1. WHEN a message is sent THEN the Patient_Conversation_System SHALL return the response with a timestamp
2. WHEN displaying conversation history THEN the Frontend SHALL show messages with role indicators (patient/agent) and timestamps
3. WHEN an audio response is available THEN the Frontend SHALL provide audio playback controls for the agent response

### Requirement 6

**User Story:** As a system administrator, I want the conversation system to handle errors gracefully, so that patients have a reliable experience.

#### Acceptance Criteria

1. IF the ElevenLabs TTS service fails THEN the Patient_Conversation_System SHALL return the text response without audio and log the error
2. IF the Firestore write operation fails THEN the Patient_Conversation_System SHALL retry the operation and log the failure
3. WHEN an unexpected error occurs THEN the Patient_Conversation_System SHALL return a 500 error with a generic error message without exposing internal details
