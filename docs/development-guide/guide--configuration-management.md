# Configuration Management Guide

This guide explains how to manage application parameters across different development stages (Local, Staging, Production).

---

## 🚀 Overview

ElevenDops uses a multi-layered configuration strategy:

1.  **`.env` File**: Primary source for local development.
2.  **`backend/config.py` Defaults**: Safety fallback values (test environment).
3.  **`cloudbuild.yaml` Substitutions**: Centralized configuration for cloud deployment.
4.  **Google Secret Manager**: For sensitive keys (API Keys, etc.).

---

## 💻 Development Stage (Local)

In development, the system reads settings from the `.env` file in the root directory.

### Quick Setup

1.  Copy `.env.example` to `.env`.
2.  Configure your local values (e.g., `GCS_BUCKET_NAME=elevendops-bucket`).
3.  The backend (FastAPI) uses `pydantic-settings` to automatically load these values.

### Safety Mechanism

If a variable is missing from `.env`, `backend/config.py` provides safety defaults that point to **test resources** (e.g., `elevendops-bucket-test`). This prevents accidental connection to production resources if the `.env` file is misconfigured.

---

## ☁️ Production Stage (Cloud Run)

For production, settings are defined in the deployment pipeline. **The `.env` file is NOT used in Cloud Run.**

### 1. Centralized Management (`cloudbuild.yaml`)

We use **Substitution Variables** in `cloudbuild.yaml` to manage environment-specific values:

```yaml
substitutions:
  _GCS_BUCKET_NAME: "elevendops-bucket"
  _FIRESTORE_DATABASE_ID: "elevendops-db"
```

These variables are injected into the `--set-env-vars` flag during the `gcloud run deploy` step:

```yaml
--set-env-vars=GCS_BUCKET_NAME=${_GCS_BUCKET_NAME},FIRESTORE_DATABASE_ID=${_FIRESTORE_DATABASE_ID},...
```

### 2. Sensitive Keys (Secret Manager)

API keys and secrets are never stored in YAML files. They are referenced from Secret Manager:

```yaml
--set-secrets=ELEVENLABS_API_KEY=elevenlabs-api-key:latest,...
```

---

## 📊 Summary of Configuration Flow

| Component        | Dev Source       | Prod Source                 | Fallback Default         |
| :--------------- | :--------------- | :-------------------------- | :----------------------- |
| **GCS Bucket**   | `.env`           | `cloudbuild.yaml`           | `elevendops-bucket-test` |
| **Firestore DB** | `.env`           | `cloudbuild.yaml`           | `elevendops-db-test`     |
| **API Keys**     | `.env`           | Secret Manager              | `None` (Error)           |
| **Debug Mode**   | `.env` (`true`)  | `cloudbuild.yaml` (`false`) | `true`                   |
| **Demo Mode**    | `.env` (`false`) | `cloudbuild.yaml` (`true`)  | `false`                  |

---

## 🛠️ How to Change a Parameter

### To change a value for Local Development:

Update the value in your local `.env` file. Restart the servers.

### To change a value for Production Deployment:

1.  Open `cloudbuild.yaml`.
2.  Update the value in the `substitutions` section.
3.  Commit and push to trigger a new build.

> [!IMPORTANT]
> Always ensure that `deploy/service.yaml` is kept in sync if you perform manual deployments via `gcloud run services replace`.
