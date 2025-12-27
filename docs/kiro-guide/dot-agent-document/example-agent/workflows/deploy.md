---
description: How to deploy the application to staging or production
---

# Deploy Workflow

This workflow deploys the application to the target environment.

## Prerequisites

- Build completed successfully (run `/build` first)
- Required environment variables configured
- Deployment credentials available

## Steps

### Step 1: Verify Build Exists

```powershell
if (-not (Test-Path "dist")) {
    Write-Error "Build directory not found. Run /build first."
    exit 1
}
```

### Step 2: Select Environment

Choose deployment target:

- **Staging**: For testing and QA
- **Production**: For live users

### Step 3: Deploy to Staging

```powershell
# Deploy to staging environment
pnpm run deploy:staging
```

### Step 4: Deploy to Production

> [!CAUTION]
> Production deployment requires explicit user confirmation.

```powershell
# Deploy to production environment
pnpm run deploy:production
```

### Step 5: Verify Deployment

```powershell
# Health check
Invoke-WebRequest -Uri "https://api.example.com/health" -Method GET
```

---

## Environment Configuration

| Environment | URL                 | Branch    |
| :---------- | :------------------ | :-------- |
| Staging     | staging.example.com | `develop` |
| Production  | example.com         | `main`    |

---

## Rollback Procedure

If deployment fails:

```powershell
# Rollback to previous version
pnpm run rollback
```
