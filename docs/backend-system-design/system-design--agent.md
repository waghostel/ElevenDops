# Agent System Design

## Architecture Overview

The Agent System manages the lifecycle of AI medical assistants, bridging the local application with the ElevenLabs Conversational AI platform.

```mermaid
graph TB
    subgraph Client ["Frontend Client"]
        Msg[("Messages")]
    end

    subgraph Backend ["FastAPI Backend"]
        API["API Layer<br/>/api/agent"]
        Svc["AgentService"]
        DS["DataService<br/>(MongoDB/Firestore)"]
    end

    subgraph External ["External Services"]
        EL["ElevenLabs API"]
    end

    Client <--> API
    API --> Svc
    Svc -->|"Manages"| EL
    Svc <-->|"Persists"| DS
```

## Agent Creation Workflow

This sequence diagram illustrates the process of creating a new AI agent. Key steps include generating the system prompt, syncing knowledge base documents, and coordinating with the ElevenLabs API.

```mermaid
sequenceDiagram
    participant User
    participant API as API Layer
    participant Svc as AgentService
    participant DS as DataService
    participant EL as ElevenLabs API

    User->>API: POST /api/agent/create
    API->>Svc: create_agent(request)

    rect rgb(240, 248, 255)
        note right of Svc: 1. Preparation
        Svc->>Svc: _get_system_prompt(style)
        Svc->>DS: get_knowledge_document(ids)
        DS-->>Svc: documents
        Svc->>Svc: Filter synced documents
    end

    rect rgb(255, 250, 240)
        note right of Svc: 2. External Creation
        Svc->>EL: create_agent(name, prompt, ...)

        alt Success
            EL-->>Svc: elevenlabs_agent_id
        else Failure
            EL-->>Svc: Raise Error
            Svc-->>API: 500 Error
        end
    end

    rect rgb(240, 255, 240)
        note right of Svc: 3. Persistence
        Svc->>Svc: Create local Agent object
        Svc->>DS: save_agent(agent)

        alt Save Success
            DS-->>Svc: Success
            Svc-->>API: AgentResponse
            API-->>User: 200 OK (Agent Details)
        else Save Failure
            DS-->>Svc: Error
            note right of Svc: Rollback
            Svc->>EL: delete_agent(elevenlabs_id)
            Svc-->>API: 500 Error
        end
    end
```

## Data Model

The system maintains a local representation of the agent that maps to the external ElevenLabs entity.

### Agent Entity

| Field                 | Type       | Description                                       |
| --------------------- | ---------- | ------------------------------------------------- |
| `agent_id`            | UUID       | Local unique identifier                           |
| `elevenlabs_agent_id` | String     | External ID from ElevenLabs                       |
| `name`                | String     | Display name of the agent                         |
| `voice_id`            | String     | ID of the voice model used                        |
| `answer_style`        | Enum       | Personality (PROFESSIONAL, FRIENDLY, EDUCATIONAL) |
| `knowledge_ids`       | List[UUID] | IDs of associated local knowledge documents       |
| `doctor_id`           | String     | ID of the doctor who owns this agent              |

### System Prompts

The `AgentService` automatically injects a system prompt based on the selected `AnswerStyle`. This ensures consistent persona behavior (Professional, Friendly, or Educational).
