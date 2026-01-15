---
inclusion: always
---

# ElevenDops Project Overview

## System Purpose
ElevenDops is an intelligent medical assistant system combining ElevenLabs voice AI technology to solve doctor-patient health education communication challenges.

## Core Problem Domain
- Doctors repeatedly explain the same basic medical information to different patients
- Patients lack immediate consultation channels for disease-related questions
- Doctors cannot effectively understand patient concerns before appointments

## Key Reference Documents
- **User Requirements**: #[[file:user-need/user-need-phase1.md]] - Complete Phase 1 system requirements specification
- **ElevenLabs API Index**: #[[file:docs/elevenlabs-api/index.md]] - API documentation navigation

## Technology Stack
- **Frontend**: Streamlit (MVP phase)
- **Backend**: FastAPI
- **Database**: Firestore (primary data source)
- **Voice AI**: ElevenLabs (Knowledge Base, Agents, TTS, Conversational AI)
- **LLM**: Google Gemini (via LangChain/LangGraph)
- **Observability**: LangSmith (tracing and debugging)
- **Deployment**: Cloud Run

## Architecture Principles
1. **Separation of Concerns**: Streamlit handles UI only, backend handles business logic
2. **Firestore as Source of Truth**: ElevenLabs Knowledge Base is a synchronized copy
3. **API-First Design**: RESTful endpoints for future Next.js integration
4. **Modular Structure**: All ElevenLabs calls wrapped in `backend/services/elevenlabs_service.py`

## Main Features (Phase 1)
1. **Knowledge Upload** - Doctors upload medical education documents
2. **Education Audio** - Generate TTS audio from medical scripts
3. **AI Script Generation** - LLM-powered script generation with LangGraph workflow
4. **Agent Setup** - Configure AI assistants with knowledge bases
5. **Patient Test** - Voice conversation interface for patients
6. **Conversation Logs** - Track patient questions for doctor review

## Current Implementation Status

### Backend Services (✅ Complete)
- `elevenlabs_service.py` - ElevenLabs API integration
- `audio_service.py` - TTS audio generation
- `agent_service.py` - Agent management
- `conversation_service.py` - Conversation handling
- `storage_service.py` - GCS file storage
- `firestore_data_service.py` - Firestore operations
- `langgraph_workflow.py` - AI script generation workflow
- `script_generation_service.py` - Script generation orchestration
- `prompt_template_service.py` - Configurable prompts
- `langsmith_tracer.py` - LangSmith observability
- `patient_service.py` - Patient session management
- `analysis_service.py` - Conversation analysis
- `websocket_manager.py` - WebSocket connections

### API Routes (✅ Complete)
- `/api/knowledge` - Knowledge document management
- `/api/audio` - Audio generation
- `/api/agent` - Agent configuration
- `/api/patient` - Patient sessions
- `/api/conversation` - Conversation logs
- `/api/templates` - Prompt templates
- `/api/debug` - Debug endpoints

### Frontend Pages (✅ Complete)
- Doctor Dashboard, Upload Knowledge, Education Audio
- Agent Setup, Patient Test, Conversation Logs

### In Progress
- 🔄 Property-based testing coverage expansion
- 🔄 Cloud Run deployment optimization
