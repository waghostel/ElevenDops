# Guide: Cloud Run Database Configuration

This guide explains how to correctly configure the Firestore database and Google Cloud Storage bucket for your Cloud Run deployment (`elevendops`).

## Overview

The application is designed to be **environment-agnostic**. It does not hardcode database names or bucket paths. instead, it relies on environment variables injected at runtime.

**Core Variables:**

- `FIRESTORE_DATABASE_ID`: The ID of your Firestore database (e.g., `elevendops-db`).
- `GCS_BUCKET_NAME`: The name of your GCS bucket (e.g., `elevendops-audio`).
- `GOOGLE_CLOUD_PROJECT`: Your GCP Project ID.

## ⚡ Quick Reference: What Goes Where?

| Variable Name             | Example Value      | Where to Set? | command flag     |
| :------------------------ | :----------------- | :------------ | :--------------- |
| **FIRESTORE_DATABASE_ID** | `elevendops-db`    | **Env Vars**  | `--set-env-vars` |
| **GCS_BUCKET_NAME**       | `elevendops-audio` | **Env Vars**  | `--set-env-vars` |
| **GOOGLE_CLOUD_PROJECT**  | `your-project-id`  | **Env Vars**  | `--set-env-vars` |
| **APP_ENV**               | `production`       | **Env Vars**  | `--set-env-vars` |
| **ELEVENLABS_API_KEY**    | `sk_...`           | **Secrets**   | `--set-secrets`  |
| **GOOGLE_API_KEY**        | `AIza...`          | **Secrets**   | `--set-secrets`  |
| **LANGSMITH_API_KEY**     | `lsv2...`          | **Secrets**   | `--set-secrets`  |

---

## 1. Dynamic Database Selection

### The Mechanism

The backend uses `pydantic-settings` (in `backend/config.py`) to load configuration.

- **Defaults**: If `FIRESTORE_DATABASE_ID` is missing, it defaults to `(default)`.
- **Production**: In almost all configured environments, you are likely using a named database (e.g., `elevendops-db`) rather than the default one. **You must set this variable explicitly.**

### Verification

You can verify the active database by hitting the debug endpoint (if enabled) or checking the logs during startup:

```text
INFO:backend.services.firestore_service:Firestore client initialized for project [PROJECT_ID], database [DATABASE_ID]
```

---

## 2. Configuring Cloud Run

Since the `Dockerfile` does not hardcode these values, you must provide them during the deployment process.

### Option A: Command Line Deployment (Recommended)

Add the `--set-env-vars` flag to your `gcloud run deploy` command.

```bash
gcloud run deploy elevendops \
  --image gcr.io/YOUR_PROJECT/elevendops \
  --platform managed \
  --region us-central1 \
  --set-env-vars FIRESTORE_DATABASE_ID=elevendops-db \
  --set-env-vars GCS_BUCKET_NAME=elevendops-unique-bucket-name
```

_Note: Cloud Run persists these variables for future revisions. You only need to set them once or when they change._

### Option B: Google Cloud Console (UI)

1. Go to the **Cloud Run** section in the Google Cloud Console.
2. Select your service (`elevendops`).
3. Click **Edit & Deploy New Revision**.
4. Go to the **Container** tab.
5. Scroll to **Environment variables**.
6. Add the following:
   - Name: `FIRESTORE_DATABASE_ID`, Value: `elevendops-db`
   - Name: `GCS_BUCKET_NAME`, Value: `your-bucket-name`
7. Click **Deploy**.

### Option C: Updating Existing Service

To update configuration without a full re-deploy/re-build:

```bash
gcloud run services update elevendops \
  --set-env-vars FIRESTORE_DATABASE_ID=elevendops-db
```

---

## 4. Setting API Keys (Secrets)

For sensitive values like API keys, **do not** use plain environment variables. Use **Google Secret Manager**.

### Quick Command

```bash
gcloud run deploy elevendops \
  --set-secrets ELEVENLABS_API_KEY=elevenlabs-api-key:latest \
  --set-secrets GOOGLE_API_KEY=google-api-key:latest
```

For a full guide on creating and managing these secrets, see:
👉 **[Secret Management Guide](./guide--secret-management.md)**

---

## 5. Local Development vs. Production

| Feature            | Local (`.env`)                             | Cloud Run (Env Vars)              |
| :----------------- | :----------------------------------------- | :-------------------------------- |
| **Config Source**  | `.env` file                                | Service Configuration             |
| **Loader**         | `verify--gcp-migration.ps1`                | Native container runtime          |
| **Common Pitfall** | Script not passing variables to subprocess | Forgetting to set vars in Console |

> [!IMPORTANT] > **Debugging Tip**: If your application works locally but shows "No Data" or empty lists in Cloud Run, you have likely forgotten to set `FIRESTORE_DATABASE_ID`. The app is connecting to the empty `(default)` database.

## Related Documentation

- [Environment Variables Reference](./reference--environment-variables.md)
- [Troubleshooting Guide](./guide--troubleshooting.md)
