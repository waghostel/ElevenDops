# Agent Setup Page Design Document

## Overview

The Agent Setup page enables doctors to create and manage AI agents for patient interactions. This feature integrates with ElevenLabs Conversational AI to create agents configured with medical knowledge bases, voice settings, and customized answer styles. The implementation follows the established ElevenDops architecture where Streamlit handles UI rendering while the FastAPI backend manages all business logic and external API integrations.

## Architecture

```mermaid
flowchart TB
    subgraph Frontend["Streamlit Frontend"]
        UI[4_Agent_Setup.py]
        API_Client[backend_api.py]
    end
    
    subgraph Backend["FastAPI Backend"]
        Routes[/api/agent routes]
        AgentService[agent_service.py]
        ElevenLabsService[elevenlabs_service.py]
    end
    
    subgraph External["External Services"]
        ElevenLabs[ElevenLabs API]
        Firestore[(Firestore)]
    end
    
    UI --> API_Client
    API_Client --> Routes
    Routes --> AgentService
    AgentService --> ElevenLabsService
    AgentService --> Firestore
    ElevenLabsService --> ElevenLabs
```

### Data Flow

1. Doctor interacts with Streamlit UI
2. UI calls BackendAPIClient methods
3. Backend API routes handle HTTP requests
4. AgentService orchestrates business logic
5. ElevenLabsService handles ElevenLabs API calls
6. Data persisted to Firestore with ElevenLabs agent_id reference

## Components and Interfaces

### Frontend Components

#### 4_Agent_Setup.py (Streamlit Page)
- Agent creation form with name, knowledge selection, voice, and style
- Existing agents list with delete functionality
- Voice preview audio player
- Error handling and loading states

#### BackendAPIClient Extensions
```python
# New methods to add to backend_api.py
async def create_agent(self, config: AgentCreateRequest) -> AgentResponse
async def get_agents(self) -> List[AgentResponse]
async def delete_agent(self, agent_id: str) -> bool
async def get_knowledge_documents_for_agent(self) -> List[KnowledgeDocument]
```

### Backend Components

#### API Routes (backend/api/routes/agent.py)
```python
POST /api/agent              # Create new agent
GET  /api/agent              # List all agents
GET  /api/agent/{agent_id}   # Get agent details
DELETE /api/agent/{agent_id} # Delete agent
```

#### AgentService (backend/services/agent_service.py)
Orchestrates agent operations:
- Validates input data
- Generates system prompts based on answer style
- Coordinates ElevenLabs agent creation
- Manages Firestore persistence
- Handles rollback on partial failures

#### ElevenLabsService Extensions
```python
# New methods to add to elevenlabs_service.py
def create_agent(self, name: str, system_prompt: str, 
                 knowledge_base_ids: List[str], voice_id: str) -> str
def delete_agent(self, agent_id: str) -> bool
def get_agent(self, agent_id: str) -> dict
```

## Data Models

### Request/Response Schemas (backend/models/schemas.py)

```python
class AnswerStyle(str, Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    EDUCATIONAL = "educational"

class AgentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    knowledge_ids: List[str] = Field(default_factory=list)
    voice_id: str = Field(...)
    answer_style: AnswerStyle = Field(...)
    doctor_id: str = Field(default="default_doctor")

class AgentResponse(BaseModel):
    agent_id: str
    name: str
    knowledge_ids: List[str]
    voice_id: str
    answer_style: AnswerStyle
    elevenlabs_agent_id: str
    doctor_id: str
    created_at: datetime

class AgentListResponse(BaseModel):
    agents: List[AgentResponse]
    total_count: int
```

### Frontend Models (streamlit_app/services/models.py)

```python
@dataclass
class AgentConfig:
    agent_id: str
    name: str
    knowledge_ids: List[str]
    voice_id: str
    answer_style: str
    elevenlabs_agent_id: str
    doctor_id: str
    created_at: datetime
```

### Firestore Document Structure

```
agents/{agent_id}
├── agent_id: string
├── name: string
├── knowledge_ids: array<string>
├── voice_id: string
├── answer_style: string
├── elevenlabs_agent_id: string
├── doctor_id: string
└── created_at: timestamp
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Whitespace-only names are rejected
*For any* string composed entirely of whitespace characters, attempting to create an agent with that name SHALL result in a validation error and no agent being created.
**Validates: Requirements 1.3**

### Property 2: Agent creation returns valid ID
*For any* valid agent configuration (non-empty name, valid voice_id, valid answer_style), creating an agent SHALL return a response containing a non-empty agent_id string.
**Validates: Requirements 1.4**

### Property 3: Knowledge document association persistence
*For any* set of knowledge document IDs provided during agent creation, the created agent's configuration SHALL contain exactly those document IDs.
**Validates: Requirements 2.2, 2.4**

### Property 4: Voice selection persistence
*For any* voice_id provided during agent creation, the created agent's configuration SHALL contain that exact voice_id.
**Validates: Requirements 3.2**

### Property 5: Answer style to prompt mapping
*For any* answer style (professional, friendly, educational), the system SHALL map it to a distinct, non-empty system prompt containing style-appropriate keywords.
**Validates: Requirements 4.2, 4.3, 4.4**

### Property 6: Agent deletion removes from storage
*For any* existing agent, after deletion, querying for that agent SHALL return a not-found result.
**Validates: Requirements 5.2, 6.4**

### Property 7: Agent creation stores all metadata
*For any* valid agent creation request, the stored agent SHALL contain all required fields: agent_id, name, knowledge_ids, voice_id, answer_style, doctor_id, and created_at.
**Validates: Requirements 6.1**

## Error Handling

### Validation Errors
- Empty or whitespace-only agent name: Return 422 with validation message
- Invalid answer style: Return 422 with allowed values
- Missing required fields: Return 422 with field details

### External Service Errors
- ElevenLabs API failure: Return 503 with retry suggestion
- Firestore connection failure: Return 503 with retry suggestion
- Partial creation failure: Rollback any created resources

### Error Response Format
```python
class AgentErrorResponse(BaseModel):
    detail: str
    error_code: str  # e.g., "AGENT_CREATION_FAILED", "ELEVENLABS_ERROR"
    retry_allowed: bool
```

## Testing Strategy

### Property-Based Testing Framework
- Use **Hypothesis** library for Python property-based testing
- Configure minimum 100 iterations per property test
- Tag each test with format: `**Feature: agent-setup-page, Property {number}: {property_text}**`

### Unit Tests
- Test AgentService business logic in isolation
- Test system prompt generation for each answer style
- Test validation functions for agent name and configuration
- Mock ElevenLabs and Firestore dependencies

### Property-Based Tests
Each correctness property will be implemented as a single property-based test:

1. **Whitespace validation property**: Generate random whitespace strings, verify rejection
2. **Agent ID property**: Generate valid configs, verify response contains ID
3. **Knowledge association property**: Generate random document ID lists, verify persistence
4. **Voice persistence property**: Generate random voice IDs, verify persistence
5. **Style mapping property**: Test all three styles, verify distinct prompts
6. **Deletion property**: Create then delete agents, verify removal
7. **Metadata completeness property**: Create agents, verify all fields present

### Integration Tests
- Test full flow from Streamlit UI to backend
- Test ElevenLabs API integration with real credentials (optional, CI-gated)
- Test Firestore persistence and retrieval

### Test File Structure
```
tests/
├── test_agent_service_props.py      # Property-based tests for agent service
├── test_agent_schemas_props.py      # Property-based tests for schemas
├── test_agent_api_props.py          # Property-based tests for API endpoints
└── test_agent_integration.py        # Integration tests
```
