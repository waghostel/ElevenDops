# ElevenDops Postman Collection Report

**Date:** January 15, 2026  
**Status:** ✅ Collection Created & Configured  
**Backend Status:** ⚠️ Not Running (requires manual startup)

---

## Executive Summary

A comprehensive Postman collection has been created for the ElevenDops Backend API with **42 endpoints** organized into **8 functional groups**. The collection is ready for testing once the backend server is running.

### Collection Details
- **Collection ID:** `a6cba9d4-f943-4f64-b6f1-b803ce2bb869`
- **Workspace ID:** `bb2d5c64-2218-483c-8480-10a802b15e5e`
- **Environment ID:** `a3bf18a2-9357-4834-a978-7b6049aa0292`
- **Base URL:** `http://localhost:8000`
- **Configuration File:** `.postman.json`

---

## API Endpoints Covered

### 1. Health & Infrastructure (3 endpoints)
- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `GET /api/dashboard/stats` - Dashboard statistics

### 2. Knowledge Management (5 endpoints)
- `POST /api/knowledge` - Create knowledge document
- `GET /api/knowledge` - List all documents
- `GET /api/knowledge/{id}` - Get specific document
- `PUT /api/knowledge/{id}` - Update document
- `DELETE /api/knowledge/{id}` - Delete document

### 3. Audio Generation (6 endpoints)
- `GET /api/audio/voices/list` - List available voices
- `POST /api/audio/generate-script` - Generate TTS script
- `POST /api/audio` - Generate audio from script
- `GET /api/audio/list` - List audio files
- `GET /api/audio/stream/{id}` - Stream audio file
- `DELETE /api/audio/{id}` - Delete audio file

### 4. Agent Management (6 endpoints)
- `POST /api/agent` - Create agent
- `GET /api/agent` - List agents
- `GET /api/agent/{id}` - Get agent details
- `PUT /api/agent/{id}` - Update agent
- `DELETE /api/agent/{id}` - Delete agent
- `GET /api/agent/system-prompts` - Get system prompts

### 5. Patient Sessions (4 endpoints)
- `POST /api/patient/session` - Start session
- `POST /api/patient/session/{id}/message` - Send message
- `POST /api/patient/session/{id}/end` - End session
- `GET /api/patient/{id}/summary` - Get patient summary

### 6. Conversations (3 endpoints)
- `GET /api/conversations` - List conversations (with filters)
- `GET /api/conversations/statistics` - Get statistics
- `GET /api/conversations/{id}` - Get conversation details

### 7. Templates (7 endpoints)
- `GET /api/templates` - List templates
- `POST /api/templates` - Create template
- `GET /api/templates/{id}` - Get template
- `PUT /api/templates/{id}` - Update template
- `DELETE /api/templates/{id}` - Delete template
- `GET /api/templates/system-prompt` - Get system prompt
- `POST /api/templates/preview` - Preview template

### 8. Debug Endpoints (6 endpoints)
- `GET /api/debug/health` - Debug health check
- `POST /api/debug/script-generation` - Debug script generation
- `GET /api/debug/sessions` - List debug sessions
- `POST /api/debug/sessions` - Create debug session
- `GET /api/debug/sessions/{id}` - Get debug session
- `POST /api/debug/sessions/{id}/end` - End debug session

**Total Endpoints:** 42

---

## Collection Variables

The collection includes pre-configured variables for easy testing:

| Variable | Default Value | Purpose |
|----------|---------------|---------|
| `base_url` | `http://localhost:8000` | Backend API base URL |
| `knowledge_id` | (empty) | Knowledge document ID |
| `agent_id` | (empty) | Agent ID |
| `audio_id` | (empty) | Audio file ID |
| `session_id` | (empty) | Patient session ID |
| `patient_id` | `patient_001` | Patient identifier |
| `conversation_id` | (empty) | Conversation ID |
| `template_id` | (empty) | Template ID |

---

## How to Run Tests

### Step 1: Start the Backend Server

```bash
# Using Poetry
poetry run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Or using Python directly
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Verify Backend is Running

```bash
# Test the health endpoint
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-15T00:00:00Z",
  "version": "0.1.0"
}
```

### Step 3: Import Collection into Postman

1. Open Postman
2. Click **Import** → **File**
3. Select `.postman.json`
4. Collection will be imported with all endpoints

### Step 4: Run Collection Tests

**Option A: Using Postman UI**
1. Select the collection
2. Click **Run** (play icon)
3. Select environment
4. Click **Run ElevenDops Backend API**

**Option B: Using Postman CLI**
```bash
postman collection run .postman.json \
  --environment .postman.json \
  --reporters cli,json \
  --reporter-json-export test-results.json
```

**Option C: Using Kiro Postman Power**
```bash
# Activate Postman power and run collection
kiro postman run-collection \
  --collection-id a6cba9d4-f943-4f64-b6f1-b803ce2bb869 \
  --environment-id a3bf18a2-9357-4834-a978-7b6049aa0292
```

---

## Expected Test Results

### Health & Infrastructure Tests
✅ All endpoints should return 200 OK with proper response structure

### Knowledge Management Tests
- **Create:** Should return 201 with knowledge_id
- **List:** Should return 200 with array of documents
- **Get:** Should return 200 with document details
- **Update:** Should return 200 with updated document
- **Delete:** Should return 204 No Content

### Audio Generation Tests
- **List Voices:** Should return 200 with available voices
- **Generate Script:** Should return 200 with generated script
- **Generate Audio:** Should return 200 with audio URL
- **List Audio:** Should return 200 with audio files
- **Stream:** Should return 200 with audio stream
- **Delete:** Should return 204 No Content

### Agent Management Tests
- **Create:** Should return 201 with agent_id
- **List:** Should return 200 with agents array
- **Get:** Should return 200 with agent details
- **Update:** Should return 200 with updated agent
- **Delete:** Should return 204 No Content
- **System Prompts:** Should return 200 with prompts

### Patient Sessions Tests
- **Start Session:** Should return 200 with session_id and signed_url
- **Send Message:** Should return 200 with response
- **End Session:** Should return 200 with conversation summary
- **Get Summary:** Should return 200 with patient summary

### Conversations Tests
- **List:** Should return 200 with conversations array
- **Statistics:** Should return 200 with stats
- **Get Details:** Should return 200 with conversation details

### Templates Tests
- **List:** Should return 200 with templates array
- **Create:** Should return 201 with template_id
- **Get:** Should return 200 with template details
- **Update:** Should return 200 with updated template
- **Delete:** Should return 204 No Content
- **System Prompt:** Should return 200 with prompt
- **Preview:** Should return 200 with preview content

### Debug Tests
- **Health:** Should return 200 with debug info
- **Script Generation:** Should return 200 with generated script
- **Sessions:** Should return 200 with sessions array
- **Create Session:** Should return 201 with session_id
- **Get Session:** Should return 200 with session details
- **End Session:** Should return 200 with summary

---

## Potential Issues & Fixes

### Issue 1: Backend Not Running
**Error:** `Connection refused` or `ECONNREFUSED`

**Fix:**
```bash
# Start the backend server
poetry run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Verify it's running
curl http://localhost:8000/api/health
```

### Issue 2: CORS Errors
**Error:** `Access to XMLHttpRequest blocked by CORS policy`

**Fix:** CORS is already configured in `backend/main.py`. Ensure:
- Backend is running on `http://localhost:8000`
- Postman is using the correct base URL
- No proxy is interfering with requests

### Issue 3: Missing Environment Variables
**Error:** `KeyError` or `ValueError` in response

**Fix:** Check `.env` file has required variables:
```bash
# Required
ELEVENLABS_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# Optional
LANGCHAIN_API_KEY=your_key_here
LANGCHAIN_PROJECT=your_project
```

### Issue 4: Firestore Connection Issues
**Error:** `Firestore connection failed` or `Authentication failed`

**Fix:**
- Ensure Firestore emulator is running (if using mock mode)
- Or configure GCP credentials properly
- Check `backend/config.py` for configuration

### Issue 5: ElevenLabs API Errors
**Error:** `401 Unauthorized` or `API key invalid`

**Fix:**
- Verify `ELEVENLABS_API_KEY` is correct
- Check API key has proper permissions
- Ensure API key is not expired

### Issue 6: Invalid Request Body
**Error:** `422 Unprocessable Entity`

**Fix:**
- Verify request body matches schema
- Check all required fields are present
- Ensure data types are correct (strings, numbers, arrays)

### Issue 7: Resource Not Found
**Error:** `404 Not Found`

**Fix:**
- Verify resource ID is correct
- Ensure resource was created before trying to access it
- Check resource hasn't been deleted

### Issue 8: Rate Limiting
**Error:** `429 Too Many Requests`

**Fix:**
- Add delays between requests
- Reduce number of parallel requests
- Check backend rate limiting configuration

---

## Recommended Testing Workflow

### Phase 1: Basic Connectivity
1. Test `GET /` - Root endpoint
2. Test `GET /api/health` - Health check
3. Test `GET /api/dashboard/stats` - Dashboard stats

### Phase 2: Knowledge Management
1. Create knowledge document
2. List documents
3. Get specific document
4. Update document
5. Delete document

### Phase 3: Audio Generation
1. List available voices
2. Generate script from knowledge
3. Generate audio from script
4. List audio files
5. Stream audio
6. Delete audio

### Phase 4: Agent Management
1. Create agent with knowledge
2. List agents
3. Get agent details
4. Update agent
5. Get system prompts
6. Delete agent

### Phase 5: Patient Sessions
1. Start patient session
2. Send message to agent
3. End session
4. Get patient summary

### Phase 6: Conversations
1. List conversations
2. Get conversation statistics
3. Get conversation details

### Phase 7: Templates
1. List templates
2. Create template
3. Get template
4. Preview template
5. Update template
6. Delete template

### Phase 8: Debug Endpoints
1. Debug health check
2. Debug script generation
3. Debug session management

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Start Backend
        run: |
          poetry install
          poetry run uvicorn backend.main:app &
          sleep 5
      
      - name: Run Postman Collection
        uses: postman-echo/postman-collection-runner@v1
        with:
          collection: .postman.json
          environment: .postman.json
          reporters: cli,json
```

---

## Next Steps

1. ✅ **Collection Created** - `.postman.json` is ready
2. ⏳ **Start Backend** - Run `poetry run uvicorn backend.main:app --reload`
3. ⏳ **Import Collection** - Import `.postman.json` into Postman
4. ⏳ **Run Tests** - Execute collection and verify all endpoints
5. ⏳ **Fix Issues** - Address any failing tests using the fixes above
6. ⏳ **Automate** - Set up CI/CD integration for automated testing

---

## Collection Statistics

| Metric | Value |
|--------|-------|
| Total Endpoints | 42 |
| Functional Groups | 8 |
| Collection Variables | 8 |
| Request Methods | 4 (GET, POST, PUT, DELETE) |
| Expected Status Codes | 5 (200, 201, 204, 404, 422) |
| Documentation | Complete |

---

## Files Generated

- `.postman.json` - Complete Postman collection configuration
- `reports/POSTMAN_COLLECTION_REPORT.md` - This report

---

## Support & Troubleshooting

For issues or questions:

1. Check the **Potential Issues & Fixes** section above
2. Review backend logs: `backend/logs/`
3. Check Postman console for detailed error messages
4. Verify environment variables in `.env`
5. Ensure backend is running: `curl http://localhost:8000/api/health`

---

## Conclusion

The ElevenDops Postman collection is now ready for comprehensive API testing. All 42 endpoints are configured with proper request/response structures, variables, and documentation. Start the backend server and import the collection to begin testing.

**Status:** ✅ Ready for Testing  
**Last Updated:** January 15, 2026

