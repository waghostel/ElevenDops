# Postman Kiro Power - Efficient Backend API Testing Guide

> **Purpose:** This document is designed to be read by LLM agents to rapidly test backend APIs using the Postman Kiro Power. Follow these instructions for efficient, automated API testing.

## Quick Start for LLM Agents

### Step 1: Check Existing Configuration

First, read the `.postman.json` file in the project root to get existing Postman configuration:

```
Read file: .postman.json
```

This file contains:
- `workspace_id` - Postman workspace identifier
- `collection_id` - Collection to run tests against
- `collection_uid` - Full collection UID (owner-collection format)
- `environment_id` - Environment with variables
- `base_url` - Backend server URL (typically `http://localhost:8000`)

### Step 2: Activate the Postman Power

**ALWAYS activate before using any tools:**

```
kiroPowers action="activate" powerName="postman"
```

This returns:
- Available tools and their parameters
- Server name (always `postman`)
- Documentation and steering files

### Step 3: Verify Backend is Running

Before running tests, verify the backend server is accessible:

```bash
curl http://localhost:8000/api/health
```

If not running, start it:
```powershell
.\scripts\start_server.ps1
```

### Step 4: Run Collection Tests

Execute the collection with environment:

```
kiroPowers action="use" powerName="postman" serverName="postman" toolName="runCollection"
arguments={
  "collectionId": "<collection_uid from .postman.json>",
  "environmentId": "<environment_id from .postman.json>"
}
```

## Essential Postman Power Tools

### 1. runCollection (Primary Testing Tool)
**Purpose:** Execute all requests in a collection with test assertions

```json
{
  "collectionId": "42874768-a6cba9d4-f943-4f64-b6f1-b803ce2bb869",
  "environmentId": "a3bf18a2-9357-4834-a978-7b6049aa0292",
  "stopOnError": false,
  "stopOnFailure": false,
  "iterationCount": 1,
  "requestTimeout": 60000
}
```

### 2. getCollection (Inspect Collection)
**Purpose:** View collection structure and requests

```json
{
  "collectionId": "42874768-a6cba9d4-f943-4f64-b6f1-b803ce2bb869",
  "model": "full"
}
```

### 3. getEnvironment (Check Variables)
**Purpose:** Verify environment variables are set correctly

```json
{
  "environmentId": "a3bf18a2-9357-4834-a978-7b6049aa0292"
}
```

### 4. createCollection (Create New Tests)
**Purpose:** Create a new test collection

```json
{
  "workspace": "<workspace_id>",
  "collection": {
    "info": {
      "name": "Collection Name",
      "description": "Description",
      "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
      {
        "name": "Request Name",
        "request": {
          "method": "GET",
          "header": [],
          "url": {
            "raw": "{{base_url}}/api/endpoint",
            "host": ["{{base_url}}"],
            "path": ["api", "endpoint"]
          }
        },
        "event": [
          {
            "listen": "test",
            "script": {
              "exec": [
                "pm.test('Status code is 200', function () {",
                "    pm.response.to.have.status(200);",
                "});"
              ],
              "type": "text/javascript"
            }
          }
        ]
      }
    ],
    "variable": [
      {"key": "base_url", "value": "http://localhost:8000"}
    ]
  }
}
```

### 5. createEnvironment (Setup Variables)
**Purpose:** Create environment with variables

```json
{
  "workspace": "<workspace_id>",
  "environment": {
    "name": "Environment Name",
    "values": [
      {"key": "base_url", "value": "http://localhost:8000", "enabled": true},
      {"key": "api_key", "value": "", "enabled": true}
    ]
  }
}
```

## ElevenDops Project-Specific Configuration

### Current Postman Setup
```json
{
  "workspace_id": "bb2d5c64-2218-483c-8480-10a802b15e5e",
  "collection_id": "a6cba9d4-f943-4f64-b6f1-b803ce2bb869",
  "collection_uid": "42874768-a6cba9d4-f943-4f64-b6f1-b803ce2bb869",
  "environment_id": "a3bf18a2-9357-4834-a978-7b6049aa0292",
  "base_url": "http://localhost:8000"
}
```

### API Endpoints to Test
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Root - API info |
| `/api/health` | GET | Health check |
| `/api/health/ready` | GET | Readiness probe |
| `/api/dashboard/stats` | GET | Dashboard statistics |
| `/api/knowledge` | GET | List knowledge docs |
| `/api/knowledge` | POST | Create knowledge doc |
| `/api/audio/voices/list` | GET | Available voices |
| `/api/agent` | GET | List agents |
| `/api/conversations` | GET | List conversations |
| `/api/conversations/statistics` | GET | Conversation stats |

## Efficient Testing Workflow

### Workflow 1: Quick Health Check
```
1. Read .postman.json
2. Activate postman power
3. curl http://localhost:8000/api/health
4. If healthy, run collection
```

### Workflow 2: Full API Test
```
1. Read .postman.json
2. Activate postman power
3. Start backend if needed: .\scripts\start_server.ps1
4. Run collection with environment
5. Analyze results
6. Update .postman.json with test results
```

### Workflow 3: Create New Tests
```
1. Activate postman power
2. Get workspace ID from .postman.json
3. Create collection with test requests
4. Create/update environment
5. Run collection
6. Update .postman.json with new IDs
```

## Test Script Patterns

### Basic Status Check
```javascript
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
```

### Response Structure Validation
```javascript
pm.test('Response has required fields', function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('status');
    pm.expect(jsonData).to.have.property('data');
});
```

### Save Variable for Chaining
```javascript
pm.test('Save ID for next request', function () {
    const jsonData = pm.response.json();
    pm.collectionVariables.set('item_id', jsonData.id);
});
```

### Multiple Status Codes
```javascript
pm.test('Status code is 200 or 201', function () {
    pm.expect(pm.response.code).to.be.oneOf([200, 201]);
});
```

## Troubleshooting

### Issue: Collection Not Found (404)
**Solution:** Verify collection_uid format is `owner_id-collection_id`

### Issue: Tests Fail with Connection Error
**Solution:** 
1. Check backend is running: `curl http://localhost:8000/`
2. Start backend: `.\scripts\start_server.ps1`

### Issue: Environment Variables Not Resolved
**Solution:** 
1. Verify environment_id is correct
2. Check environment has `base_url` variable set

### Issue: Postman API Rate Limits
**Solution:** Add delays between requests or reduce iteration count

## Best Practices for LLM Agents

1. **Always read `.postman.json` first** - Contains all necessary IDs
2. **Activate power before using** - Required for tool access
3. **Verify backend health** - Use curl before running tests
4. **Use environment variables** - Don't hardcode URLs
5. **Update `.postman.json`** - Keep configuration current after changes
6. **Handle failures gracefully** - Check response codes before assertions
7. **Use collection_uid format** - `owner_id-collection_id` for runCollection

## Quick Reference Commands

```
# Activate power
kiroPowers action="activate" powerName="postman"

# Run tests
kiroPowers action="use" powerName="postman" serverName="postman" toolName="runCollection" arguments={"collectionId": "...", "environmentId": "..."}

# Get collection details
kiroPowers action="use" powerName="postman" serverName="postman" toolName="getCollection" arguments={"collectionId": "..."}

# List workspaces
kiroPowers action="use" powerName="postman" serverName="postman" toolName="getWorkspaces"

# Get environment
kiroPowers action="use" powerName="postman" serverName="postman" toolName="getEnvironment" arguments={"environmentId": "..."}
```

---

**Document Version:** 1.0  
**Last Updated:** December 23, 2025  
**For Use By:** LLM Agents (Kiro, Claude, etc.)