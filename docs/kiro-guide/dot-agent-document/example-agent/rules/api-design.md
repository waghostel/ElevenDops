# API Design Rules

This document defines the API design standards that MUST be followed for all backend endpoints.

---

## Response Format

All API responses MUST use this consistent envelope:

```json
{
  "data": { ... },
  "error": null,
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "uuid-here"
  }
}
```

### Success Response

```json
{
  "data": {
    "id": "123",
    "name": "Example"
  },
  "error": null
}
```

### Error Response

```json
{
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input provided",
    "details": [{ "field": "email", "message": "Invalid email format" }]
  }
}
```

---

## HTTP Status Codes

| Code | Usage                                       |
| :--- | :------------------------------------------ |
| 200  | Successful GET, PUT, PATCH                  |
| 201  | Successful POST (resource created)          |
| 204  | Successful DELETE (no content)              |
| 400  | Bad Request (validation error)              |
| 401  | Unauthorized (missing/invalid auth)         |
| 403  | Forbidden (insufficient permissions)        |
| 404  | Not Found                                   |
| 409  | Conflict (duplicate resource)               |
| 422  | Unprocessable Entity (business logic error) |
| 500  | Internal Server Error                       |

---

## Error Codes

Use consistent, uppercase error codes:

| Code                   | Description                   |
| :--------------------- | :---------------------------- |
| `VALIDATION_ERROR`     | Input validation failed       |
| `AUTHENTICATION_ERROR` | Auth token missing or invalid |
| `AUTHORIZATION_ERROR`  | User lacks permission         |
| `NOT_FOUND`            | Resource not found            |
| `CONFLICT`             | Resource already exists       |
| `RATE_LIMIT_EXCEEDED`  | Too many requests             |
| `INTERNAL_ERROR`       | Unexpected server error       |

---

## Pagination

Use `offset` and `limit` query parameters:

```
GET /users?offset=20&limit=10
```

Response includes pagination metadata:

```json
{
  "data": [...],
  "meta": {
    "pagination": {
      "offset": 20,
      "limit": 10,
      "total": 150,
      "hasMore": true
    }
  }
}
```

---

## Filtering and Sorting

### Filtering

Use field names as query parameters:

```
GET /users?status=active&role=admin
```

### Sorting

Use `sortBy` and `sortOrder`:

```
GET /users?sortBy=createdAt&sortOrder=desc
```

---

## Versioning

- Include version in URL path: `/api/v1/users`
- Increment major version for breaking changes
- Support previous version for 6 months after new release

---

## Required Headers

| Header          | Description                   |
| :-------------- | :---------------------------- |
| `Authorization` | Bearer token for auth         |
| `Content-Type`  | `application/json`            |
| `X-Request-Id`  | Unique request ID for tracing |
