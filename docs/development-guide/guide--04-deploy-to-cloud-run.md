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

# Grant Service Account Token Creator role (REQUIRED for Signed URLs)
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" `
    --role="roles/iam.serviceAccountTokenCreator"
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

### What is Deployed?

When you run `gcloud run deploy --source .`, Google Cloud:

1.  **Takes a Snapshot**: Captures the current files in your local directory (saved changes).
2.  **Respects Ignores**: It uses your `.gcloudignore` or `.gitignore` to skip temporary files.
3.  **Builds Remotely**: It uploads the code to Cloud Build, which builds the Docker image.
4.  **Deploys**: It creates a new revision on Cloud Run from that image.

> [!IMPORTANT]
> This command deploys the **code on your disk**, not necessarily what is committed to Git. Ensure you have saved all files before running.

### Why use --source?

- **All-in-one**: It manages the Artifact Registry and Cloud Build steps for you.
- **Reliable**: It supports the `--dockerfile` flag correctly where `gcloud builds submit` often requires a complex YAML config.

---

## Step 4.5: Deploy a Demo Version (Optional)

To deploy a **budget-controlled demo** for public showcases, add the `DEMO_MODE` environment variable:

```bash
# Windows PowerShell example for elevendops-demo
gcloud run deploy elevendops-demo `
    --source . `
    --region us-central1 `
    --allow-unauthenticated `
    --port 8080 `
    --set-env-vars "DEMO_MODE=true,GOOGLE_CLOUD_PROJECT=elevendops-dev,BACKEND_API_URL=http://localhost:8000,USE_FIRESTORE_EMULATOR=false,USE_GCS_EMULATOR=false,GCS_BUCKET_NAME=elevendops-bucket,FIRESTORE_DATABASE_ID=elevendops-db" `
    --set-secrets "ELEVENLABS_API_KEY=ELEVENLABS_API_KEY:latest,GOOGLE_API_KEY=GOOGLE_API_KEY:latest"
```

> [!NOTE]
> The application now uses **Signed GCS URLs** for audio playback. This is more secure and efficient as it allows the browser to download audio directly from GCS without routing through the backend.

### Demo Mode Restrictions

When `DEMO_MODE=true`:

| Feature              | Behavior                               |
| :------------------- | :------------------------------------- |
| **Chat Mode Toggle** | Forced to Text-Only (no TTS synthesis) |
| **Delete Knowledge** | Button disabled                        |
| **Delete Agent**     | Button disabled                        |
| **Delete Audio**     | Button disabled                        |
| **Delete Template**  | Button disabled                        |
| **Create/Upload**    | All creation features remain enabled   |

> [!NOTE]
> Demo mode only affects the **frontend UI**. Backend API endpoints are not restricted.

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

### Recent Successful Deployments

| Date       | Service Name      | Revision                    | Note                 |
| :--------- | :---------------- | :-------------------------- | :------------------- |
| 2026-01-16 | `elevendops-demo` | `elevendops-demo-00001-qps` | First successful run |

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
- `iam.serviceAccountTokenCreator`: Can sign GCS URLs for browser playback.

---

## Managing and Rotating Secrets

To update an API key (ElevenLabs or Gemini) without changing your deployment settings:

### Update ElevenLabs API Key

```bash
echo -n "YOUR_NEW_ELEVENLABS_KEY" | gcloud secrets versions add ELEVENLABS_API_KEY --data-file=-
```

### Update Google (Gemini) API Key

```bash
echo -n "YOUR_NEW_GEMINI_KEY" | gcloud secrets versions add GOOGLE_API_KEY --data-file=-
```

> [!TIP] > **Windows/PowerShell Encoding Tip**: If keys appear corrupted (PowerShell's `echo` adds invisible characters), use this safer method:
>
> ```powershell
> [System.IO.File]::WriteAllBytes("temp_key.txt", [System.Text.Encoding]::UTF8.GetBytes("YOUR_NEW_KEY"))
> gcloud secrets versions add GOOGLE_API_KEY --data-file=temp_key.txt
> Remove-Item temp_key.txt
> ```

### Which Version is Used?

When you have multiple versions enabled (e.g., version 1 and 2), **`:latest` always picks the highest enabled version number**. In this example, version 2 will be used.

- `:latest` → Highest enabled version (dynamic)
- `:1` → Exactly version 1 (pinned)

### Activate the New Key

After adding a new version, trigger a new deployment so Cloud Run fetches the latest secret:

```bash
# Option A: Full redeploy
gcloud run deploy elevendops-service --source . --region us-central1 ...

# Option B: Fast restart (no code changes)
gcloud run services update elevendops-service --region us-central1
```

### Verify

Check that the new version was created by listing the secret versions:

```bash
gcloud secrets versions list GOOGLE_API_KEY
gcloud secrets versions list ELEVENLABS_API_KEY
```

You should see a new version (e.g., version 2 or 3) marked as **Enabled**.

### Advanced Secret Management

- **Delete (Destroy) a Version**:
  ```bash
  gcloud secrets versions destroy [VERSION_NUMBER] --secret=ELEVENLABS_API_KEY
  ```
- **Rollback to a Specific Version**:
  Change the deployment flag from `:latest` to a specific version (e.g., `:1`):
  `--set-secrets "ELEVENLABS_API_KEY=ELEVENLABS_API_KEY:1"`

> [!NOTE] > **Automation Note**: Unlike Artifact Registry, Secret Manager does **not** have an automated "cleanup policy." Old versions are kept for safety/history. Keep them unless a key is leaked, as they use negligible space.

> [!WARNING] > **No Automatic Fallback**: If the latest secret version contains an invalid key (e.g., revoked by the provider), Secret Manager will NOT automatically try older versions. The app will simply fail with authentication errors. You must manually rollback by pinning to a known-good version (e.g., `:1`) or add a new valid key.

---

## Managing Artifact Registry Space

Every time you run `gcloud run deploy --source .`, a **new image** is created and stored in Artifact Registry. Over time, these can add up significantly (~350 MB per image).

### Deploy vs Update: Choosing the Right Command

| Action                           | Command                        | New Image? | Time    | Storage Impact |
| :------------------------------- | :----------------------------- | :--------- | :------ | :------------- |
| **Changed Code** (`.py`, `.css`) | `gcloud run deploy --source .` | **Yes**    | 3-5 min | +350 MB        |
| **Changed Env Vars**             | `gcloud run services update`   | **No**     | ~30 sec | **0 bytes**    |
| **Rotated API Keys**             | `gcloud run services update`   | **No**     | ~30 sec | **0 bytes**    |

**Example: Update environment variables without rebuilding:**

```bash
gcloud run services update elevendops-demo `
    --region us-central1 `
    --set-env-vars "DEMO_MODE=false"
```

> [!TIP]
> Use `services update` whenever you only need to change settings. It's faster and doesn't consume any additional storage.

### Checking Storage Usage

To see all images and their sizes:

```bash
gcloud artifacts docker images list us-central1-docker.pkg.dev/elevendops-dev/cloud-run-source-deploy --sort-by=~CREATE_TIME
```

This will show each image with its digest, create time, and size in bytes.

### Manual Cleanup

To delete a specific old image version:

```bash
gcloud artifacts docker images delete us-central1-docker.pkg.dev/elevendops-dev/cloud-run-source-deploy/elevendops-service@sha256:[DIGEST] --delete-tags --quiet
```

> [!WARNING]
> Do NOT delete the image currently deployed to Cloud Run. Only delete older versions that are no longer in use.

### Automated Cleanup Policies (Recommended)

Instead of manual cleanup, configure automatic deletion:

1.  Go to **GCP Console** → **Artifact Registry** → **Repositories**.
2.  Click on `cloud-run-source-deploy`.
3.  Click **Cleanup Policies** tab.
4.  Create a policy with rules like:
    - **Keep**: Only the 3 most recent images per package.
    - **Delete**: Images older than 7 days (except those tagged `latest`).

Once set, Google Cloud automatically runs a daily background job to enforce these rules.

### Storage Cost Reference

- **Free Tier**: ~0.5 GB/month.
- **After Free Tier**: ~$0.10 per GB/month.
- **Example**: 1.2 GB stored = ~$0.07/month after free tier.

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

---

## Monitoring and Stopping

Cloud Run is "Pay-as-you-go" and scales to zero when not in use.

- **Check Status**: Use the Google Cloud Console or `gcloud run services list`.
- **Pause Access (Make Private)**:
  ```bash
  gcloud run services remove-iam-policy-binding elevendops-service \
      --member="allUsers" --role="roles/run.invoker" --region=us-central1
  ```
- **Turn Back On (Make Public)**:
  ```bash
  gcloud run services add-iam-policy-binding elevendops-service \
      --member="allUsers" --role="roles/run.invoker" --region=us-central1
  ```
- **Total Shutdown (Delete Service)**:

```bash
gcloud run services delete elevendops-service --region=us-central1
```

_Note: Deleting the service does NOT delete your Docker images in the Registry. You can redeploy anytime._

### Troubleshooting

- **503 Service Unavailable**:
  - Check `scripts/start.sh` for line endings (must be LF).
  - Check logs for "Backend failed to start".
- **Permission Denied**:
  - Verify Step 3 permissions were applied to the correct `$PROJECT_NUMBER`.
  - Specifically, ensure `iam.serviceAccountTokenCreator` is granted if audio is not playing.
