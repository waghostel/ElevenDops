# ElevenDops Project Context: Streamlit MVP Foundation

## 1. Project Overview (User Needs Phase 1)

**ElevenDops** is an intelligent medical assistant system leveraging ElevenLabs voice technology to improve communication between doctors and patients.

- **Core Problem**: Doctors repeat the same basic medical instructions; patients lack immediate channels for questions.
- **Solution**:
  - **Education Audio**: Pre-recorded standardized medical explanations.
  - **Conversational AI**: Voice-enabled Q&A for patients.
  - **Insight Analysis**: Collection of patient questions for doctor review.

## 2. Phase 1 Architecture (Streamlit MVP)

The system is designed as a **Streamlit Application** backed by a **FastAPI** service, deployed on **Cloud Run**.

### Components

1.  **Streamlit Frontend** (`port 8501`)

    - **Role**: Presentation layer, Doctor UI, Patient Test UI.
    - **Pages**:
      - `1_Doctor_Dashboard.py`: System status and metrics.
      - `2_Upload_Knowledge.py`: RAG knowledge base management.
      - `3_Education_Audio.py`: TTS audio generation and review.
      - `4_Agent_Setup.py`: Conversational agent configuration.
      - `5_Patient_Test.py`: Patient verification interface.
      - `6_Conversation_Logs.py`: History and analytics.
    - **Service Layer**: Communicates with Backend API, **NO** direct DB/LLM access.

2.  **FastAPI Backend** (`port 8000`)
    - **Role**: Business logic, Database access, Third-party integrations.
    - **Endpoints**:
      - `/api/health`: System health check.
      - `/api/dashboard/stats`: Aggregated metrics.
      - Future: `/api/knowledge`, `/api/audio`, `/api/agent`, etc.
    - **Data Layer**:
      - **Firestore**: Primary source of truth.
      - **ElevenLabs**: Knowledge base and Voice synthesis (synced from Firestore).

## 3. Implementation Plan (Foundation)

The current focus is building the architectural skeleton (`streamlit-mvp-foundation`).

### Immediate Goals

- [ ] **Project Structure**: Poetry setup, directory layout (`backend/`, `streamlit_app/`).
- [ ] **FastAPI Foundation**: Health check, Mock data service, Pydantic models.
- [ ] **Streamlit Skeleton**: Main `app.py`, Sidebar navigation, Branding.
- [ ] **Doctor Dashboard**: Metrics display fetching data from Backend API.
- [ ] **Client Service**: `BackendAPIClient` module for frontend-backend communication.
- [ ] **Deployment**: Dockerfile for Cloud Run.

## 4. Key Design Principles

- **Separation of Concerns**: Streamlit only handles UI; FastAPI handles logic.
- **Medical Compliance**: All generated content requires Doctor review/approval.
- **Security**: Use Signed URLs for client-side audio/sockets; Secrets management via Env vars.
- **Scalability**: Designed to migrate Frontend to Next.js in Phase 2 while keeping Backend API.

## 5. References

- **User Needs**: `user-need/user-need-phase1.md`
- **Design Doc**: `.kiro/specs/streamlit-mvp-foundation/design.md`
- **Requirements**: `.kiro/specs/streamlit-mvp-foundation/requirements.md`
- **Tasks**: `.kiro/specs/streamlit-mvp-foundation/tasks.md`
