# MVP1 Quick Reference

Fast lookup guide for common tasks and commands.

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

## Common Commands

### Docker Compose

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# Stop all services
docker-compose -f docker-compose.dev.yml down

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# View specific service logs
docker-compose -f docker-compose.dev.yml logs -f firestore-emulator

# Restart services
docker-compose -f docker-compose.dev.yml restart
```

### Backend

```bash
# Start with auto-reload
cd backend && poetry run uvicorn main:app --reload

# Start on different port
cd backend && poetry run uvicorn main:app --reload --port 8001

# Run tests
cd backend && poetry run pytest

# Run specific test
cd backend && poetry run pytest tests/test_knowledge.py

# Run with coverage
cd backend && poetry run pytest --cov=backend tests/
```

### Frontend

```bash
# Start Streamlit
cd streamlit_app && poetry run streamlit run app.py

# Start on different port
cd streamlit_app && poetry run streamlit run app.py --server.port 8502

# Clear cache
cd streamlit_app && poetry run streamlit cache clear
```

### Database

```bash
# Access Firestore Emulator UI
# Open browser to: http://localhost:8080

# Query Firestore from Python
from google.cloud import firestore
db = firestore.Client()
docs = db.collection('knowledge_documents').stream()
for doc in docs:
    print(doc.to_dict())
```

### Storage

```bash
# List files in GCS Emulator
curl -X GET http://localhost:4443/storage/v1/b/elevenlabs-audio/o

# Upload file to GCS Emulator
curl -X POST -F "file=@audio.mp3" http://localhost:4443/upload
```

## API Endpoints Quick Reference

### Knowledge Management
```
POST   /api/knowledge              # Upload knowledge
GET    /api/knowledge              # List knowledge
GET    /api/knowledge/{id}         # Get knowledge details
DELETE /api/knowledge/{id}         # Delete knowledge
```

### Audio Generation
```
POST   /api/audio                  # Generate audio
GET    /api/audio                  # List audio files
GET    /api/audio/voices           # Get available voices
```

### Agent Management
```
POST   /api/agent                  # Create agent
GET    /api/agent                  # List agents
GET    /api/agent/{id}             # Get agent details
PUT    /api/agent/{id}             # Update agent
DELETE /api/agent/{id}             # Delete agent
```

### Patient Conversations
```
POST   /api/patient/conversation/start              # Start conversation
POST   /api/patient/conversation/{id}/message       # Send message
GET    /api/patient/conversation/{id}/response      # Get response
POST   /api/patient/conversation/{id}/end           # End conversation
```

### Conversation Logs
```
GET    /api/conversation/logs      # List conversations
GET    /api/conversation/{id}      # Get conversation details
```

### Dashboard
```
GET    /api/dashboard/stats        # Get statistics
```

## Testing with cURL

### Upload Knowledge
```bash
curl -X POST http://localhost:8000/api/knowledge \
  -H "Content-Type: application/json" \
  -d '{
    "disease_name": "白內障",
    "document_type": "術後照護",
    "raw_content": "# 白內障術後照護\n\n1. 保持眼睛清潔",
    "doctor_id": "doctor_001"
  }'
```

### Get Knowledge
```bash
curl http://localhost:8000/api/knowledge
```

### Create Agent
```bash
curl -X POST http://localhost:8000/api/agent \
  -H "Content-Type: application/json" \
  -d '{
    "name": "白內障助手",
    "knowledge_ids": ["kb_123"],
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "answer_style": "professional",
    "doctor_id": "doctor_001"
  }'
```

### Start Conversation
```bash
curl -X POST http://localhost:8000/api/patient/conversation/start \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient_001",
    "agent_id": "agent_123"
  }'
```

### Send Message
```bash
curl -X POST http://localhost:8000/api/patient/conversation/conv_123/message \
  -H "Content-Type: application/json" \
  -d '{
    "text": "白內障手術後多久可以洗臉？"
  }'
```

## File Structure

```
ElevenDops/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration settings
│   ├── api/
│   │   ├── routes/
│   │   │   ├── knowledge.py
│   │   │   ├── audio.py
│   │   │   ├── agent.py
│   │   │   ├── patient.py
│   │   │   ├── conversation.py
│   │   │   └── dashboard.py
│   │   └── models/
│   │       ├── knowledge.py
│   │       ├── audio.py
│   │       ├── agent.py
│   │       └── conversation.py
│   └── services/
│       ├── elevenlabs_service.py
│       ├── firestore_service.py
│       ├── storage_service.py
│       └── conversation_service.py
├── streamlit_app/
│   ├── app.py                  # Streamlit entry point
│   ├── pages/
│   │   ├── 1_Doctor_Dashboard.py
│   │   ├── 2_Upload_Knowledge.py
│   │   ├── 3_Education_Audio.py
│   │   ├── 4_Agent_Setup.py
│   │   ├── 5_Patient_Test.py
│   │   └── 6_Conversation_Logs.py
│   └── services/
│       └── backend_api.py
├── tests/
│   ├── test_knowledge_props.py
│   ├── test_audio_props.py
│   ├── test_agent_props.py
│   └── test_conversation_props.py
├── docs/
│   ├── MVP1_SETUP_GUIDE.md
│   ├── MVP1_IMPLEMENTATION_SUMMARY.md
│   ├── MVP1_API_REFERENCE.md
│   ├── MVP1_ARCHITECTURE.md
│   └── MVP1_QUICK_REFERENCE.md
├── docker-compose.dev.yml
├── pyproject.toml
├── poetry.lock
└── .env.example
```

## Environment Variables

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

## Firestore Collections

### knowledge_documents
```json
{
  "knowledge_id": "kb_123",
  "doctor_id": "doctor_001",
  "disease_name": "白內障",
  "document_type": "術後照護",
  "raw_content": "...",
  "sync_status": "completed",
  "elevenlabs_document_id": "doc_abc",
  "created_at": "2024-12-21T10:30:00Z"
}
```

### agents
```json
{
  "agent_id": "agent_123",
  "name": "白內障助手",
  "knowledge_ids": ["kb_123"],
  "voice_id": "21m00Tcm4TlvDq8ikWAM",
  "answer_style": "professional",
  "elevenlabs_agent_id": "agent_abc",
  "doctor_id": "doctor_001",
  "created_at": "2024-12-21T10:40:00Z"
}
```

### conversations
```json
{
  "conversation_id": "conv_123",
  "patient_id": "patient_001",
  "agent_id": "agent_123",
  "agent_name": "白內障助手",
  "requires_attention": false,
  "main_concerns": ["術後護理"],
  "answered_questions": 4,
  "unanswered_questions": 1,
  "duration_seconds": 300,
  "created_at": "2024-12-21T10:50:00Z"
}
```

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Port 8080 in use | `lsof -i :8080` then `kill -9 <PID>` |
| Port 8000 in use | `lsof -i :8000` then `kill -9 <PID>` |
| Port 8501 in use | `lsof -i :8501` then `kill -9 <PID>` |
| Firestore not starting | `rm -rf ~/.cache/firebase` then retry |
| GCS connection error | `docker restart fake-gcs` |
| API key error | Check `.env` file has correct key |
| Streamlit can't connect | Verify backend is running on 8000 |
| Firestore empty | Check emulator is running on 8080 |

## Useful URLs

| Service | URL |
|---------|-----|
| Streamlit Frontend | http://localhost:8501 |
| FastAPI Backend | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Firestore Emulator | http://localhost:8080 |
| GCS Emulator | http://localhost:4443 |

## Key Concepts

### Knowledge Document
Medical information uploaded by doctor, synced to ElevenLabs Knowledge Base.

### Agent
AI assistant configured with knowledge bases, voice, and answer style.

### Conversation
Patient interaction with an agent, logged for doctor review.

### Audio File
Generated education audio or conversation response.

### Sync Status
- `pending`: Waiting to sync to ElevenLabs
- `syncing`: Currently syncing
- `completed`: Successfully synced
- `failed`: Sync failed

### Answer Style
- `professional`: Accurate, objective responses
- `friendly`: Warm, easy-to-understand responses
- `educational`: Focus on medical education

## Common Workflows

### Workflow 1: Create Education Content
1. Upload knowledge document
2. Wait for sync to complete
3. Generate education audio
4. Review and confirm script
5. Audio ready for patients

### Workflow 2: Setup AI Agent
1. Upload knowledge documents
2. Create agent with knowledge bases
3. Select voice and answer style
4. Agent ready for patient conversations

### Workflow 3: Patient Conversation
1. Patient selects agent
2. Patient types question
3. AI generates response
4. Audio response played
5. Conversation logged

### Workflow 4: Review Patient Feedback
1. Doctor views conversation logs
2. Identifies unanswered questions
3. Reviews patient concerns
4. Updates knowledge base if needed

## Performance Tips

- Cache voices list to reduce API calls
- Batch knowledge document uploads
- Use pagination for large result sets
- Monitor API usage to avoid quota limits
- Clear Streamlit cache periodically

## Security Reminders

- Never commit `.env` file with API keys
- Use environment variables for secrets
- Rotate API keys regularly
- Limit API key permissions
- Monitor API usage for anomalies

## Getting Help

1. Check logs in each terminal
2. Review error messages in Swagger UI
3. Check Firestore Emulator UI for data
4. Verify all services are running
5. Check environment variables are set
6. Review API documentation
7. Check implementation roadmap for known issues

## Next Steps

After MVP1 setup:
1. Explore Swagger UI at http://localhost:8000/docs
2. Test each API endpoint
3. Review Firestore data in emulator
4. Test end-to-end workflows
5. Review code in backend/services/
6. Run tests: `poetry run pytest`
7. Read full documentation in docs/ folder
