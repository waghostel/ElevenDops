# Implementation Plan

- [ ] 1. Set up data models and schemas
  - [ ] 1.1 Add agent-related Pydantic schemas to backend/models/schemas.py
    - Add AnswerStyle enum (professional, friendly, educational)
    - Add AgentCreateRequest model with validation
    - Add AgentResponse and AgentListResponse models
    - _Requirements: 1.1, 1.2, 1.3, 4.1, 6.1_
  - [ ] 1.2 Write property test for whitespace name validation
    - **Property 1: Whitespace-only names are rejected**
    - **Validates: Requirements 1.3**
  - [ ] 1.3 Add AgentConfig dataclass to streamlit_app/services/models.py
    - Mirror backend AgentResponse structure
    - _Requirements: 6.1_

- [ ] 2. Implement ElevenLabs agent service methods
  - [ ] 2.1 Add agent creation method to backend/services/elevenlabs_service.py
    - Implement create_agent() using ElevenLabs SDK
    - Handle system prompt and knowledge base configuration
    - _Requirements: 6.2_
  - [ ] 2.2 Add agent deletion method to backend/services/elevenlabs_service.py
    - Implement delete_agent() using ElevenLabs SDK
    - _Requirements: 5.2, 6.4_
  - [ ] 2.3 Add agent retrieval method to backend/services/elevenlabs_service.py
    - Implement get_agent() for verification
    - _Requirements: 5.1_

- [ ] 3. Implement agent service business logic
  - [ ] 3.1 Create backend/services/agent_service.py
    - Implement system prompt generation for each answer style
    - Implement create_agent() orchestration (validate → ElevenLabs → Firestore)
    - Implement get_agents() to list all agents
    - Implement delete_agent() with cleanup from both systems
    - _Requirements: 4.2, 4.3, 4.4, 6.1, 6.2, 6.3, 6.4_
  - [ ] 3.2 Write property test for answer style to prompt mapping
    - **Property 5: Answer style to prompt mapping**
    - **Validates: Requirements 4.2, 4.3, 4.4**
  - [ ] 3.3 Write property test for agent creation returns valid ID
    - **Property 2: Agent creation returns valid ID**
    - **Validates: Requirements 1.4**

- [ ] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement backend API routes
  - [ ] 5.1 Create backend/api/routes/agent.py
    - POST /api/agent - Create new agent
    - GET /api/agent - List all agents
    - DELETE /api/agent/{agent_id} - Delete agent
    - _Requirements: 7.3_
  - [ ] 5.2 Register agent routes in backend/main.py
    - Add router to FastAPI app
    - _Requirements: 7.3_
  - [ ] 5.3 Write property test for knowledge document association
    - **Property 3: Knowledge document association persistence**
    - **Validates: Requirements 2.2, 2.4**
  - [ ] 5.4 Write property test for voice selection persistence
    - **Property 4: Voice selection persistence**
    - **Validates: Requirements 3.2**

- [ ] 6. Implement frontend API client methods
  - [ ] 6.1 Add agent methods to streamlit_app/services/backend_api.py
    - Implement create_agent() async method
    - Implement get_agents() async method
    - Implement delete_agent() async method
    - _Requirements: 7.1, 7.2_

- [ ] 7. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement Streamlit Agent Setup page
  - [ ] 8.1 Create streamlit_app/pages/4_Agent_Setup.py
    - Implement page header and layout
    - Implement agent creation form (name, knowledge selection, voice, style)
    - Implement voice preview functionality
    - Implement existing agents list with delete buttons
    - Implement error handling and loading states
    - _Requirements: 1.1, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 4.1, 5.1, 5.2, 5.3, 5.4_
  - [ ] 8.2 Write property test for agent deletion
    - **Property 6: Agent deletion removes from storage**
    - **Validates: Requirements 5.2, 6.4**
  - [ ] 8.3 Write property test for metadata completeness
    - **Property 7: Agent creation stores all metadata**
    - **Validates: Requirements 6.1**

- [ ] 9. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
