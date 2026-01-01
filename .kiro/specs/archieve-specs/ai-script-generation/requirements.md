# Requirements Document

## Introduction

This feature enhances the Education Audio page with AI-powered script generation using LangGraph and Google Gemini models. The system will allow doctors to generate optimized voice scripts from knowledge documents, with customizable prompts and model selection. The generated scripts will follow ElevenLabs voice optimization best practices for natural-sounding patient education audio.

## Glossary

- **Script_Generator**: The backend service component that uses LangGraph and Gemini to generate voice-optimized scripts from knowledge documents
- **LLM_Selector**: The UI component that allows users to select which Gemini model to use for script generation
- **Prompt_Editor**: A popup dialog component that allows users to view and customize the script generation prompt
- **Default_Prompt**: The pre-configured system prompt optimized for generating ElevenLabs-compatible voice scripts
- **Knowledge_Document**: A medical education document stored in Firestore containing disease information
- **Voice_Script**: The generated text output optimized for text-to-speech conversion

## Requirements

### Requirement 1: LLM Model Selection

**User Story:** As a doctor, I want to select which Gemini model to use for script generation, so that I can balance between speed, cost, and quality based on my needs.

#### Acceptance Criteria

1. THE LLM_Selector SHALL display a dropdown in the Script Editor section with the following Gemini model options: Gemini 2.5 Pro, Gemini 2.5 Flash, Gemini 2.0 Flash
2. WHEN a user selects a model from the LLM_Selector, THE Script_Generator SHALL use that model for subsequent script generation requests
3. THE LLM_Selector SHALL persist the selected model in session state across page interactions
4. THE LLM_Selector SHALL default to Gemini 2.5 Flash as the initial selection

### Requirement 2: Customizable Prompt Editor

**User Story:** As a doctor, I want to customize the prompt used for script generation, so that I can tailor the output style to my specific patient communication needs.

#### Acceptance Criteria

1. WHEN a user clicks on the prompt edit button, THE Prompt_Editor SHALL display a popup dialog containing the current prompt text
2. THE Prompt_Editor SHALL allow users to edit the prompt text in a multi-line text area
3. WHEN a user clicks the reset button in the Prompt_Editor, THE Prompt_Editor SHALL restore the Default_Prompt
4. WHEN a user saves changes in the Prompt_Editor, THE Script_Generator SHALL use the customized prompt for subsequent generations
5. THE Prompt_Editor SHALL persist the customized prompt in session state
6. THE Default_Prompt SHALL include ElevenLabs voice optimization guidelines from the prompting guide

### Requirement 3: AI Script Generation with LangGraph

**User Story:** As a doctor, I want to generate voice-optimized scripts from my knowledge documents using AI, so that I can create professional patient education audio efficiently.

#### Acceptance Criteria

1. WHEN a user clicks the Generate Script button with a selected knowledge document, THE Script_Generator SHALL invoke the LangGraph workflow with the selected Gemini model
2. THE Script_Generator SHALL pass the knowledge document content and customized prompt to the LangGraph workflow
3. WHEN the LangGraph workflow completes successfully, THE Script_Generator SHALL return the generated script to the frontend
4. IF the LangGraph workflow fails, THEN THE Script_Generator SHALL return an appropriate error message
5. THE Script_Generator SHALL generate scripts optimized for ElevenLabs text-to-speech conversion
6. THE Script_Generator SHALL include proper pacing markers and natural speech patterns in generated scripts

### Requirement 4: Backend API Integration

**User Story:** As a system, I want to expose the AI script generation through a REST API, so that the frontend can request script generation with model and prompt parameters.

#### Acceptance Criteria

1. THE Backend SHALL expose a POST endpoint at `/api/audio/generate-script` that accepts knowledge_id, model_name, and custom_prompt parameters
2. WHEN the endpoint receives a request, THE Backend SHALL validate that the knowledge document exists
3. WHEN the endpoint receives a request, THE Backend SHALL invoke the Script_Generator service with the provided parameters
4. THE Backend SHALL return the generated script with metadata including model used and generation timestamp
5. IF the knowledge document is not found, THEN THE Backend SHALL return a 404 error response
6. IF the Gemini API call fails, THEN THE Backend SHALL return a 502 error response with error details

### Requirement 5: Default Prompt Configuration

**User Story:** As a system administrator, I want to provide a well-crafted default prompt, so that doctors can generate high-quality scripts without prompt engineering expertise.

#### Acceptance Criteria

1. THE Default_Prompt SHALL instruct the model to generate scripts suitable for voice synthesis
2. THE Default_Prompt SHALL include guidelines for natural speech patterns and pacing
3. THE Default_Prompt SHALL instruct the model to use clear, patient-friendly language
4. THE Default_Prompt SHALL be stored in a configuration file for easy maintenance
5. THE Default_Prompt SHALL include Traditional Chinese language support instructions
