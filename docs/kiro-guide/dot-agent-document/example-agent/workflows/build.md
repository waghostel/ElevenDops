---
description: How to build the project for production
---

# Build Workflow

This workflow compiles and bundles the application for production deployment.

## Prerequisites

- Node.js 18+ installed
- All dependencies installed via `pnpm install`

## Steps

### Step 1: Clean Previous Build

// turbo

```powershell
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
```

### Step 2: Run Type Checking

// turbo

```powershell
pnpm run type-check
```

### Step 3: Run Linting

// turbo

```powershell
pnpm run lint
```

### Step 4: Build Production Bundle

// turbo

```powershell
pnpm run build
```

### Step 5: Verify Build Output

```powershell
Get-ChildItem -Path dist -Recurse | Measure-Object
```

---

## Build Configuration

| Setting          | Value                                        |
| :--------------- | :------------------------------------------- |
| Output Directory | `dist/`                                      |
| Source Maps      | Enabled for staging, disabled for production |
| Minification     | Enabled                                      |
| Tree Shaking     | Enabled                                      |

---

## Troubleshooting

### Build Fails with Type Errors

1. Run `pnpm run type-check` to see detailed errors
2. Fix type issues before rebuilding

### Build Fails with Memory Error

```powershell
$env:NODE_OPTIONS="--max-old-space-size=4096"
pnpm run build
```
