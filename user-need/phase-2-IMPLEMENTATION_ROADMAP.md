# ElevenDops Implementation Roadmap

## Overview

This document outlines the remaining implementation specifications for the ElevenDops medical assistant system, organized by priority and milestone. The roadmap follows the Streamlit frontend + FastAPI backend architecture.

## Design Principle: Minimize Code Rewriting

To ensure smooth transition from MVP1 to MVP2, we use **cloud emulators locally** instead of different technologies:

| Component | MVP1 (Local) | MVP2 (Cloud) | Code Change |
|-----------|--------------|--------------|-------------|
| Database | Firestore Emulator | Firestore Production | Config only |
| File Storage | fake-gcs-server | Google Cloud Storage | Config only |
| ElevenLabs | Real API | Real API | None |

**Result**: Same application code works in both environments. Only connection strings change.

---

## Current Implementation Status

### ✅ Completed Features
- **Streamlit MVP Foundation** - Basic page structure and navigation
- **Upload Knowledge Page** - UI and backend API (mock data)
- **Education Audio Page** - UI and backend API (mock data)
- **Agent Setup Page** - UI and backend API (mock data)
- **Patient Test Page** - UI and backend API (mock data)
- **Conversation Logs Page** - UI and backend API (mock data)
- **Doctor Dashboard** - UI and backend API (mock data)

### 🔄 Current State
All pages are functional with **MockDataService**. The system can run locally but uses in-memory mock data instead of persistent storage.

---

## Milestone Definitions

### MVP1: Local Development Environment
**Goal**: Workable Streamlit dev pages for both doctor and patient, running locally with real ElevenLabs integration and local emulators.

**Infrastructure**:
- Firestore Emulator (data persistence)
- fake-gcs-server (audio file storage)
- Real ElevenLabs API

**Success Criteria**:
- Doctor can upload knowledge documents and sync to ElevenLabs
- Doctor can generate education audio using ElevenLabs TTS
- Doctor can create AI agents linked to knowledge bases
- Patient can have text-based conversations with AI agents
- Doctor can view conversation logs
- All data persists locally via emulators

### MVP2: Cloud Deployment
**Goal**: Workable Streamlit application deployed on Google Cloud Run.

**Infrastructure**:
- Firestore Production
- Google Cloud Storage
- Real ElevenLabs API

**Success Criteria**:
- Application runs on Cloud Run
- Data persists in Firestore
- Audio files stored in Google Cloud Storage
- Secure environment variable management
- Basic health monitoring

**Code Changes from MVP1**: Configuration only (connection strings)

---

## MVP1 Specifications (High Priority)

### Spec 1: Local Development Infrastructure Setup
**Priority**: 🔴 Critical (Do First)  
**Estimated Effort**: 1 day

**Description**: Set up Firestore Emulator and fake-gcs-server for local development.

**Components**:

#### 1.1 Firestore Emulator Setup (Python-based)

```bash
# Install Firebase CLI using pnpm
pnpm install -g firebase-tools

# Initialize Firebase project (select Firestore only)
firebase init emulators

# Start emulator
firebase emulators:start --only firestore
```

**Python Configuration**:
```python
# backend/config.py
import os

class Settings:
    # Firestore
    USE_FIRESTORE_EMULATOR: bool = os.getenv("USE_FIRESTORE_EMULATOR", "true").lower() == "true"
    FIRESTORE_EMULATOR_HOST: str = os.getenv("FIRESTORE_EMULATOR_HOST", "localhost:8080")
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "elevenlabs-local")
    
    # GCS
    USE_GCS_EMULATOR: bool = os.getenv("USE_GCS_EMULATOR", "true").lower() == "true"
    GCS_EMULATOR_HOST: str = os.getenv("GCS_EMULATOR_HOST", "http://localhost:4443")
    GCS_BUCKET_NAME: str = os.getenv("GCS_BUCKET_NAME", "elevenlabs-audio")
    
    # ElevenLabs (always real API)
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
```

#### 1.2 fake-gcs-server Setup

```bash
# Option A: Docker (recommended)
docker run -d --name fake-gcs -p 4443:4443 fsouza/fake-gcs-server

# Option B: Download binary
# https://github.com/fsouza/fake-gcs-server/releases
```

**Python GCS Client Configuration**:
```python
# backend/services/storage_service.py
from google.cloud import storage
from backend.config import Settings

def get_storage_client():
    settings = Settings()
    
    if settings.USE_GCS_EMULATOR:
        # Connect to fake-gcs-server
        client = storage.Client(
            project=settings.GOOGLE_CLOUD_PROJECT,
            _http=None,  # Will use emulator
        )
        client._http._base_url = settings.GCS_EMULATOR_HOST
        return client
    else:
        # Production GCS
        return storage.Client()
```

#### 1.3 Development Startup Script

**Files to Create**:
- `scripts/start_emulators.bat` (Windows)
- `scripts/start_emulators.sh` (Linux/Mac)
- `docker-compose.dev.yml` (Alternative: all-in-one)

**docker-compose.dev.yml**:
```yaml
version: '3.8'
services:
  firestore-emulator:
    image: google/cloud-sdk:latest
    command: gcloud emulators firestore start --host-port=0.0.0.0:8080
    ports:
      - "8080:8080"
    environment:
      - FIRESTORE_PROJECT_ID=elevenlabs-local

  gcs-emulator:
    image: fsouza/fake-gcs-server
    ports:
      - "4443:4443"
    command: -scheme http -port 4443
```

**Dependencies**: 
- Docker (recommended) OR
- pnpm + firebase-tools + fake-gcs-server binary

---

### Spec 2: Firestore Data Service
**Priority**: 🔴 Critical  
**Estimated Effort**: 2 days

**Description**: Replace MockDataService with FirestoreDataService that works with both emulator and production.

**Current State**: 
- `backend/services/data_service.py` has MockDataService
- All data stored in-memory dictionaries

**Required Changes**:

1. **Create FirestoreDataService class**
```python
# backend/services/firestore_service.py
from google.cloud import firestore
from backend.config import Settings

class FirestoreDataService:
    def __init__(self):
        settings = Settings()
        
        if settings.USE_FIRESTORE_EMULATOR:
            import os
            os.environ["FIRESTORE_EMULATOR_HOST"] = settings.FIRESTORE_EMULATOR_HOST
        
        self.db = firestore.Client(project=settings.GOOGLE_CLOUD_PROJECT)
    
    # Implement same interface as MockDataService
    async def save_knowledge_document(self, doc): ...
    async def get_knowledge_documents(self): ...
    async def get_dashboard_stats(self): ...
    # ... etc
```

2. **Create abstract DataService interface**
```python
# backend/services/data_service.py
from abc import ABC, abstractmethod

class DataServiceInterface(ABC):
    @abstractmethod
    async def save_knowledge_document(self, doc): pass
    
    @abstractmethod
    async def get_knowledge_documents(self): pass
    # ... etc

def get_data_service() -> DataServiceInterface:
    """Factory function - returns appropriate service based on config"""
    settings = Settings()
    if settings.USE_FIRESTORE_EMULATOR or not settings.USE_MOCK_DATA:
        from backend.services.firestore_service import FirestoreDataService
        return FirestoreDataService()
    else:
        return MockDataService()
```

**Firestore Collections**:
```
/knowledge_documents/{doc_id}
  - knowledge_id: string
  - doctor_id: string
  - disease_name: string
  - document_type: string
  - raw_content: string
  - sync_status: string
  - elevenlabs_document_id: string (nullable)
  - created_at: timestamp

/audio_files/{audio_id}
  - audio_id: string
  - knowledge_id: string
  - voice_id: string
  - script: string
  - audio_url: string
  - duration_seconds: number
  - created_at: timestamp

/agents/{agent_id}
  - agent_id: string
  - name: string
  - knowledge_ids: array
  - voice_id: string
  - answer_style: string
  - elevenlabs_agent_id: string
  - doctor_id: string
  - created_at: timestamp

/conversations/{conversation_id}
  - conversation_id: string
  - patient_id: string
  - agent_id: string
  - agent_name: string
  - requires_attention: boolean
  - main_concerns: array
  - messages: array (subcollection or embedded)
  - answered_questions: array
  - unanswered_questions: array
  - duration_seconds: number
  - created_at: timestamp
```

**Files to Create/Modify**:
- `backend/services/firestore_service.py` (create new)
- `backend/services/data_service.py` (refactor to interface + factory)
- `backend/config.py` (add settings)

**Dependencies**: Spec 1 (Infrastructure Setup)

---

### Spec 3: Storage Service (GCS Compatible)
**Priority**: � Criti cal  
**Estimated Effort**: 1 day

**Description**: Create storage service for audio files that works with both fake-gcs-server and production GCS.

**Required Changes**:

```python
# backend/services/storage_service.py
from google.cloud import storage
from google.auth.credentials import AnonymousCredentials
from backend.config import Settings
import io

class StorageService:
    def __init__(self):
        settings = Settings()
        self.bucket_name = settings.GCS_BUCKET_NAME
        
        if settings.USE_GCS_EMULATOR:
            # Connect to fake-gcs-server
            self.client = storage.Client(
                credentials=AnonymousCredentials(),
                project=settings.GOOGLE_CLOUD_PROJECT,
            )
            # Override endpoint for emulator
            self.client._http._base_url = settings.GCS_EMULATOR_HOST
        else:
            # Production GCS (uses default credentials)
            self.client = storage.Client()
        
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist (for emulator)"""
        try:
            self.client.get_bucket(self.bucket_name)
        except Exception:
            self.client.create_bucket(self.bucket_name)
    
    def upload_audio(self, audio_data: bytes, filename: str) -> str:
        """Upload audio file and return public URL"""
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(f"audio/{filename}")
        blob.upload_from_string(audio_data, content_type="audio/mpeg")
        
        # Return URL (different format for emulator vs production)
        settings = Settings()
        if settings.USE_GCS_EMULATOR:
            return f"{settings.GCS_EMULATOR_HOST}/storage/v1/b/{self.bucket_name}/o/audio%2F{filename}?alt=media"
        else:
            return f"https://storage.googleapis.com/{self.bucket_name}/audio/{filename}"
    
    def delete_audio(self, filename: str) -> bool:
        """Delete audio file"""
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(f"audio/{filename}")
        blob.delete()
        return True

def get_storage_service() -> StorageService:
    return StorageService()
```

**Files to Create**:
- `backend/services/storage_service.py`

**Dependencies**: Spec 1 (Infrastructure Setup)

---

### Spec 4: ElevenLabs Knowledge Base Integration
**Priority**: 🔴 Critical  
**Estimated Effort**: 2 days

**Description**: Enable real synchronization between Firestore knowledge documents and ElevenLabs Knowledge Base API.

**Current State**: 
- `elevenlabs_service.py` has `create_document()` method
- Upload Knowledge page calls backend API
- Data stored in MockDataService

**Required Changes**:
1. **Backend**: Enhance `elevenlabs_service.py` error handling and retry logic
2. **Backend**: Update knowledge API to use FirestoreDataService
3. **Backend**: Implement sync status tracking (pending/syncing/completed/failed)
4. **Backend**: Add retry mechanism for failed syncs
5. **Frontend**: Display real sync status from ElevenLabs

**Files to Modify**:
- `backend/services/elevenlabs_service.py`
- `backend/api/routes/knowledge.py`
- `streamlit_app/pages/2_Upload_Knowledge.py`

**Dependencies**: Spec 2 (Firestore Data Service)

---

### Spec 5: ElevenLabs TTS Audio Generation
**Priority**: 🔴 Critical  
**Estimated Effort**: 2 days

**Description**: Enable real audio generation using ElevenLabs TTS API with GCS storage.

**Current State**:
- `elevenlabs_service.py` has `text_to_speech()` method
- Education Audio page has UI
- Audio files not persisted

**Required Changes**:
1. **Backend**: Use StorageService to save audio files
2. **Backend**: Store audio metadata in Firestore
3. **Backend**: Implement voice list fetching from ElevenLabs
4. **Backend**: Add script generation (simple template-based for MVP1)
5. **Frontend**: Display generated audio with playback controls

**Files to Modify**:
- `backend/services/elevenlabs_service.py`
- `backend/api/routes/audio.py`
- `streamlit_app/pages/3_Education_Audio.py`

**Dependencies**: Spec 2, Spec 3, Spec 4

---

### Spec 6: ElevenLabs Agent Creation
**Priority**: 🔴 Critical  
**Estimated Effort**: 2 days

**Description**: Enable real AI agent creation in ElevenLabs with knowledge base linking.

**Current State**:
- `elevenlabs_service.py` has `create_agent()` method
- Agent Setup page has UI
- Agents stored in MockDataService

**Required Changes**:
1. **Backend**: Implement real ElevenLabs agent creation API calls
2. **Backend**: Add system prompt templates for answer styles
3. **Backend**: Link knowledge base documents to agents
4. **Backend**: Store agent metadata in Firestore
5. **Backend**: Implement agent deletion with ElevenLabs sync

**System Prompt Templates**:
```python
SYSTEM_PROMPTS = {
    "professional": "你是一位專業的醫療助理，請以準確、客觀的方式回答病患問題。請使用繁體中文回答。",
    "friendly": "你是一位親切的醫療助理，請以溫暖、易懂的方式協助病患。請使用繁體中文回答。",
    "educational": "你是一位衛教專員，請重點提供教育性的醫療資訊。請使用繁體中文回答。"
}
```

**Files to Modify**:
- `backend/services/elevenlabs_service.py`
- `backend/api/routes/agent.py`
- `streamlit_app/pages/4_Agent_Setup.py`

**Dependencies**: Spec 2, Spec 4

---

### Spec 7: Patient Conversation (Text Mode)
**Priority**: 🔴 Critical  
**Estimated Effort**: 3 days

**Description**: Enable text-based patient conversations with AI agents, with audio responses.

**Current State**:
- Patient Test page has conversation UI
- Uses mock responses

**Required Changes**:
1. **Backend**: Implement ElevenLabs Conversational AI integration
2. **Backend**: Create session management for conversations
3. **Backend**: Store conversation messages in Firestore
4. **Backend**: Generate audio responses using TTS
5. **Frontend**: Display text input with audio response playback

**Phase 1 Limitation**: Text input only (no voice input).

**Files to Modify**:
- `backend/services/elevenlabs_service.py`
- `backend/services/patient_service.py`
- `backend/api/routes/patient.py`
- `streamlit_app/pages/5_Patient_Test.py`

**Dependencies**: Spec 2, Spec 5, Spec 6

---

### Spec 8: Conversation Logs Integration
**Priority**: 🟡 High  
**Estimated Effort**: 1 day

**Description**: Connect Conversation Logs page to real Firestore data.

**Current State**:
- Conversation Logs page UI complete
- Uses mock data

**Required Changes**:
1. **Backend**: Save conversations when patient session ends
2. **Backend**: Implement question analysis (answered/unanswered)
3. **Backend**: Query conversations from Firestore
4. **Frontend**: Display real conversation data

**Files to Modify**:
- `backend/services/conversation_service.py`
- `backend/api/routes/conversation.py`
- `streamlit_app/pages/6_Conversation_Logs.py`

**Dependencies**: Spec 2, Spec 7

---

### Spec 9: Dashboard Real Statistics
**Priority**: 🟡 High  
**Estimated Effort**: 0.5 day

**Description**: Connect Doctor Dashboard to real Firestore statistics.

**Required Changes**:
1. **Backend**: Query real counts from Firestore
2. **Backend**: Calculate last activity timestamp

**Files to Modify**:
- `backend/api/dashboard.py`
- `streamlit_app/pages/1_Doctor_Dashboard.py`

**Dependencies**: Spec 2

---

## MVP2 Specifications (Configuration Changes Only)

### Spec 10: Production Environment Configuration
**Priority**: 🟡 High  
**Estimated Effort**: 1 day

**Description**: Configure application for Google Cloud production environment.

**Required Changes**:
1. **Config**: Set `USE_FIRESTORE_EMULATOR=false`
2. **Config**: Set `USE_GCS_EMULATOR=false`
3. **Config**: Configure real GCS bucket name
4. **Config**: Set up service account credentials
5. **Docs**: Document environment setup

**Files to Modify**:
- `backend/config.py`
- `.env.production.example` (create)
- `docs/DEPLOYMENT.md` (create)

**Dependencies**: MVP1 complete

---

### Spec 11: Cloud Run Deployment
**Priority**: 🟡 High  
**Estimated Effort**: 2 days

**Description**: Deploy application to Google Cloud Run.

**Required Changes**:
1. **Docker**: Update Dockerfile for production
2. **Config**: Cloud Run service configuration
3. **CI/CD**: Basic deployment script
4. **Monitoring**: Health check endpoint

**Files to Create/Modify**:
- `Dockerfile` (update)
- `cloudbuild.yaml` (create)
- `backend/api/health.py` (enhance)

**Dependencies**: Spec 10

---

## What Still Needs Real API Calls (No Emulator)

| Component | Reason | Impact |
|-----------|--------|--------|
| ElevenLabs API | No emulator available | Requires API key for all development |

**Mitigation**: 
- Use ElevenLabs free tier during development
- Implement caching to reduce API calls during testing
- Consider mock mode for unit tests only

---

## Implementation Order Summary (Optimized)

### MVP1 Phase 1: Infrastructure (Week 1)

| Order | Spec | Est. Days | Description |
|-------|------|-----------|-------------|
| 1 | Spec 1: Infrastructure Setup | 1 | Emulators + Docker Compose |
| 2 | Spec 2: Firestore Data Service | 2 | Replace MockDataService |
| 3 | Spec 3: Storage Service | 1 | GCS-compatible storage |

### MVP1 Phase 2: Core Features (Week 2)

| Order | Spec | Est. Days | Description |
|-------|------|-----------|-------------|
| 4 | Spec 4: Knowledge Base Integration | 2 | Real ElevenLabs KB sync |
| 5 | Spec 5: TTS Audio Generation | 2 | Real audio with GCS storage |
| 6 | Spec 6: Agent Creation | 2 | Real ElevenLabs agents |

### MVP1 Phase 3: Patient Features (Week 3)

| Order | Spec | Est. Days | Description |
|-------|------|-----------|-------------|
| 7 | Spec 7: Patient Conversation | 3 | Text → Audio conversations |
| 8 | Spec 8: Conversation Logs | 1 | Real conversation data |
| 9 | Spec 9: Dashboard Statistics | 0.5 | Real-time stats |

### MVP2: Cloud Deployment (Week 4)

| Order | Spec | Est. Days | Description |
|-------|------|-----------|-------------|
| 10 | Spec 10: Production Config | 1 | Environment configuration |
| 11 | Spec 11: Cloud Run Deploy | 2 | Deployment setup |

---

## Quick Start Commands

### MVP1 Development Setup

```bash
# 1. Start emulators (choose one method)

# Method A: Docker Compose (recommended)
docker-compose -f docker-compose.dev.yml up -d

# Method B: Manual
# Terminal 1: Firestore Emulator
pnpm install -g firebase-tools
firebase emulators:start --only firestore

# Terminal 2: GCS Emulator
docker run -d -p 4443:4443 fsouza/fake-gcs-server

# 2. Set environment variables
cp .env.example .env
# Edit .env with your ELEVENLABS_API_KEY

# 3. Start backend
cd backend
poetry run uvicorn main:app --reload

# 4. Start frontend
cd streamlit_app
poetry run streamlit run app.py
```

### MVP2 Deployment

```bash
# 1. Set production environment
export USE_FIRESTORE_EMULATOR=false
export USE_GCS_EMULATOR=false
export GCS_BUCKET_NAME=your-production-bucket

# 2. Deploy to Cloud Run
gcloud run deploy elevendops \
  --source . \
  --region asia-east1 \
  --allow-unauthenticated
```

---

## Deferred Specifications (Post-MVP)

The following features are documented but deferred to future phases:

- **Authentication and Security** - Doctor login, patient session security
- **Voice Input for Patient** - Real-time voice input using WebSocket
- **ElevenLabs Webhook Integration** - Automatic conversation analysis
- **Usage Monitoring** - API usage tracking and cost monitoring
- **Advanced Analytics** - Conversation analytics dashboard

---

## Document History

| Date | Version | Changes |
|------|---------|---------|
| 2024-12-19 | 1.0 | Initial roadmap creation |
| 2024-12-19 | 2.0 | Updated to use Firestore Emulator + fake-gcs-server |
