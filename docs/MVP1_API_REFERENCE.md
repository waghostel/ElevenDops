# MVP1 API Reference

Complete REST API documentation for ElevenDops MVP1 backend.

## Base URL

```
http://localhost:8000
```

## Authentication

MVP1 does not implement authentication. All endpoints are publicly accessible.

**Note**: MVP2 will add authentication and authorization.

## Response Format

All responses follow a consistent JSON format:

### Success Response (2xx)
```json
{
  "status": "success",
  "data": {
    // Response data
  },
  "message": "Operation completed successfully"
}
```

### Error Response (4xx, 5xx)
```json
{
  "status": "error",
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {}
}
```

## API Endpoints

### Knowledge Management

#### Upload Knowledge Document
```
POST /api/knowledge
```

**Request Body:**
```json
{
  "disease_name": "白內障",
  "document_type": "術後照護",
  "raw_content": "# 白內障術後照護\n\n1. 保持眼睛清潔...",
  "doctor_id": "doctor_001"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "knowledge_id": "kb_123456",
    "disease_name": "白內障",
    "document_type": "術後照護",
    "sync_status": "pending",
    "created_at": "2024-12-21T10:30:00Z"
  }
}
```

**Error Responses:**
- `400`: Invalid document format
- `413`: Document too large
- `500`: Firestore error

---

#### Get Knowledge Documents
```
GET /api/knowledge
```

**Query Parameters:**
- `doctor_id` (optional): Filter by doctor
- `disease_name` (optional): Filter by disease
- `limit` (optional, default: 50): Number of results
- `offset` (optional, default: 0): Pagination offset

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "knowledge_id": "kb_123456",
      "disease_name": "白內障",
      "document_type": "術後照護",
      "sync_status": "completed",
      "elevenlabs_document_id": "doc_abc123",
      "created_at": "2024-12-21T10:30:00Z"
    }
  ],
  "total": 1
}
```

---

#### Get Knowledge Document Details
```
GET /api/knowledge/{knowledge_id}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "knowledge_id": "kb_123456",
    "disease_name": "白內障",
    "document_type": "術後照護",
    "raw_content": "# 白內障術後照護\n\n1. 保持眼睛清潔...",
    "sync_status": "completed",
    "elevenlabs_document_id": "doc_abc123",
    "created_at": "2024-12-21T10:30:00Z"
  }
}
```

---

#### Delete Knowledge Document
```
DELETE /api/knowledge/{knowledge_id}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Knowledge document deleted successfully"
}
```

---

### Audio Generation

#### Generate Education Audio
```
POST /api/audio
```

**Request Body:**
```json
{
  "knowledge_id": "kb_123456",
  "script": "白內障是眼睛晶狀體混濁的疾病...",
  "voice_id": "21m00Tcm4TlvDq8ikWAM",
  "doctor_id": "doctor_001"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "audio_id": "audio_789012",
    "knowledge_id": "kb_123456",
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "script": "白內障是眼睛晶狀體混濁的疾病...",
    "audio_url": "http://localhost:4443/storage/v1/b/elevenlabs-audio/o/audio%2Faudio_789012.mp3",
    "duration_seconds": 45,
    "created_at": "2024-12-21T10:35:00Z"
  }
}
```

---

#### Get Audio Files
```
GET /api/audio
```

**Query Parameters:**
- `knowledge_id` (optional): Filter by knowledge document
- `limit` (optional, default: 50): Number of results

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "audio_id": "audio_789012",
      "knowledge_id": "kb_123456",
      "voice_id": "21m00Tcm4TlvDq8ikWAM",
      "audio_url": "http://localhost:4443/storage/v1/b/elevenlabs-audio/o/audio%2Faudio_789012.mp3",
      "duration_seconds": 45,
      "created_at": "2024-12-21T10:35:00Z"
    }
  ],
  "total": 1
}
```

---

#### Get Available Voices
```
GET /api/audio/voices
```

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "voice_id": "21m00Tcm4TlvDq8ikWAM",
      "name": "Rachel",
      "category": "premade",
      "language": "en"
    },
    {
      "voice_id": "EXAVITQu4vr4xnSDxMaL",
      "name": "Bella",
      "category": "premade",
      "language": "en"
    }
  ]
}
```

---

### Agent Management

#### Create AI Agent
```
POST /api/agent
```

**Request Body:**
```json
{
  "name": "白內障衛教助手",
  "knowledge_ids": ["kb_123456", "kb_234567"],
  "voice_id": "21m00Tcm4TlvDq8ikWAM",
  "answer_style": "professional",
  "doctor_id": "doctor_001"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "agent_id": "agent_345678",
    "name": "白內障衛教助手",
    "knowledge_ids": ["kb_123456", "kb_234567"],
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "answer_style": "professional",
    "elevenlabs_agent_id": "agent_abc123xyz",
    "created_at": "2024-12-21T10:40:00Z"
  }
}
```

---

#### Get Agents
```
GET /api/agent
```

**Query Parameters:**
- `doctor_id` (optional): Filter by doctor
- `limit` (optional, default: 50): Number of results

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "agent_id": "agent_345678",
      "name": "白內障衛教助手",
      "knowledge_ids": ["kb_123456", "kb_234567"],
      "voice_id": "21m00Tcm4TlvDq8ikWAM",
      "answer_style": "professional",
      "elevenlabs_agent_id": "agent_abc123xyz",
      "created_at": "2024-12-21T10:40:00Z"
    }
  ],
  "total": 1
}
```

---

#### Get Agent Details
```
GET /api/agent/{agent_id}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "agent_id": "agent_345678",
    "name": "白內障衛教助手",
    "knowledge_ids": ["kb_123456", "kb_234567"],
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "answer_style": "professional",
    "elevenlabs_agent_id": "agent_abc123xyz",
    "created_at": "2024-12-21T10:40:00Z"
  }
}
```

---

#### Update Agent
```
PUT /api/agent/{agent_id}
```

**Request Body:**
```json
{
  "name": "白內障衛教助手 v2",
  "knowledge_ids": ["kb_123456"],
  "answer_style": "friendly"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "agent_id": "agent_345678",
    "name": "白內障衛教助手 v2",
    "knowledge_ids": ["kb_123456"],
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "answer_style": "friendly",
    "updated_at": "2024-12-21T10:45:00Z"
  }
}
```

---

#### Delete Agent
```
DELETE /api/agent/{agent_id}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Agent deleted successfully"
}
```

---

### Patient Conversations

#### Start Conversation
```
POST /api/patient/conversation/start
```

**Request Body:**
```json
{
  "patient_id": "patient_001",
  "agent_id": "agent_345678"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "conversation_id": "conv_567890",
    "patient_id": "patient_001",
    "agent_id": "agent_345678",
    "agent_name": "白內障衛教助手",
    "started_at": "2024-12-21T10:50:00Z"
  }
}
```

---

#### Send Message
```
POST /api/patient/conversation/{conversation_id}/message
```

**Request Body:**
```json
{
  "text": "白內障手術後多久可以洗臉？"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "message_id": "msg_678901",
    "conversation_id": "conv_567890",
    "role": "user",
    "text": "白內障手術後多久可以洗臉？",
    "timestamp": "2024-12-21T10:51:00Z"
  }
}
```

---

#### Get Agent Response
```
GET /api/patient/conversation/{conversation_id}/response
```

**Query Parameters:**
- `message_id` (optional): Get response to specific message

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "message_id": "msg_678902",
    "conversation_id": "conv_567890",
    "role": "agent",
    "text": "白內障手術後通常需要等待1-2週才能洗臉...",
    "audio_url": "http://localhost:4443/storage/v1/b/elevenlabs-audio/o/audio%2Fresponse_678902.mp3",
    "timestamp": "2024-12-21T10:51:30Z"
  }
}
```

---

#### End Conversation
```
POST /api/patient/conversation/{conversation_id}/end
```

**Request Body:**
```json
{
  "satisfaction_score": 4
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "conversation_id": "conv_567890",
    "status": "completed",
    "duration_seconds": 300,
    "message_count": 5,
    "ended_at": "2024-12-21T10:55:00Z"
  }
}
```

---

### Conversation Logs

#### Get Conversation Logs
```
GET /api/conversation/logs
```

**Query Parameters:**
- `patient_id` (optional): Filter by patient
- `agent_id` (optional): Filter by agent
- `doctor_id` (optional): Filter by doctor
- `requires_attention` (optional): Filter by attention flag
- `limit` (optional, default: 50): Number of results
- `offset` (optional, default: 0): Pagination offset

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "conversation_id": "conv_567890",
      "patient_id": "patient_001",
      "agent_id": "agent_345678",
      "agent_name": "白內障衛教助手",
      "requires_attention": false,
      "main_concerns": ["術後護理", "用藥"],
      "answered_questions": 4,
      "unanswered_questions": 1,
      "duration_seconds": 300,
      "created_at": "2024-12-21T10:50:00Z"
    }
  ],
  "total": 1
}
```

---

#### Get Conversation Details
```
GET /api/conversation/{conversation_id}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "conversation_id": "conv_567890",
    "patient_id": "patient_001",
    "agent_id": "agent_345678",
    "agent_name": "白內障衛教助手",
    "messages": [
      {
        "message_id": "msg_678901",
        "role": "user",
        "text": "白內障手術後多久可以洗臉？",
        "timestamp": "2024-12-21T10:51:00Z"
      },
      {
        "message_id": "msg_678902",
        "role": "agent",
        "text": "白內障手術後通常需要等待1-2週才能洗臉...",
        "timestamp": "2024-12-21T10:51:30Z"
      }
    ],
    "requires_attention": false,
    "main_concerns": ["術後護理"],
    "duration_seconds": 300,
    "created_at": "2024-12-21T10:50:00Z"
  }
}
```

---

### Dashboard

#### Get Dashboard Statistics
```
GET /api/dashboard/stats
```

**Query Parameters:**
- `doctor_id` (optional): Filter by doctor

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "total_knowledge_documents": 5,
    "total_agents": 3,
    "total_audio_files": 8,
    "total_conversations": 42,
    "total_patients": 15,
    "last_activity": "2024-12-21T10:55:00Z",
    "conversations_this_week": 12,
    "conversations_this_month": 42
  }
}
```

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Invalid request parameters |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `VALIDATION_ERROR` | 422 | Data validation failed |
| `FIRESTORE_ERROR` | 500 | Database operation failed |
| `ELEVENLABS_ERROR` | 502 | ElevenLabs API error |
| `STORAGE_ERROR` | 500 | File storage operation failed |
| `INTERNAL_ERROR` | 500 | Internal server error |

---

## Rate Limiting

MVP1 does not implement rate limiting. Production (MVP2) will add rate limiting.

---

## Pagination

Endpoints that return lists support pagination:

**Query Parameters:**
- `limit`: Number of results (default: 50, max: 100)
- `offset`: Number of results to skip (default: 0)

**Response:**
```json
{
  "status": "success",
  "data": [...],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

---

## Testing with cURL

### Upload Knowledge
```bash
curl -X POST http://localhost:8000/api/knowledge \
  -H "Content-Type: application/json" \
  -d '{
    "disease_name": "白內障",
    "document_type": "術後照護",
    "raw_content": "# 白內障術後照護\n\n1. 保持眼睛清潔...",
    "doctor_id": "doctor_001"
  }'
```

### Get Knowledge Documents
```bash
curl http://localhost:8000/api/knowledge
```

### Create Agent
```bash
curl -X POST http://localhost:8000/api/agent \
  -H "Content-Type: application/json" \
  -d '{
    "name": "白內障衛教助手",
    "knowledge_ids": ["kb_123456"],
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "answer_style": "professional",
    "doctor_id": "doctor_001"
  }'
```

---

## Testing with Swagger UI

Interactive API documentation available at:
```
http://localhost:8000/docs
```

Use Swagger UI to:
- View all endpoints
- Test API calls
- See request/response examples
- Download OpenAPI specification

---

## WebSocket Endpoints (Future)

The following WebSocket endpoints are planned for Phase 2:

- `WS /api/patient/conversation/{conversation_id}/stream` - Real-time conversation streaming
- `WS /api/audio/stream/{audio_id}` - Real-time audio streaming

---

## Changelog

### Version 1.0 (MVP1)
- Initial API implementation
- Knowledge management endpoints
- Audio generation endpoints
- Agent management endpoints
- Patient conversation endpoints
- Conversation logs endpoints
- Dashboard statistics endpoint
