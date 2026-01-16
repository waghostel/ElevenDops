# Deploying to Cloud Run

This guide details the steps to deploy the ElevenDops application (FastAPI Backend + Streamlit Frontend) to Google Cloud Run using a single container strategy.

## Prerequisites

- Completed [Migration to Real GCP](./guide--03-migrate-to-real-gcp.md).
- `gcloud` CLI installed and authenticated.
- A valid `Dockerfile` (using `uv` for dependencies).
- A valid `scripts/start.sh` entrypoint.

---

## Step 0: Verify Active Project

Before running any `gcloud` commands, ensure you are working in the correct project.

1.  **Check Current Project**:

    ```bash
    gcloud config get-value project
    ```

2.  **Set Project (If Incorrect)**:
    ```bash
    gcloud config set project [YOUR_PROJECT_ID]
    ```

---

## Step 1: Initialize Services

Enable the required Google Cloud APIs and prepare the project.

1.  **Enable Required APIs**:

    ```bash
    gcloud services enable artifactregistry.googleapis.com `
        cloudbuild.googleapis.com `
        run.googleapis.com `
        secretmanager.googleapis.com
    ```

2.  **Set Project Variables** (optional, for the commands below):
    ```bash
    $PROJECT_ID = gcloud config get-value project
    $PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"
    ```

---

## Step 2: Configure Secrets (Secret Manager)

We **never** put sensitive API keys in environment variables directly. Use Secret Manager.

1.  **Create Secrets**:

    ```bash
    # ElevenLabs API Key
    echo -n "YOUR_ELEVENLABS_KEY" | gcloud secrets create ELEVENLABS_API_KEY --data-file=-

    # Google API Key (Gemini)
    echo -n "YOUR_GOOGLE_KEY" | gcloud secrets create GOOGLE_API_KEY --data-file=-
    ```

    > [!TIP] > **Windows PowerShell Tip**: If your keys appear "corrupted" (due to UTF-16 encoding), use this instead:
    > `[System.IO.File]::WriteAllBytes("temp.txt", [System.Text.Encoding]::UTF8.GetBytes("YOUR_KEY"))` > `gcloud secrets create MY_SECRET --data-file=temp.txt`

2.  **Grant Secret Access to the Service Account**:
    ```bash
    gcloud projects add-iam-policy-binding $PROJECT_ID `
        --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" `
        --role="roles/secretmanager.secretAccessor"
    ```

---

## Step 3: Grant Mandatory Permissions

The Cloud Run service account needs permission to access your Firestore database and Storage bucket.

```bash
# Grant Firestore User role
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" `
    --role="roles/datastore.user"

# Grant Storage Admin role
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" `
    --role="roles/storage.objectAdmin"
```

---

## Step 4: Build and Deploy (One Command)

We will use the **Deploy from Source** strategy. This automatically builds your image using Cloud Build and deploys it to Cloud Run in one step. It correctly handles custom Dockerfile names.

```bash
# Windows PowerShell example for elevendops-dev
gcloud run deploy elevendops-service `
    --source . `
    --region us-central1 `
    --allow-unauthenticated `
    --port 8080 `
    --set-env-vars "GOOGLE_CLOUD_PROJECT=elevendops-dev,BACKEND_API_URL=http://localhost:8000,USE_FIRESTORE_EMULATOR=false,USE_GCS_EMULATOR=false,GCS_BUCKET_NAME=elevendops-bucket,FIRESTORE_DATABASE_ID=elevendops-db" `
    --set-secrets "ELEVENLABS_API_KEY=ELEVENLABS_API_KEY:latest,GOOGLE_API_KEY=GOOGLE_API_KEY:latest"
```

### Why use --source?

- **All-in-one**: It manages the Artifact Registry and Cloud Build steps for you.
- **Reliable**: It supports the `--dockerfile` flag correctly where `gcloud builds submit` often requires a complex YAML config.

---

## Deployment Reference (elevendops-dev)

Use these values for your current development environment:

| Resource         | Value                |
| :--------------- | :------------------- |
| **Project ID**   | `elevendops-dev`     |
| **Firestore DB** | `elevendops-db`      |
| **GCS Bucket**   | `elevendops-bucket`  |
| **Region**       | `us-central1`        |
| **Service Name** | `elevendops-service` |

---

## Proper Security Setup (Rationale)

This deployment follows **Google Cloud Security Best Practices** to protect your sensitive data:

### 1. Identity-Based Access (The "Who")

We do not use shared passwords or long-lived API keys in the code. Instead, we use **IAM (Identity and Access Management)**.

- Permissions are granted to the **Compute Service Account** (`[NUMBER]-compute@developer.gserviceaccount.com`).
- Only your actual application, running inside Cloud Run, "wears" this identity and inherits these permissions.

### 2. Secret Manager (Encrypted Vault)

Sensitive keys (ElevenLabs, Gemini) are stored in **Secret Manager**, not in the source code or plain environment variables.

- **At Rest**: Keys are encrypted by Google.
- **In Console**: No one can see the values just by looking at the Cloud Run settings.
- **At Runtime**: Cloud Run safely injects the value directly into the container's memory.

### 3. Principle of Least Privilege

The commands in **Step 3** and **Step 3.5** grant just enough power for the app to function:

- `secretAccessor`: Can read the necessary API keys.
- `datastore.user`: Can read/write to the Firestore database.
- `storage.objectAdmin`: Can manage audio files in the GCS bucket.

---

## Managing and Rotating Secrets

To update an API key without changing your deployment settings:

1.  **Add a new version**:
    ```bash
    echo -n "NEW_API_KEY_VALUE" | gcloud secrets versions add ELEVENLABS_API_KEY --data-file=-
    ```
2.  **Redeploy**: Run the `gcloud run deploy` command again. Cloud Run will resolve the `:latest` version and inject the new key into the new containers.

### Advanced Secret Management

- **Delete (Destroy) a Version**:
  ```bash
  gcloud secrets versions destroy [VERSION_NUMBER] --secret=ELEVENLABS_API_KEY
  ```
- **Rollback to a Specific Version**:
  Change the deployment flag from `:latest` to a specific version (e.g., `:1`):
  `--set-secrets "ELEVENLABS_API_KEY=ELEVENLABS_API_KEY:1"`

> [!NOTE] > **Automation Note**: Unlike Artifact Registry, Secret Manager does **not** have an automated "cleanup policy." Old versions are kept for safety/history. Keep them unless a key is leaked, as they use negligible space.

---

## Managing Artifact Registry Space

Every time you deploy, a new image version is stored. Over time, these can add up.

- **Layer Reuse**: Docker only stores the _changes_. If you only change code (not dependencies), the extra space used is very small.
- **Manual Cleanup**: To see your images:
  ```bash
  gcloud artifacts docker images list us-central1-docker.pkg.dev/[PROJECT_ID]/cloud-run-source-deploy/elevendops-service
  ```
- **Automation (Set-and-Forget)**: You can set **Cleanup Policies** in the Artifact Registry console. Once set, Google Cloud automatically runs a background job daily to delete images based on your rules (e.g., "Keep only the 5 most recent images").

---

## Future Automation (CI/CD)

Once you verify the manual deployment works, you can automate it so that every `git push` triggers a new deployment.

### Option A: Cloud Build Triggers (Google-Native)

- **Best for**: Projects staying entirely within GCP.
- **Setup**: Connect your GitHub repo in the **Cloud Build > Triggers** console.
- **Action**: It uses your `cloudbuild.yaml` to build and deploy automatically on every push to the `main` branch.

### Option B: GitHub Actions (Developer Favorite)

- **Best for**: Running tests (Pytest/Jest) before deploying.
- **Setup**: Add a `.github/workflows/deploy.yml` file.
- **Benefit**: You can ensure that "broken" code (failing tests) never reaches your production environment.

---

## Step 5: Verify and Troubleshoot

1.  **Open in Browser**: The URL is in the output (e.g., `https://elevendops-service-xyz.run.app`).
2.  **Check Logs**:
    ```bash
    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=elevendops-service" --limit 20
    ```

### Troubleshooting

- **503 Service Unavailable**:
  - Check `scripts/start.sh` for line endings (must be LF).
  - Check logs for "Backend failed to start".
- **Permission Denied**:
  - Verify Step 3 permissions were applied to the correct `$PROJECT_NUMBER`.
