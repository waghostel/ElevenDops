# Requirements Document

## Introduction

This specification defines the requirements for enabling real audio generation using ElevenLabs Text-to-Speech (TTS) API with Google Cloud Storage (GCS) persistence. The feature allows doctors to generate patient education audio materials from knowledge documents, with audio files stored persistently in GCS and metadata tracked in Firestore. This is a critical component of the ElevenDops medical assistant system that transforms written medical education content into accessible audio format for patients.

## Glossary

- **TTS (Text-to-Speech)**: Technology that converts written text into spoken audio using AI voice synthesis
- **ElevenLabs**: Third-party AI voice platform providing TTS and voice cloning services
- **GCS (Google Cloud Storage)**: Cloud storage service for persisting audio files
- **StorageService**: Backend service that handles file uploads to GCS (or fake-gcs-server in development)
- **FirestoreDataService**: Backend service that handles data persistence in Firestore
- **AudioService**: Backend service that orchestrates audio generation workflow
- **Voice**: A specific voice model in ElevenLabs identified by voice_id
- **Script**: Text content prepared for TTS conversion, typically derived from knowledge documents
- **AudioMetadata**: Data structure containing audio file information (ID, URL, duration, etc.)
- **Knowledge Document**: Medical education document uploaded by doctors

## Requirements

### Requirement 1

**User Story:** As a doctor, I want to generate audio from medical education scripts, so that patients can listen to health information instead of reading.

#### Acceptance Criteria

1. WHEN a doctor submits a script with a selected voice THEN the AudioService SHALL call ElevenLabs TTS API to generate audio bytes
2. WHEN ElevenLabs TTS API returns audio data THEN the AudioService SHALL upload the audio to StorageService
3. WHEN audio upload completes THEN the AudioService SHALL save audio metadata to Firestore via FirestoreDataService
4. WHEN audio generation succeeds THEN the system SHALL return AudioMetadata containing audio_id, audio_url, knowledge_id, voice_id, script, and created_at
5. IF ElevenLabs TTS API call fails THEN the system SHALL raise ElevenLabsTTSError with descriptive error message

### Requirement 2

**User Story:** As a doctor, I want to select from available ElevenLabs voices, so that I can choose the most appropriate voice for patient education.

#### Acceptance Criteria

1. WHEN a doctor requests available voices THEN the ElevenLabsService SHALL fetch voice list from ElevenLabs API
2. WHEN voices are fetched successfully THEN the system SHALL return a list of VoiceOption containing voice_id, name, description, and preview_url
3. IF ElevenLabs voice API call fails THEN the system SHALL raise ElevenLabsTTSError with descriptive error message
4. WHEN displaying voices THEN the frontend SHALL show voice name and provide preview audio playback

### Requirement 3

**User Story:** As a doctor, I want generated audio files to be persisted, so that I can access them later and patients can listen to them.

#### Acceptance Criteria

1. WHEN audio is generated THEN the StorageService SHALL upload audio bytes to GCS bucket with path "audio/{filename}"
2. WHEN audio is uploaded THEN the StorageService SHALL return a publicly accessible URL
3. WHEN audio metadata is saved THEN the FirestoreDataService SHALL store audio_id, knowledge_id, voice_id, script, audio_url, duration_seconds, and created_at
4. WHEN querying audio files by knowledge_id THEN the FirestoreDataService SHALL return all matching AudioMetadata records

### Requirement 4

**User Story:** As a doctor, I want to generate education scripts from knowledge documents, so that I have appropriate content for TTS conversion.

#### Acceptance Criteria

1. WHEN a doctor requests script generation THEN the AudioService SHALL generate a script based on the knowledge document
2. WHEN script is generated THEN the system SHALL return ScriptGenerateResponse containing script text, knowledge_id, and generated_at timestamp
3. WHEN script generation completes THEN the doctor SHALL be able to review and edit the script before audio generation

### Requirement 5

**User Story:** As a doctor, I want to view audio generation history for each knowledge document, so that I can manage and replay previously generated audio.

#### Acceptance Criteria

1. WHEN a doctor views a knowledge document THEN the frontend SHALL display a list of previously generated audio files
2. WHEN displaying audio history THEN the system SHALL show generation timestamp, voice used, and provide audio playback controls
3. WHEN audio files exist THEN the frontend SHALL allow inline audio playback using the stored audio_url

### Requirement 6

**User Story:** As a system administrator, I want audio generation to handle errors gracefully, so that the system remains stable and provides useful feedback.

#### Acceptance Criteria

1. IF ElevenLabs API returns rate limit error THEN the system SHALL return HTTP 502 with appropriate error message
2. IF StorageService upload fails THEN the system SHALL NOT save incomplete metadata to Firestore
3. IF audio generation fails THEN the system SHALL log the error with sufficient detail for debugging
4. WHEN an error occurs THEN the frontend SHALL display a user-friendly error message in English

