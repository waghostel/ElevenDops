# Code Quality Rules

This document defines the code quality standards that MUST be followed in all code.

---

## General Principles

1. **Clarity over cleverness** - Write code that is easy to read and understand
2. **DRY (Don't Repeat Yourself)** - Extract duplicate logic into reusable functions
3. **Single Responsibility** - Each function/class should do one thing well
4. **Fail Fast** - Validate inputs early and return/throw immediately on error
5. **Document the Why** - Comments explain WHY, not WHAT the code does

---

## Function Guidelines

### DO's ✅

- Keep functions under 30 lines when possible
- Use descriptive names that indicate what the function does
- Accept configuration objects for functions with 3+ parameters
- Return early to avoid deep nesting
- Include type annotations/hints

### DON'Ts ❌

- Don't use magic numbers - define constants
- Don't catch generic exceptions without re-throwing
- Don't leave commented-out code in production
- Don't use `any` type in TypeScript
- Don't use `print` statements - use proper logging

---

## Error Handling

### Python

```python
# ✅ Correct - Specific exception handling
try:
    result = process_data(input_data)
except ValidationError as e:
    logger.warning(f"Validation failed: {e}")
    raise HTTPException(status_code=400, detail=str(e))
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Internal error")
```

```python
# ❌ Incorrect - Generic exception handling
try:
    result = process_data(input_data)
except Exception as e:
    print(e)  # Never do this
```

### TypeScript

```typescript
// ✅ Correct - Type-safe error handling
try {
  const result = await processData(inputData);
  return { data: result, error: null };
} catch (error) {
  if (error instanceof ValidationError) {
    return {
      data: null,
      error: { code: "VALIDATION_ERROR", message: error.message },
    };
  }
  throw error; // Re-throw unexpected errors
}
```

---

## Logging

### Log Levels

| Level      | Usage                             |
| :--------- | :-------------------------------- |
| `DEBUG`    | Detailed diagnostic information   |
| `INFO`     | General operational events        |
| `WARNING`  | Unexpected but handled situations |
| `ERROR`    | Errors that need attention        |
| `CRITICAL` | System failures                   |

### What to Log

- ✅ API requests with method, path, status, duration
- ✅ Error details with stack traces
- ✅ Business events (user created, order placed)
- ❌ Sensitive data (passwords, tokens, PII)
- ❌ High-frequency debug logs in production

---

## Testing Requirements

- Minimum 80% code coverage for new code
- All public functions must have unit tests
- All API endpoints must have integration tests
- Use property-based testing for data transformations

---

## Security

- Never hardcode secrets or API keys
- Always validate and sanitize user input
- Use parameterized queries to prevent SQL injection
- Implement rate limiting on public endpoints
- Log security-relevant events (login attempts, permission changes)
