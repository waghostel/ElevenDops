# MVP1 Complete Backend Guide

> **Note:** This document consolidates the former MVP1_ARCHITECTURE.md, MVP1_IMPLEMENTATION_SUMMARY.md, and MVP1_API_REFERENCE.md files.

Comprehensive technical documentation for ElevenDops MVP1 backend system.

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Component Breakdown](#component-breakdown)
4. [API Reference](#api-reference)
5. [Data Schemas](#data-schemas)
6. [Configuration](#configuration)
7. [Error Handling](#error-handling)
8. [Testing & Performance](#testing--performance)
9. [Future Roadmap](#future-roadmap)

---

## Overview

MVP1 is a **fully functional local development environment** for the ElevenDops medical assistant system with real ElevenLabs integration and local data persistence.

### What MVP1 Delivers

- Doctors can upload medical knowledge documents
- System syncs knowledge to ElevenLabs Knowledge Base
- Doctors can generate education audio using ElevenLabs TTS
- Doctors can create AI agents linked to knowledge bases
- Patients can have text-based conversations with AI agents
- All conversations are logged and analyzed
- Doctors can review patient questions and concerns

**Key Principle**: MVP1 uses the same application code as production (MVP2). Only configuration changes between environments.

### Technology Stack

| Component | Technology         | Purpose                                        |
| --------- | ------------------ | ---------------------------------------------- |
| Frontend  | Streamlit          | User interface                                 |
| Backend   | FastAPI            | REST API                                       |
| Database  | Firestore Emulator | Local data persistence                         |
| Storage   | fake-gcs-server    | Local file storage                             |
| AI/Voice  | ElevenLabs         | Knowledge Base, Agents, TTS, Conversational AI |
| Language  | Python             | Backend implementation                         |

---

## System Architecture

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
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────┬──────────────────────────────────────────────────────────┘
          │
┌─────────▼─────────────────────────────────────────────────────────┐
│                    Service Layer (Python)                          │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  ElevenLabs Service · Firestore Service · Storage Service  │   │
│  │  Conversation Service · LangSmith Tracer · LangGraph       │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────┬──────────────────────┬──────────────────────┬───────────┘
          │                      │                      │
          ▼                      ▼                      ▼
    ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
    │  Firestore   │      │ ElevenLabs   │      │     GCS      │
    │  Emulator    │      │  Real API    │      │  Emulator    │
    │  :8080       │      │              │      │  :4443       │
    └──────────────┘      └──────────────┘      └──────────────┘
```

---

## Component Breakdown

### 1. User Interface Layer (Streamlit)

**Doctor Portal Pages:**

- Doctor Dashboard - System overview and statistics
- Upload Knowledge - Medical document management
- Education Audio - Audio generation and management
- Agent Setup - AI agent configuration
- Conversation Logs - Patient interaction review

**Patient Portal Pages:**

- Patient Test - AI agent interaction interface
- Education Audio - Pre-recorded medical information

### 2. API Layer (FastAPI)

```
backend/api/
├── routes/
│   ├── knowledge.py      # Knowledge document endpoints
│   ├── audio.py          # Audio generation endpoints
│   ├── agent.py          # Agent management endpoints
│   ├── patient.py        # Patient conversation endpoints
│   ├── conversation.py   # Conversation logs endpoints
│   ├── dashboard.py      # Dashboard statistics endpoints
│   └── debug.py          # Debug and tracing endpoints
└── models/
    ├── knowledge.py      # Knowledge Pydantic schemas
    ├── audio.py          # Audio Pydantic schemas
    ├── agent.py          # Agent Pydantic schemas
    └── conversation.py   # Conversation Pydantic schemas
```

### 3. Service Layer

| Service                   | Responsibilities                                       |
| ------------------------- | ------------------------------------------------------ |
| `elevenlabs_service.py`   | Knowledge Base API, Agents API, TTS, Conversational AI |
| `firestore_service.py`    | CRUD operations, Query operations, Transactions        |
| `storage_service.py`      | File upload/download, GCS-compatible operations        |
| `conversation_service.py` | Session management, Message handling, Analysis         |
| `langsmith_tracer.py`     | Workflow tracing and debugging                         |
| `langgraph_workflow.py`   | Script generation workflow                             |

### 4. Data Flow Patterns

**Knowledge Upload Flow:**

```
Doctor uploads Markdown → Backend validates → Store in Firestore
→ Sync to ElevenLabs → Update Firestore with ID → Show status
```

**Audio Generation Flow:**

```
Doctor selects document → Generate script → ElevenLabs TTS
→ Upload to GCS → Store metadata → Display audio player
```

**Patient Conversation Flow:**

```
Patient types question → ElevenLabs AI response → Generate audio
→ Store conversation → Play response → Log for doctor review
```

---

## API Reference

**Base URL:** `http://localhost:8000`

**Authentication:** MVP1 does not implement authentication. All endpoints are publicly accessible.

### Response Format

**Success (2xx):**

```json
{"status": "success", "data": {...}, "message": "Operation completed successfully"}
```

**Error (4xx, 5xx):**

```json
{
  "status": "error",
  "error": "ERROR_CODE",
  "message": "Human-readable message",
  "details": {}
}
```

### Knowledge Management

| Method   | Endpoint              | Description               |
| -------- | --------------------- | ------------------------- |
| `POST`   | `/api/knowledge`      | Upload knowledge document |
| `GET`    | `/api/knowledge`      | List knowledge documents  |
| `GET`    | `/api/knowledge/{id}` | Get knowledge details     |
| `DELETE` | `/api/knowledge/{id}` | Delete knowledge document |

### Audio Generation

| Method | Endpoint            | Description              |
| ------ | ------------------- | ------------------------ |
| `POST` | `/api/audio`        | Generate education audio |
| `GET`  | `/api/audio`        | List audio files         |
| `GET`  | `/api/audio/voices` | Get available voices     |

### Agent Management

| Method   | Endpoint          | Description       |
| -------- | ----------------- | ----------------- |
| `POST`   | `/api/agent`      | Create AI agent   |
| `GET`    | `/api/agent`      | List agents       |
| `GET`    | `/api/agent/{id}` | Get agent details |
| `PUT`    | `/api/agent/{id}` | Update agent      |
| `DELETE` | `/api/agent/{id}` | Delete agent      |

### Patient Conversations

| Method | Endpoint                                  | Description        |
| ------ | ----------------------------------------- | ------------------ |
| `POST` | `/api/patient/conversation/start`         | Start conversation |
| `POST` | `/api/patient/conversation/{id}/message`  | Send message       |
| `GET`  | `/api/patient/conversation/{id}/response` | Get response       |
| `POST` | `/api/patient/conversation/{id}/end`      | End conversation   |

### Conversation Logs

| Method | Endpoint                 | Description              |
| ------ | ------------------------ | ------------------------ |
| `GET`  | `/api/conversation/logs` | List conversations       |
| `GET`  | `/api/conversation/{id}` | Get conversation details |

### Dashboard

| Method | Endpoint               | Description    |
| ------ | ---------------------- | -------------- |
| `GET`  | `/api/dashboard/stats` | Get statistics |

### Error Codes

| Code               | HTTP Status | Description                   |
| ------------------ | ----------- | ----------------------------- |
| `INVALID_REQUEST`  | 400         | Invalid request parameters    |
| `NOT_FOUND`        | 404         | Resource not found            |
| `CONFLICT`         | 409         | Resource already exists       |
| `VALIDATION_ERROR` | 422         | Data validation failed        |
| `FIRESTORE_ERROR`  | 500         | Database operation failed     |
| `ELEVENLABS_ERROR` | 502         | ElevenLabs API error          |
| `STORAGE_ERROR`    | 500         | File storage operation failed |

### Pagination

Endpoints that return lists support pagination with `limit` (default: 50, max: 100) and `offset` (default: 0) query parameters.

---

## Data Schemas

### Firestore Collections

**knowledge_documents:**

```json
{
  "knowledge_id": "string",
  "doctor_id": "string",
  "disease_name": "string",
  "document_type": "string",
  "raw_content": "string",
  "sync_status": "pending|syncing|completed|failed",
  "elevenlabs_document_id": "string (nullable)",
  "created_at": "timestamp"
}
```

**audio_files:**

```json
{
  "audio_id": "string",
  "knowledge_id": "string",
  "voice_id": "string",
  "script": "string",
  "audio_url": "string",
  "duration_seconds": "number",
  "created_at": "timestamp"
}
```

**agents:**

```json
{
  "agent_id": "string",
  "name": "string",
  "knowledge_ids": ["string"],
  "voice_id": "string",
  "answer_style": "professional|friendly|educational",
  "elevenlabs_agent_id": "string",
  "doctor_id": "string",
  "created_at": "timestamp"
}
```

**conversations:**

```json
{
  "conversation_id": "string",
  "patient_id": "string",
  "agent_id": "string",
  "agent_name": "string",
  "requires_attention": "boolean",
  "main_concerns": ["string"],
  "answered_questions": ["string"],
  "unanswered_questions": ["string"],
  "duration_seconds": "number",
  "created_at": "timestamp"
}
```

---

## Configuration

### Environment Variables

```bash
# ElevenLabs
ELEVENLABS_API_KEY=sk_...

# Firestore
USE_FIRESTORE_EMULATOR=true
FIRESTORE_EMULATOR_HOST=localhost:8080
GOOGLE_CLOUD_PROJECT=elevenlabs-local

# GCS
USE_GCS_EMULATOR=true
GCS_EMULATOR_HOST=http://localhost:4443
GCS_BUCKET_NAME=elevenlabs-audio
```

### MVP2 Transition

MVP1 to MVP2 requires **configuration changes only**:

| Setting                  | MVP1             | MVP2               |
| ------------------------ | ---------------- | ------------------ |
| `USE_FIRESTORE_EMULATOR` | true             | false              |
| `USE_GCS_EMULATOR`       | true             | false              |
| `GOOGLE_CLOUD_PROJECT`   | elevenlabs-local | production-project |
| `GCS_BUCKET_NAME`        | elevenlabs-audio | production-bucket  |

---

## Error Handling

### Error Hierarchy

```
Exception
├── ValidationError (InvalidDocumentFormat, InvalidAgentConfig, InvalidConversationData)
├── NotFoundError (KnowledgeNotFound, AgentNotFound, ConversationNotFound)
├── ExternalServiceError (ElevenLabsError, FirestoreError, StorageError)
└── InternalError (UnexpectedError)
```

---

## Testing & Performance

### Testing Strategy

- **Unit Tests:** Test individual service functions, mock ElevenLabs API
- **Integration Tests:** Test API endpoints with real Firestore Emulator
- **Property-Based Tests:** Use Hypothesis for data validation

### Performance Benchmarks

| Operation             | Target Response Time                   |
| --------------------- | -------------------------------------- |
| Knowledge upload      | < 2 seconds                            |
| Audio generation      | 5-30 seconds (script length dependent) |
| Agent creation        | < 5 seconds                            |
| Conversation response | 2-10 seconds                           |

### Database Indexing

- Index on `doctor_id` for doctor queries
- Index on `patient_id` for patient queries
- Index on `created_at` for time-based queries
- Composite index on `(doctor_id, created_at)`

---

## Future Roadmap

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

---

## References

- [ElevenLabs API Documentation](https://elevenlabs.io/docs)
- [Firestore Emulator Guide](https://firebase.google.com/docs/emulator-suite/connect_firestore)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [DEBUG_API_REFERENCE.md](DEBUG_API_REFERENCE.md) - Complete debug API documentation
