# API Route Patterns

## Overview

This rule defines the standard patterns for FastAPI API routes in this project.

## Backend Route Endpoint Convention

When defining collection endpoints (list/create) in FastAPI routers:

### ✅ Use empty string `""` (no trailing slash)

```python
router = APIRouter(prefix="/api/resource", tags=["resource"])

@router.get("", response_model=ResourceListResponse)
async def list_resources():
    ...

@router.post("", response_model=ResourceResponse)
async def create_resource():
    ...
```

### ❌ Do NOT use `"/"` (with trailing slash)

```python
# BAD - causes 307 redirects when clients call without trailing slash
@router.get("/", response_model=ResourceListResponse)
async def list_resources():
    ...
```

## Frontend Client Convention

When calling backend APIs from the frontend httpx client:

### ✅ Use URLs WITHOUT trailing slashes

```python
response = await client.post("/api/resource", json=payload)
response = await client.get("/api/resource")
response = await client.delete(f"/api/resource/{resource_id}")
```

### ❌ Do NOT add trailing slashes

```python
# BAD - causes 307 redirect error (httpx doesn't follow POST redirects)
response = await client.post("/api/resource/", json=payload)
```

## Rationale

1. **Consistency**: All routers in this project use `""` for collection endpoints
2. **Avoid 307 Redirects**: FastAPI redirects `/api/resource` → `/api/resource/` when route uses `"/"`
3. **Client Compatibility**: Our frontend httpx client does not follow redirects for POST requests by default

## Existing Pattern Examples

### Backend

- `templates.py`: `@router.get("")`, `@router.post("")`
- `knowledge.py`: `@router.get("")`, `@router.post("")`
- `agent.py`: `@router.get("")`, `@router.post("")`
- `conversation.py`: `@router.get("")`

### Frontend (`backend_api.py`)

- `client.get("/api/templates")`
- `client.post("/api/templates", json=payload)`
- `client.delete(f"/api/templates/{template_id}")`
