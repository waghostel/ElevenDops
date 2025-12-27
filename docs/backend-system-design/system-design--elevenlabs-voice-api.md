# ElevenLabs Voice API System Architecture

## Architecture Overview

The following diagram illustrates the high-level architecture and component interactions for the ElevenLabs Voice API integration.

```mermaid
graph TB
    subgraph Frontend ["Streamlit Frontend"]
        EA["3_Education_Audio.py"]
        AS["4_Agent_Setup.py"]
    end

    subgraph BackendClient ["Backend API Client"]
        BAC["BackendAPIClient"]
    end

    subgraph FastAPIBackend ["FastAPI Backend"]
        AR["audio.py Router<br/>/api/audio/voices/list"]
        ASvc["AudioService"]
    end

    subgraph ExternalServices ["External Services"]
        ELS["ElevenLabsService"]
        ELAPI["ElevenLabs API<br/>voices.get_all()"]
    end

    subgraph Configuration ["Configuration Layer"]
        ENV[".env file<br/>ELEVENLABS_API_KEY"]
        Settings["get_settings()"]
    end

    EA -->|"get_available_voices()"| BAC
    AS -->|"get_cached_voices()"| BAC
    BAC -->|"GET /api/audio/voices/list"| AR
    AR -->|"Depends(get_audio_service)"| ASvc
    ASvc -->|"get_voices()"| ELS
    ELS -->|"client.voices.get_all()"| ELAPI

    ENV -.->|"loads"| Settings
    Settings -.->|"elevenlabs_api_key"| ELS

    style ELAPI fill:#ff6b6b,stroke:#c92a2a,color:white
    style ENV fill:#ffd43b,stroke:#fab005
```

## Service Interaction Flow

This sequence diagram details the request flow from the UI to the ElevenLabs API, including error propagation handling.

```mermaid
sequenceDiagram
    participant UI as Streamlit Frontend<br/>(3_Education_Audio.py)
    participant Client as BackendAPIClient<br/>(backend_api.py)
    participant Router as FastAPI Router<br/>(audio.py)
    participant AudioSvc as AudioService<br/>(audio_service.py)
    participant ElevenSvc as ElevenLabsService<br/>(elevenlabs_service.py)
    participant API as ElevenLabs API<br/>(External)

    UI->>Client: get_available_voices()
    Note over UI,Client: async call from load_voices_cached()

    Client->>Router: GET /api/audio/voices/list
    Note over Client,Router: HTTP request via httpx

    Router->>AudioSvc: get_available_voices()
    Note over Router,AudioSvc: Dependency injection

    AudioSvc->>ElevenSvc: get_voices()
    Note over AudioSvc,ElevenSvc: Delegates to ElevenLabs service

    ElevenSvc->>API: client.voices.get_all()
    Note over ElevenSvc,API: ElevenLabs SDK call

    alt API Error (e.g., 401 Unauthorized)
        API-->>ElevenSvc: ❌ 401 Unauthorized<br/>missing_permissions: voices_read
        Note over API,ElevenSvc: API Key lacks voices_read permission

        ElevenSvc-->>AudioSvc: raises ElevenLabsTTSError
        AudioSvc-->>Router: Exception propagates
        Router-->>Client: HTTP 502 Bad Gateway
        Client-->>UI: raises APIError(status_code=502)
        UI-->>UI: Shows error message
    else Success
        API-->>ElevenSvc: Returns List[Voice]
        ElevenSvc-->>AudioSvc: Returns List[Voice]
        AudioSvc-->>Router: Returns List[Voice]
        Router-->>Client: HTTP 200 OK (JSON)
        Client-->>UI: Returns List[Voice]
    end
```

## Configuration & Security

### Required Permissions

The ElevenLabs API Key requires specific permissions to function correctly with the backend services. Ensure the API key configured in `.env` has the following scopes:

| Feature                  | Required Permission       |
| ------------------------ | ------------------------- |
| List Voices              | `voices_read`             |
| Generate Audio (TTS)     | `audio_generation_create` |
| Sync Knowledge Documents | `knowledge_base_write`    |
| Create Agents            | `agent_create`            |
| Delete Agents            | `agent_delete`            |

### Environment Setup

The application looks for the API key in the `.env` file or environment variables:

```ini
ELEVENLABS_API_KEY=your_api_key_here
```

## Troubleshooting & Diagnostics

Use the following checkpoints to diagnose issues with the Voice API integration.

### Checkpoint 1: Verify API Key Presence

**Purpose**: Confirm the `ELEVENLABS_API_KEY` is loaded from the environment.

**Test Command** (PowerShell):

```powershell
# Check if the key is set in the environment
$env:ELEVENLABS_API_KEY
```

**Expected Result**: A non-empty API key string should be displayed.

### Checkpoint 2: Verify API Key Validity

**Purpose**: Confirm the API key is valid and not expired/revoked.

**Test Command** (PowerShell):

```powershell
# Test the API key directly with ElevenLabs
$headers = @{
    "xi-api-key" = $env:ELEVENLABS_API_KEY
}
Invoke-RestMethod -Uri "https://api.elevenlabs.io/v1/user" -Headers $headers
```

**Expected Result**: Returns user information JSON with subscription details.

### Checkpoint 3: Verify `voices_read` Permission

**Purpose**: Confirm the API key has the required `voices_read` permission.

**Test Command** (PowerShell):

```powershell
# Attempt to fetch voices directly
$headers = @{
    "xi-api-key" = $env:ELEVENLABS_API_KEY
}
try {
    Invoke-RestMethod -Uri "https://api.elevenlabs.io/v1/voices" -Headers $headers
} catch {
    $_.Exception.Response.StatusCode
    $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
    $reader.ReadToEnd()
}
```

**Expected Result**: Returns a list of available voices. If 401 Unauthorized is returned, check permissions.

### Checkpoint 4: Verify Backend Service Configuration

**Purpose**: Confirm the backend is correctly loading the API key and communicating with ElevenLabs.

**Test Command** (PowerShell):

```powershell
# Call the backend endpoint directly
Invoke-RestMethod -Uri "http://localhost:8000/api/audio/voices/list"
```

**Expected Result**: Returns a list of voice options in JSON format.
