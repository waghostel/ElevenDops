# Requirements Document

## Introduction

This document specifies the requirements for the Education Audio page (3_Education_Audio.py) in the ElevenDops medical assistant system. The Education Audio feature enables doctors to generate standardized patient education audio files from uploaded knowledge documents. The workflow involves selecting knowledge content, generating a script preview via LLM, allowing doctor review and editing, and finally converting the approved script to speech using ElevenLabs Text-to-Speech API. This feature reduces repetitive explanations by doctors and provides patients with 24/7 accessible audio education resources.

## Glossary

- **Education Audio System**: The Streamlit page and backend services responsible for generating patient education audio files
- **Knowledge Document**: A previously uploaded medical document containing disease information, FAQs, or care instructions
- **Script**: A text document optimized for audio narration, generated from knowledge document content
- **TTS (Text-to-Speech)**: ElevenLabs service that converts text into natural-sounding speech
- **Voice Model**: A specific voice configuration in ElevenLabs used for audio generation
- **Audio Metadata**: Information about generated audio including URL, duration, voice ID, and creation timestamp
- **Backend API**: FastAPI service that handles business logic and ElevenLabs API integration

## Requirements

### Requirement 1: Knowledge Document Selection

**User Story:** As a doctor, I want to select from my uploaded knowledge documents, so that I can generate education audio based on existing medical content.

#### Acceptance Criteria

1. WHEN the Education Audio page loads, THE Education Audio System SHALL display a dropdown list of all available knowledge documents with their disease names and document types
2. WHEN a doctor selects a knowledge document, THE Education Audio System SHALL display the document's content preview in a read-only text area
3. WHEN no knowledge documents exist, THE Education Audio System SHALL display an informational message directing the doctor to upload documents first

### Requirement 2: Script Generation

**User Story:** As a doctor, I want to generate an audio-optimized script from my knowledge document, so that the resulting audio sounds natural and educational.

#### Acceptance Criteria

1. WHEN a doctor clicks the "Generate Script Preview" button with a selected document, THE Education Audio System SHALL send the document content to the backend for LLM-based script generation
2. WHEN script generation is in progress, THE Education Audio System SHALL display a loading indicator with appropriate status message
3. WHEN script generation completes successfully, THE Education Audio System SHALL display the generated script in an editable text area
4. IF script generation fails, THEN THE Education Audio System SHALL display an error message with the failure reason

### Requirement 3: Script Review and Editing

**User Story:** As a doctor, I want to review and edit the generated script before audio conversion, so that I can ensure medical accuracy and appropriate tone.

#### Acceptance Criteria

1. WHEN a script is displayed, THE Education Audio System SHALL provide an editable text area for doctor modifications
2. WHEN a doctor modifies the script, THE Education Audio System SHALL preserve the edited content for audio generation
3. WHEN a doctor clicks "Reset Script", THE Education Audio System SHALL restore the original generated script content

### Requirement 4: Voice Selection

**User Story:** As a doctor, I want to select a voice for the education audio, so that I can choose an appropriate voice style for my patients.

#### Acceptance Criteria

1. WHEN the Education Audio page loads, THE Education Audio System SHALL display a dropdown of available voice options
2. WHEN a doctor selects a voice, THE Education Audio System SHALL use that voice for subsequent audio generation

### Requirement 5: Audio Generation

**User Story:** As a doctor, I want to convert the approved script to audio, so that patients can listen to the education content.

#### Acceptance Criteria

1. WHEN a doctor clicks "Generate Audio" with a confirmed script, THE Education Audio System SHALL send the script to the backend for TTS conversion
2. WHEN audio generation is in progress, THE Education Audio System SHALL display a loading indicator with status message
3. WHEN audio generation completes successfully, THE Education Audio System SHALL display an audio player for playback
4. WHEN audio generation completes successfully, THE Education Audio System SHALL display the audio URL for reference
5. IF audio generation fails, THEN THE Education Audio System SHALL display an error message with the failure reason

### Requirement 6: Audio Playback and Management

**User Story:** As a doctor, I want to play back and manage generated audio files, so that I can verify quality and access previous recordings.

#### Acceptance Criteria

1. WHEN audio is available, THE Education Audio System SHALL provide standard playback controls (play, pause, seek)
2. WHEN the page loads, THE Education Audio System SHALL display a list of previously generated audio files for the selected knowledge document
3. WHEN a doctor selects a previous audio file, THE Education Audio System SHALL load it into the audio player

### Requirement 7: Backend API Integration

**User Story:** As a system architect, I want the Streamlit frontend to communicate with the backend API for all business logic, so that the system maintains proper separation of concerns.

#### Acceptance Criteria

1. WHEN generating scripts, THE Education Audio System SHALL call the backend API endpoint rather than directly invoking LLM services
2. WHEN generating audio, THE Education Audio System SHALL call the backend API endpoint rather than directly invoking ElevenLabs TTS API
3. WHEN fetching audio history, THE Education Audio System SHALL call the backend API endpoint to retrieve stored audio metadata

### Requirement 8: Medical Compliance

**User Story:** As a healthcare administrator, I want all education audio to require doctor confirmation before generation, so that the system complies with medical information standards.

#### Acceptance Criteria

1. WHEN a script is generated, THE Education Audio System SHALL require explicit doctor confirmation before enabling audio generation
2. WHEN a doctor confirms the script, THE Education Audio System SHALL enable the "Generate Audio" button
3. WHEN a doctor modifies the script after confirmation, THE Education Audio System SHALL require re-confirmation before audio generation
