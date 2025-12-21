# MVP1 Architecture Overview

Comprehensive technical architecture documentation for ElevenDops MVP1.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                         │
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Doctor Portal   │  │  Patient Portal  │  │  Admin Dashboard │  │
│  │  (Streamlit)     │  │  (Streamlit)     │  │  (Streamlit)     │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  │
│           │                     │                     │             │
└───────────┼─────────────────────┼─────────────────────┼─────────────┘
            │                     │                     │
            └─────────────────────┼─────────────────────┘
                                  │ HTTP/REST
┌─────────────────────────────────▼─────────────────────────────────┐
│                      API Layer (FastAPI)                           │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  Knowledge   │  │    Audio     │  │    Agent     │             │
│  │   Routes     │  │   Routes     │  │   Routes     │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
│         │                 │                 │                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  Patient     │  │ Conversation │  │  Dashboard   │             │
│  │   Routes     │  │   Routes     │  │   Routes     │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
│         │                 │                 │                     │
└─────────┼─────────────────┼─────────────────┼─────────────────────┘
          │                 │                 │
┌─────────▼─────────────────▼─────────────────▼─────────────────────┐
│                    Service Layer (Python)                          │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  ElevenLabs Service                                          │ │
│  │  - Knowledge Base API                                        │ │
│  │  - Agents API                                                │ │
│  │  - Text-to-Speech API                                        │ │
│  │  - Conversational AI WebSocket                               │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Firestore Service                                           │ │
│  │  - CRUD operations                                           │ │
│  │  - Query operations                                          │ │
│  │  - Transaction management                                    │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Storage Service                                             │ │
│  │  - File upload/download                                      │ │
│  │  - GCS-compatible operations                                 │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Conversation Service                                        │ │
│  │  - Session management                                        │ │
│  │  - Message handling                                          │ │
│  │  - Analysis and logging                                      │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────┬──────────────────────┬──────────────────────┬────────────┘
          │                      │                      │
          ▼                      ▼                      ▼
    ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
    │  Firestore   │      │ ElevenLabs   │      │     GCS      │
    │  Emulator    │      │  Real API    │      │  Emulator    │
    │              │      │              │      │              │
    │ localhost:   │      │ api.eleven   │      │ localhost:   │
    │ 8080         │      │ labs.io      │      │ 4443         │
    └──────────────┘      └──────────────┘      └──────────────┘
```

## Component Breakdown

### 1. User Interface Layer (Streamlit)

#### Doctor Portal Pages
- **Doctor Dashboard** - System overview and statistics
- **Upload Knowledge** - Medical document management
- **Education Audio** - Audio generation and management
- **Agent Setup** - AI agent configuration
- **Conversation Logs** - Patient interaction review

#### Patient Portal Pages
- **Patient Test** - AI agent interaction interface
- **Education Audio** - Pre-recorded medical information

#### Responsibilities
- ✅ Render user interface
- ✅ Call backend APIs
- ✅ Display results and feedback
- ❌ No direct ElevenLabs API calls
- ❌ No direct Firestore operations
- ❌ No business logic

### 2. API Layer (FastAPI)

#### Route Modules
```
backend/api/
├── routes/
│   ├── knowledge.py      # Knowledge document endpoints
│   ├── audio.py          # Audio generation endpoints
│   ├── agent.py          # Agent management endpoints
│   ├── patient.py        # Patient conversation endpoints
│   ├── conversation.py   # Conversation logs endpoints
│   └── dashboard.py      # Dashboard statistics endpoints
└── models/
    ├── knowledge.py      # Knowledge Pydantic schemas
    ├── audio.py          # Audio Pydantic schemas
    ├── agent.py          # Agent Pydantic schemas
    └── conversation.py   # Conversation Pydantic schemas
```

#### Responsibilities
- ✅ Request validation
- ✅ Route handling
- ✅ Response formatting
- ✅ Error handling
- ✅ Call appropriate services

### 3. Service Layer (Python)

#### ElevenLabs Service
```python
# backend/services/elevenlabs_service.py

class ElevenLabsService:
    # Knowledge Base API
    - create_knowledge_document()
    - get_knowledge_documents()
    - delete_knowledge_document()
    
    # Agents API
    - create_agent()
    - update_agent()
    - get_agent()
    - delete_agent()
    
    # Text-to-Speech API
    - text_to_speech()
    - get_voices()
    
    # Conversational AI
    - start_conversation()
    - send_message()
    - get_response()
    - end_conversation()
```

#### Firestore Service
```python
# backend/services/firestore_service.py

class FirestoreService:
    # Knowledge operations
    - save_knowledge_document()
    - get_knowledge_documents()
    - get_knowledge_document()
    - delete_knowledge_document()
    
    # Audio operations
    - save_audio_metadata()
    - get_audio_files()
    - get_audio_file()
    
    # Agent operations
    - save_agent()
    - get_agents()
    - get_agent()
    - update_agent()
    - delete_agent()
    
    # Conversation operations
    - save_conversation()
    - get_conversations()
    - get_conversation()
    - save_message()
    - get_messages()
```

#### Storage Service
```python
# backend/services/storage_service.py

class StorageService:
    - upload_audio()
    - download_audio()
    - delete_audio()
    - get_audio_url()
    - ensure_bucket_exists()
```

#### Conversation Service
```python
# backend/services/conversation_service.py

class ConversationService:
    - start_conversation()
    - add_message()
    - get_conversation_history()
    - end_conversation()
    - analyze_conversation()
    - extract_concerns()
```

### 4. Data Layer

#### Firestore Emulator (MVP1)
- **Purpose**: Local persistent data storage
- **Port**: 8080
- **Collections**: knowledge_documents, audio_files, agents, conversations, messages

#### Firestore Production (MVP2)
- **Purpose**: Cloud persistent data storage
- **Project**: Google Cloud Firestore
- **Same collections** as emulator

#### GCS Emulator (MVP1)
- **Purpose**: Local file storage
- **Port**: 4443
- **Bucket**: elevenlabs-audio

#### GCS Production (MVP2)
- **Purpose**: Cloud file storage
- **Bucket**: production-bucket-name

### 5. External Services

#### ElevenLabs API
- **Knowledge Base API**: Document management
- **Agents API**: AI agent creation and configuration
- **Text-to-Speech API**: Audio generation
- **Conversational AI**: Real-time conversation handling

## Data Flow Patterns

### Pattern 1: Knowledge Upload Flow

```
User Input (Streamlit)
    ↓
POST /api/knowledge
    ↓
Knowledge Route Handler
    ├─ Validate request
    ├─ Call FirestoreService.save_knowledge_document()
    │   └─ Save to Firestore Emulator
    ├─ Call ElevenLabsService.create_knowledge_document()
    │   └─ Sync to ElevenLabs Knowledge Base
    └─ Update Firestore with elevenlabs_document_id
    ↓
Response to Streamlit
    ↓
Display Status to User
```

### Pattern 2: Audio Generation Flow

```
User Input (Streamlit)
    ↓
POST /api/audio
    ↓
Audio Route Handler
    ├─ Validate request
    ├─ Call ElevenLabsService.text_to_speech()
    │   └─ Generate audio from script
    ├─ Call StorageService.upload_audio()
    │   └─ Upload to GCS Emulator
    ├─ Call FirestoreService.save_audio_metadata()
    │   └─ Save metadata to Firestore
    └─ Return audio URL
    ↓
Response to Streamlit
    ↓
Display Audio Player to User
```

### Pattern 3: Patient Conversation Flow

```
User Input (Streamlit)
    ↓
POST /api/patient/conversation/start
    ├─ Create conversation in Firestore
    └─ Return conversation_id
    ↓
POST /api/patient/conversation/{id}/message
    ├─ Save user message to Firestore
    ├─ Call ElevenLabsService.send_message()
    │   └─ Get AI response
    ├─ Call ElevenLabsService.text_to_speech()
    │   └─ Generate audio response
    ├─ Call StorageService.upload_audio()
    │   └─ Upload response audio
    └─ Save response to Firestore
    ↓
GET /api/patient/conversation/{id}/response
    ├─ Retrieve response from Firestore
    └─ Return audio URL
    ↓
Response to Streamlit
    ↓
Display Audio Response to User
```

## Configuration Management

### Environment Variables

```python
# .env file
ELEVENLABS_API_KEY=sk_...

# Firestore Configuration
USE_FIRESTORE_EMULATOR=true
FIRESTORE_EMULATOR_HOST=localhost:8080
GOOGLE_CLOUD_PROJECT=elevenlabs-local

# GCS Configuration
USE_GCS_EMULATOR=true
GCS_EMULATOR_HOST=http://localhost:4443
GCS_BUCKET_NAME=elevenlabs-audio
```

### Settings Class

```python
# backend/config.py
class Settings:
    # Firestore
    USE_FIRESTORE_EMULATOR: bool
    FIRESTORE_EMULATOR_HOST: str
    GOOGLE_CLOUD_PROJECT: str
    
    # GCS
    USE_GCS_EMULATOR: bool
    GCS_EMULATOR_HOST: str
    GCS_BUCKET_NAME: str
    
    # ElevenLabs
    ELEVENLABS_API_KEY: str
```

## Error Handling Strategy

### Error Hierarchy

```
Exception
├── ValidationError
│   ├── InvalidDocumentFormat
│   ├── InvalidAgentConfig
│   └── InvalidConversationData
├── NotFoundError
│   ├── KnowledgeNotFound
│   ├── AgentNotFound
│   └── ConversationNotFound
├── ExternalServiceError
│   ├── ElevenLabsError
│   ├── FirestoreError
│   └── StorageError
└── InternalError
    └── UnexpectedError
```

### Error Response Format

```json
{
  "status": "error",
  "error": "ERROR_CODE",
  "message": "Human-readable message",
  "details": {
    "field": "error details"
  }
}
```

## Security Considerations

### MVP1 (No Authentication)
- All endpoints publicly accessible
- No user authentication
- No authorization checks
- Suitable for local development only

### MVP2 (With Authentication)
- Doctor authentication required
- Patient session tokens
- API key management
- Role-based access control

## Performance Considerations

### Caching Strategy
- Cache ElevenLabs voices list (rarely changes)
- Cache agent configurations (updated infrequently)
- No caching for real-time conversation data

### Database Indexing
- Index on `doctor_id` for doctor queries
- Index on `patient_id` for patient queries
- Index on `created_at` for time-based queries
- Composite index on `(doctor_id, created_at)`

### API Response Times
- Knowledge upload: < 2 seconds
- Audio generation: 5-30 seconds (depends on script length)
- Agent creation: < 5 seconds
- Conversation response: 2-10 seconds

## Scalability Considerations

### MVP1 Limitations
- Single instance deployment
- No load balancing
- No horizontal scaling
- Suitable for development/testing only

### MVP2 Improvements
- Cloud Run auto-scaling
- Load balancing
- Database replication
- CDN for audio files

## Testing Architecture

### Unit Tests
- Test individual service methods
- Mock external dependencies
- Test error handling

### Integration Tests
- Test API endpoints with real Firestore Emulator
- Test storage service with fake-gcs-server
- Test end-to-end workflows

### Property-Based Tests
- Use Hypothesis for data validation
- Test edge cases and boundary conditions

## Deployment Architecture

### MVP1 (Local Development)
```
Developer Machine
├── Streamlit (port 8501)
├── FastAPI (port 8000)
├── Firestore Emulator (port 8080)
└── GCS Emulator (port 4443)
```

### MVP2 (Cloud Deployment)
```
Google Cloud
├── Cloud Run (Streamlit + FastAPI)
├── Firestore (production database)
├── Cloud Storage (audio files)
└── Cloud Monitoring (logs and metrics)
```

## Technology Stack Rationale

| Component | Technology | Reason |
|-----------|-----------|--------|
| Frontend | Streamlit | Rapid MVP development, Python-native |
| Backend | FastAPI | High performance, async support, auto-docs |
| Database | Firestore | Serverless, real-time, easy scaling |
| Storage | GCS | Integrated with Google Cloud, CDN support |
| AI/Voice | ElevenLabs | Best-in-class voice AI, multilingual support |
| Language | Python | Rapid development, rich ecosystem |

## Future Architecture Improvements

### Phase 2
- Add authentication layer
- Implement caching layer (Redis)
- Add message queue (Cloud Tasks)
- Implement webhook system

### Phase 3
- Add analytics engine
- Implement real-time notifications
- Add advanced search capabilities
- Implement multi-tenancy

### Phase 4
- Add machine learning pipeline
- Implement advanced analytics
- Add recommendation engine
- Implement voice input support
