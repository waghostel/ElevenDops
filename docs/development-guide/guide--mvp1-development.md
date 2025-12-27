# MVP1 Development Guide

> **Note:** This document consolidates the former MVP1_SETUP_GUIDE.md and MVP1_QUICK_REFERENCE.md files.

Complete guide to set up and develop with the ElevenDops MVP1 local environment.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Common Commands](#common-commands)
5. [API Quick Reference](#api-quick-reference)
6. [Project Structure](#project-structure)
7. [Key Concepts](#key-concepts)
8. [Common Workflows](#common-workflows)
9. [Troubleshooting](#troubleshooting)
10. [Testing](#testing)

---

## Quick Start (5 minutes)

```bash
# 1. Start infrastructure
docker-compose -f docker-compose.dev.yml up -d

# 2. Set environment
cp .env.example .env
# Edit .env and add ELEVENLABS_API_KEY

# 3. Start backend (Terminal 2)
cd backend && poetry run uvicorn main:app --reload

# 4. Start frontend (Terminal 3)
cd streamlit_app && poetry run streamlit run app.py

# 5. Open browser
# Frontend: http://localhost:8501
# API Docs: http://localhost:8000/docs
```

---

## Prerequisites

### Required Software

- Python 3.9+
- Node.js 16+ (for Firebase CLI)
- Docker & Docker Compose (recommended)
- pnpm (for Firebase CLI installation)

### Required Accounts

- ElevenLabs account with API key
- Google Cloud account (for future reference, not needed for MVP1)

---

## Installation

### Step 1: Clone and Install Dependencies

```bash
git clone <repository-url>
cd ElevenDops
poetry install
pnpm install -g firebase-tools
```

### Step 2: Setup Environment Variables

```bash
cp .env.example .env
# Edit .env and add your ElevenLabs API key
```

**Required Environment Variables:**

```bash
ELEVENLABS_API_KEY=sk_...your_key_here...
USE_FIRESTORE_EMULATOR=true
FIRESTORE_EMULATOR_HOST=localhost:8080
GOOGLE_CLOUD_PROJECT=elevenlabs-local
USE_GCS_EMULATOR=true
GCS_EMULATOR_HOST=http://localhost:4443
GCS_BUCKET_NAME=elevenlabs-audio
```

### Step 3: Start Infrastructure

**Docker Compose (Recommended):**

```bash
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml ps  # Verify
```

**Manual Setup (Windows):**

```powershell
# Terminal 1 - Firestore
firebase init emulators
firebase emulators:start --only firestore

# Terminal 2 - GCS
.\fake-gcs-server.exe -scheme http -port 4443
```

### Step 4: Start Application

```bash
# Backend
cd backend && poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (new terminal)
cd streamlit_app && poetry run streamlit run app.py
```

### Verification Checklist

- [ ] Docker containers running
- [ ] Firestore Emulator at localhost:8080
- [ ] GCS Emulator at localhost:4443
- [ ] Backend at localhost:8000
- [ ] Streamlit at localhost:8501
- [ ] Swagger UI at localhost:8000/docs

---

## Common Commands

### Docker Compose

```bash
docker-compose -f docker-compose.dev.yml up -d      # Start
docker-compose -f docker-compose.dev.yml down       # Stop
docker-compose -f docker-compose.dev.yml logs -f    # Logs
docker-compose -f docker-compose.dev.yml restart    # Restart
```

### Backend

```bash
cd backend && poetry run uvicorn main:app --reload              # Start
cd backend && poetry run uvicorn main:app --reload --port 8001  # Different port
cd backend && poetry run pytest                                  # Tests
cd backend && poetry run pytest --cov=backend tests/            # Coverage
```

### Frontend

```bash
cd streamlit_app && poetry run streamlit run app.py              # Start
cd streamlit_app && poetry run streamlit run app.py --server.port 8502  # Different port
cd streamlit_app && poetry run streamlit cache clear             # Clear cache
```

### Database (Firestore)

```python
from google.cloud import firestore
db = firestore.Client()
docs = db.collection('knowledge_documents').stream()
for doc in docs:
    print(doc.to_dict())
```

### Storage (GCS)

```bash
curl -X GET http://localhost:4443/storage/v1/b/elevenlabs-audio/o
```

---

## API Quick Reference

### Endpoints

| Category      | Endpoints                                                                                |
| ------------- | ---------------------------------------------------------------------------------------- | -------- | ---- |
| **Knowledge** | `POST GET DELETE /api/knowledge`, `GET /api/knowledge/{id}`                              |
| **Audio**     | `POST GET /api/audio`, `GET /api/audio/voices`                                           |
| **Agent**     | `POST GET PUT DELETE /api/agent`, `GET /api/agent/{id}`                                  |
| **Patient**   | `POST /api/patient/conversation/start`, `POST GET /api/patient/conversation/{id}/message | response | end` |
| **Logs**      | `GET /api/conversation/logs`, `GET /api/conversation/{id}`                               |
| **Dashboard** | `GET /api/dashboard/stats`                                                               |

### Testing with cURL

```bash
# Upload Knowledge
curl -X POST http://localhost:8000/api/knowledge \
  -H "Content-Type: application/json" \
  -d '{"disease_name": "白內障", "document_type": "術後照護", "raw_content": "# Content", "doctor_id": "doctor_001"}'

# Create Agent
curl -X POST http://localhost:8000/api/agent \
  -H "Content-Type: application/json" \
  -d '{"name": "白內障助手", "knowledge_ids": ["kb_123"], "voice_id": "21m00Tcm4TlvDq8ikWAM", "answer_style": "professional", "doctor_id": "doctor_001"}'

# Start Conversation
curl -X POST http://localhost:8000/api/patient/conversation/start \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "patient_001", "agent_id": "agent_123"}'
```

---

## Project Structure

```
ElevenDops/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration
│   ├── api/routes/          # API endpoints
│   └── services/            # Business logic
├── streamlit_app/
│   ├── app.py               # Streamlit entry point
│   ├── pages/               # UI pages
│   └── services/            # API client
├── tests/                   # Test files
├── docker-compose.dev.yml
├── pyproject.toml
└── .env.example
```

---

## Key Concepts

| Concept                | Description                                                |
| ---------------------- | ---------------------------------------------------------- |
| **Knowledge Document** | Medical info uploaded by doctor, synced to ElevenLabs      |
| **Agent**              | AI assistant with knowledge bases, voice, and answer style |
| **Conversation**       | Patient interaction with agent, logged for review          |
| **Sync Status**        | `pending` → `syncing` → `completed` or `failed`            |
| **Answer Style**       | `professional`, `friendly`, or `educational`               |

---

## Common Workflows

### Create Education Content

1. Upload knowledge document
2. Wait for sync to complete
3. Generate education audio
4. Review and confirm script
5. Audio ready for patients

### Setup AI Agent

1. Upload knowledge documents
2. Create agent with knowledge bases
3. Select voice and answer style
4. Agent ready for conversations

### Patient Conversation

1. Patient selects agent
2. Patient types question
3. AI generates response
4. Audio response played
5. Conversation logged

---

## Troubleshooting

| Problem                 | Solution                              |
| ----------------------- | ------------------------------------- |
| Port 8080 in use        | `lsof -i :8080` then `kill -9 <PID>`  |
| Port 8000 in use        | `lsof -i :8000` then `kill -9 <PID>`  |
| Port 8501 in use        | `lsof -i :8501` then `kill -9 <PID>`  |
| Firestore not starting  | `rm -rf ~/.cache/firebase` then retry |
| GCS connection error    | `docker restart fake-gcs`             |
| API key error           | Check `.env` file has correct key     |
| Streamlit can't connect | Verify backend is running on 8000     |
| Firestore empty         | Check emulator is running on 8080     |

### Common Fixes

**Firestore Emulator Not Starting:**

```bash
rm -rf ~/.cache/firebase
pnpm install -g firebase-tools@latest
firebase emulators:start --only firestore
```

**Backend Can't Connect to Firestore:**

```bash
echo $FIRESTORE_EMULATOR_HOST  # Should be localhost:8080
curl http://localhost:8080      # Test connection
```

---

## Testing

### Run Tests

```bash
cd backend && poetry run pytest tests/
cd backend && poetry run pytest tests/test_knowledge.py  # Specific test
cd backend && poetry run pytest --cov=backend tests/     # With coverage
```

### Manual Testing

1. **Upload Knowledge:** Streamlit → Upload Knowledge → Upload file → Save and Sync
2. **Generate Audio:** Education Audio → Select document → Generate Audio
3. **Create Agent:** Agent Setup → Enter name → Select knowledge → Create
4. **Test Conversation:** Patient Test → Select agent → Ask question

---

## Useful URLs

| Service            | URL                         | Port |
| ------------------ | --------------------------- | ---- |
| Streamlit Frontend | http://localhost:8501       | 8501 |
| FastAPI Backend    | http://localhost:8000       | 8000 |
| Swagger UI         | http://localhost:8000/docs  | 8000 |
| ReDoc              | http://localhost:8000/redoc | 8000 |
| Firestore Emulator | http://localhost:8080       | 8080 |
| GCS Emulator       | http://localhost:4443       | 4443 |

---

## Additional Resources

- [ElevenLabs API Documentation](https://elevenlabs.io/docs)
- [Firestore Emulator Guide](https://firebase.google.com/docs/emulator-suite/connect_firestore)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
