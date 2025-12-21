# MVP1 Setup Guide

Complete step-by-step guide to set up and run the ElevenDops MVP1 local development environment.

## Prerequisites

### Required Software
- Python 3.9+
- Node.js 16+ (for Firebase CLI)
- Docker & Docker Compose (recommended) OR
- pnpm (for Firebase CLI installation)

### Required Accounts
- ElevenLabs account with API key
- Google Cloud account (for future reference, not needed for MVP1)

## Installation Steps

### Step 1: Clone Repository and Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd ElevenDops

# Install Python dependencies
poetry install

# Install Node.js dependencies (for Firebase CLI)
pnpm install -g firebase-tools
```

### Step 2: Setup Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your ElevenLabs API key
# ELEVENLABS_API_KEY=your_api_key_here
```

**Required Environment Variables:**
```
ELEVENLABS_API_KEY=sk_...your_key_here...
USE_FIRESTORE_EMULATOR=true
FIRESTORE_EMULATOR_HOST=localhost:8080
GOOGLE_CLOUD_PROJECT=elevenlabs-local
USE_GCS_EMULATOR=true
GCS_EMULATOR_HOST=http://localhost:4443
GCS_BUCKET_NAME=elevenlabs-audio
```

### Step 3: Start Infrastructure (Emulators)

#### Option A: Docker Compose (Recommended)

```bash
# Start both Firestore Emulator and GCS Emulator
docker-compose -f docker-compose.dev.yml up -d

# Verify services are running
docker-compose -f docker-compose.dev.yml ps

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

**Expected Output:**
```
firestore-emulator   running   Port 8080
gcs-emulator         running   Port 4443
```

#### Option B: Manual Setup (Linux/Mac)

**Terminal 1 - Firestore Emulator:**
```bash
# Install Firebase CLI
pnpm install -g firebase-tools

# Initialize Firebase (select Firestore only)
firebase init emulators

# Start Firestore Emulator
firebase emulators:start --only firestore
```

**Terminal 2 - GCS Emulator:**
```bash
# Download and run fake-gcs-server
# https://github.com/fsouza/fake-gcs-server/releases

# Or use Docker
docker run -d --name fake-gcs -p 4443:4443 fsouza/fake-gcs-server
```

#### Option C: Manual Setup (Windows)

**Terminal 1 - Firestore Emulator:**
```powershell
# Install Firebase CLI
pnpm install -g firebase-tools

# Initialize Firebase
firebase init emulators

# Start Firestore Emulator
firebase emulators:start --only firestore
```

**Terminal 2 - GCS Emulator:**
```powershell
# Download fake-gcs-server binary from:
# https://github.com/fsouza/fake-gcs-server/releases

# Extract and run
.\fake-gcs-server.exe -scheme http -port 4443
```

### Step 4: Verify Emulators Are Running

```bash
# Check Firestore Emulator
curl http://localhost:8080

# Check GCS Emulator
curl -k https://localhost:4443

# Both should respond (Firestore with HTML, GCS with error is OK)
```

### Step 5: Start Backend Server

```bash
# Navigate to backend directory
cd backend

# Start FastAPI server with auto-reload
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

**Backend API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Step 6: Start Frontend (Streamlit)

```bash
# In a new terminal, navigate to streamlit_app directory
cd streamlit_app

# Start Streamlit application
poetry run streamlit run app.py

# Expected output:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
```

### Step 7: Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:8501
- **Backend API Docs**: http://localhost:8000/docs

## Verification Checklist

- [ ] Docker containers running (if using Docker Compose)
- [ ] Firestore Emulator accessible at localhost:8080
- [ ] GCS Emulator accessible at localhost:4443
- [ ] Backend API running at localhost:8000
- [ ] Streamlit app running at localhost:8501
- [ ] Can access Swagger UI at localhost:8000/docs
- [ ] Can load Streamlit app in browser

## Troubleshooting

### Issue: Port Already in Use

```bash
# Find process using port 8080 (Firestore)
lsof -i :8080
# Kill process
kill -9 <PID>

# Or use different port
firebase emulators:start --only firestore --port 9090
# Update FIRESTORE_EMULATOR_HOST=localhost:9090 in .env
```

### Issue: Firestore Emulator Not Starting

```bash
# Clear Firebase cache
rm -rf ~/.cache/firebase

# Reinstall Firebase CLI
pnpm install -g firebase-tools@latest

# Try again
firebase emulators:start --only firestore
```

### Issue: GCS Emulator Connection Error

```bash
# Verify Docker is running
docker ps

# Check container logs
docker logs fake-gcs

# Restart container
docker restart fake-gcs
```

### Issue: Backend Can't Connect to Firestore

```bash
# Verify environment variable is set
echo $FIRESTORE_EMULATOR_HOST
# Should output: localhost:8080

# Check Firestore is running
curl http://localhost:8080

# Restart backend
# Ctrl+C to stop, then restart
poetry run uvicorn main:app --reload
```

### Issue: Streamlit Can't Connect to Backend

```bash
# Verify backend is running
curl http://localhost:8000/docs

# Check Streamlit logs for errors
# Look for connection errors in terminal

# Verify backend URL in streamlit_app/services/backend_api.py
# Should be: http://localhost:8000
```

### Issue: ElevenLabs API Key Error

```bash
# Verify API key is set
echo $ELEVENLABS_API_KEY

# Check .env file has correct format
cat .env | grep ELEVENLABS_API_KEY

# Get new API key from https://elevenlabs.io/app/api-keys
# Update .env and restart backend
```

## Development Workflow

### Daily Startup

```bash
# Terminal 1: Start emulators
docker-compose -f docker-compose.dev.yml up -d

# Terminal 2: Start backend
cd backend && poetry run uvicorn main:app --reload

# Terminal 3: Start frontend
cd streamlit_app && poetry run streamlit run app.py

# Open browser to http://localhost:8501
```

### Daily Shutdown

```bash
# Stop Streamlit (Ctrl+C in Terminal 3)
# Stop Backend (Ctrl+C in Terminal 2)
# Stop Emulators
docker-compose -f docker-compose.dev.yml down
```

## Testing the Setup

### Test 1: Upload Knowledge Document

1. Open Streamlit app (http://localhost:8501)
2. Navigate to "Upload Knowledge" page
3. Upload a sample Markdown file
4. Fill in disease name and document type
5. Click "Save and Sync"
6. Verify document appears in Firestore Emulator

### Test 2: Generate Education Audio

1. Navigate to "Education Audio" page
2. Select uploaded knowledge document
3. Review generated script
4. Click "Generate Audio"
5. Verify audio file is created in GCS Emulator

### Test 3: Create AI Agent

1. Navigate to "Agent Setup" page
2. Enter agent name
3. Select knowledge documents
4. Choose voice and answer style
5. Click "Create Agent"
6. Verify agent is created in ElevenLabs

### Test 4: Patient Conversation

1. Navigate to "Patient Test" page
2. Enter patient ID
3. Select agent
4. Type a question
5. Verify AI response is generated
6. Check conversation is logged in Firestore

## Next Steps

After successful setup:

1. **Explore the Codebase**
   - Review `backend/main.py` for API structure
   - Check `backend/services/` for service implementations
   - Examine `streamlit_app/pages/` for UI components

2. **Implement Real Services**
   - Replace MockDataService with FirestoreDataService
   - Implement StorageService for GCS
   - Enhance ElevenLabs integration

3. **Run Tests**
   - Execute unit tests: `poetry run pytest tests/`
   - Run property-based tests: `poetry run pytest tests/test_*_props.py`

4. **Monitor and Debug**
   - Check backend logs for errors
   - Use Swagger UI to test API endpoints
   - Monitor Firestore Emulator data

## Additional Resources

- [ElevenLabs API Documentation](https://elevenlabs.io/docs)
- [Firestore Emulator Guide](https://firebase.google.com/docs/emulator-suite/connect_firestore)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## Getting Help

If you encounter issues:

1. Check the Troubleshooting section above
2. Review logs in each terminal
3. Verify all environment variables are set
4. Ensure all ports are available
5. Check ElevenLabs API key is valid
6. Review the Implementation Roadmap for known issues

## Quick Reference

| Component | URL | Port |
|-----------|-----|------|
| Streamlit Frontend | http://localhost:8501 | 8501 |
| FastAPI Backend | http://localhost:8000 | 8000 |
| Swagger UI | http://localhost:8000/docs | 8000 |
| Firestore Emulator | http://localhost:8080 | 8080 |
| GCS Emulator | http://localhost:4443 | 4443 |

| Environment Variable | Value |
|---------------------|-------|
| ELEVENLABS_API_KEY | sk_... |
| USE_FIRESTORE_EMULATOR | true |
| FIRESTORE_EMULATOR_HOST | localhost:8080 |
| USE_GCS_EMULATOR | true |
| GCS_EMULATOR_HOST | http://localhost:4443 |
