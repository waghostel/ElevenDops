---
description: How to run the test suite for quality assurance
---

# Test Workflow

This workflow runs the complete test suite for the project.

// turbo-all

## Prerequisites

- Dependencies installed (`pnpm install`)
- Test database configured (for integration tests)

## Steps

### Step 1: Run Unit Tests

```powershell
pnpm run test:unit
```

### Step 2: Run Integration Tests

```powershell
pnpm run test:integration
```

### Step 3: Run End-to-End Tests

```powershell
pnpm run test:e2e
```

### Step 4: Generate Coverage Report

```powershell
pnpm run test:coverage
```

### Step 5: View Coverage Report

```powershell
Start-Process "coverage/index.html"
```

---

## Test Configuration

| Test Type   | Framework  | Location             |
| :---------- | :--------- | :------------------- |
| Unit        | Jest       | `tests/unit/`        |
| Integration | Jest       | `tests/integration/` |
| E2E         | Playwright | `tests/e2e/`         |

---

## Quick Commands

| Command                      | Description        |
| :--------------------------- | :----------------- |
| `pnpm test`                  | Run all tests      |
| `pnpm test -- --watch`       | Run in watch mode  |
| `pnpm test -- --filter=auth` | Run specific tests |

---

## Troubleshooting

### Tests Timeout

Increase timeout in jest.config.js:

```javascript
testTimeout: 30000;
```

### Database Connection Errors

Ensure test database is running:

```powershell
docker-compose up -d test-db
```
