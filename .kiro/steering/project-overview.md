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
- **Deployment**: Cloud Run

## Architecture Principles
1. **Separation of Concerns**: Streamlit handles UI only, backend handles business logic
2. **Firestore as Source of Truth**: ElevenLabs Knowledge Base is a synchronized copy
3. **API-First Design**: RESTful endpoints for future Next.js integration
4. **Modular Structure**: All ElevenLabs calls wrapped in `backend/services/elevenlabs_service.py`

## Main Features (Phase 1)
1. **Knowledge Upload** - Doctors upload medical education documents
2. **Education Audio** - Generate TTS audio from medical scripts
3. **Agent Setup** - Configure AI assistants with knowledge bases
4. **Patient Test** - Voice conversation interface for patients
5. **Conversation Logs** - Track patient questions for doctor review
