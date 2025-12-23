# Implementation Plan: AI Script Generation

## Overview

This plan implements AI-powered script generation for the Education Audio page using LangGraph and Google Gemini models. Tasks are organized to build incrementally, starting with backend infrastructure, then frontend components, and finally integration.

## Tasks

- [ ] 1. Set up dependencies and configuration
  - [ ] 1.1 Add LangGraph and Google Generative AI dependencies to pyproject.toml
    - Add `langgraph`, `langchain-google-genai` packages
    - Add `GOOGLE_API_KEY` to .env.example
    - _Requirements: 3.1, 4.1_

  - [ ] 1.2 Create default prompt configuration file
    - Create `backend/config/default_script_prompt.txt` with ElevenLabs-optimized prompt
    - Include voice optimization guidelines, pacing markers, Traditional Chinese support
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ] 1.3 Add Gemini model configuration to backend config
    - Add `GEMINI_MODELS` dictionary with model name mappings
    - Add function to load default prompt from config file
    - _Requirements: 1.1, 5.4_

- [ ] 2. Implement backend script generation service
  - [ ] 2.1 Create LangGraph workflow for script generation
    - Create `backend/services/langgraph_workflow.py`
    - Implement `ScriptGenerationState` TypedDict
    - Implement `create_script_generation_graph()` with prepare_context, generate_script, post_process nodes
    - _Requirements: 3.1, 3.2, 3.5, 3.6_

  - [ ] 2.2 Write property test for Configuration Passthrough
    - **Property 2: Configuration Passthrough**
    - **Validates: Requirements 1.2, 2.4, 3.1, 3.2, 4.3**

  - [ ] 2.3 Create script generation service
    - Create `backend/services/script_generation_service.py`
    - Implement `ScriptGenerationService` class with `generate_script()` method
    - Integrate with LangGraph workflow and Firestore data service
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [ ] 2.4 Write property test for Successful Response Format
    - **Property 3: Successful Response Format**
    - **Validates: Requirements 3.3, 4.4**

  - [ ] 2.5 Write property test for Error Propagation
    - **Property 4: Error Propagation**
    - **Validates: Requirements 3.4, 4.6**

- [ ] 3. Checkpoint - Backend service tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Implement backend API endpoint
  - [ ] 4.1 Add request/response schemas for script generation
    - Add `ScriptGenerationRequest` and `ScriptGenerationResponse` to `backend/models/schemas.py`
    - _Requirements: 4.1, 4.4_

  - [ ] 4.2 Create API endpoint for script generation
    - Add POST `/api/audio/generate-script` endpoint to `backend/api/routes/audio.py`
    - Implement knowledge document validation
    - Integrate with ScriptGenerationService
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [ ] 4.3 Write property test for Document Validation
    - **Property 6: Document Validation**
    - **Validates: Requirements 4.2, 4.5**

- [ ] 5. Checkpoint - Backend API tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement frontend components
  - [ ] 6.1 Add backend API client method for script generation
    - Add `generate_script_with_ai()` method to `streamlit_app/services/backend_api.py`
    - _Requirements: 4.1_

  - [ ] 6.2 Implement LLM model selector dropdown
    - Add `render_llm_selector()` function to Education Audio page
    - Add session state for `selected_llm_model` with default "gemini-2.5-flash"
    - Display dropdown in Script Editor section
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [ ] 6.3 Write property test for Configuration Persistence
    - **Property 1: Configuration Persistence**
    - **Validates: Requirements 1.3, 2.5**

  - [ ] 6.4 Implement prompt editor popup
    - Add `render_prompt_editor()` function with popup dialog
    - Add session state for `custom_prompt` and `show_prompt_editor`
    - Implement edit text area and reset button
    - Load default prompt from backend or local config
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [ ] 6.5 Write property test for Prompt Reset Round-Trip
    - **Property 5: Prompt Reset Round-Trip**
    - **Validates: Requirements 2.3**

  - [ ] 6.6 Update generate script button to use AI generation
    - Modify `generate_script()` function to call new AI endpoint
    - Pass selected model and custom prompt to API
    - Display loading state and error handling
    - _Requirements: 3.1, 3.3, 3.4_

- [ ] 7. Checkpoint - Frontend integration tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Final integration and cleanup
  - [ ] 8.1 Add unit tests for UI components
    - Test LLM_Selector renders correct model options
    - Test Prompt_Editor popup behavior
    - Test default prompt content validation
    - _Requirements: 1.1, 2.1, 5.1, 5.2, 5.3, 5.5_

  - [ ] 8.2 Update .env.example with required environment variables
    - Add `GOOGLE_API_KEY` placeholder
    - _Requirements: 3.1_

- [ ] 9. Final checkpoint - All tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- All tasks including property tests are required for comprehensive coverage
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The LangGraph workflow uses a simple 3-node graph: prepare_context → generate_script → post_process
- Default prompt follows ElevenLabs prompting guide best practices for voice optimization
