# Deploying to Cloud Run

This guide details the steps to deploy the ElevenDops application (FastAPI Backend + Streamlit Frontend) to Google Cloud Run using a single container strategy.

## Prerequisites

- Completed [Migration to Real GCP](./guide--03-migrate-to-real-gcp.md).
- `gcloud` CLI installed and authenticated.
- A valid `Dockerfile.cloudrun` (using `uv` for dependencies).
- A valid `scripts/start.sh` entrypoint.

---

## Step 1: Initialize Artifact Registry

Artifact Registry is where your Docker images will be stored.

1.  **Enable Artifact Registry API** (if not done):

    ```bash
    gcloud services enable artifactregistry.googleapis.com cloudbuild.googleapis.com run.googleapis.com secretmanager.googleapis.com
    ```

2.  **Create a Repository**:

    ```bash
    gcloud artifacts repositories create elevendops-repo \
        --repository-format=docker \
        --location=asia-east1 \
        --description="Docker repository for ElevenDops"
    ```

3.  **Configure Docker to authenticate** (Optional, for local builds):
    ```bash
    gcloud auth configure-docker asia-east1-docker.pkg.dev
    ```

---

## Step 2: Build and Push Image

We will use **Cloud Build** to build the image remotely and push it to Artifact Registry. This avoids needing Docker installed locally and is faster.

1.  **Set Project ID Variable** (for convenience):

    ```bash
    # Windows PowerShell
    $PROJECT_ID = gcloud config get-value project

    # Verify
    echo $PROJECT_ID
    ```

2.  **Submit Build**:

    ```bash
    gcloud builds submit --tag asia-east1-docker.pkg.dev/$PROJECT_ID/elevendops-repo/elevendops-app:latest --file Dockerfile.cloudrun .
    ```

    > **Note**: This may take 2-3 minutes. It uploads your source code, builds the `Dockerfile.cloudrun` using `uv`, and stores the image.

---

## Step 3: Configure Secrets (Secret Manager)

We **never** put sensitive API keys in environment variables directly. Use Secret Manager.

1.  **Create Secrets**:

    ```bash
    # ElevenLabs API Key
    echo -n "YOUR_ELEVENLABS_KEY" | gcloud secrets create ELEVENLABS_API_KEY --data-file=-

    # Google API Key (Gemini)
    echo -n "YOUR_GOOGLE_KEY" | gcloud secrets create GOOGLE_API_KEY --data-file=-
    ```

2.  **Grant Access to Cloud Run Service Account**:
    Cloud Run uses the **Default Compute Service Account** by default.
    _(ID: `[PROJECT_NUMBER]-compute@developer.gserviceaccount.com`)_.

    ```bash
    # Get Project Number
    $PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"

    # Grant Secret Accessor role
    gcloud projects add-iam-policy-binding $PROJECT_ID `
        --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" `
        --role="roles/secretmanager.secretAccessor"
    ```

---

## Step 4: Deploy to Cloud Run

Now deploy the image. We map ports and link secrets here.

```bash
gcloud run deploy elevendops-service `
    --image asia-east1-docker.pkg.dev/$PROJECT_ID/elevendops-repo/elevendops-app:latest `
    --region asia-east1 `
    --platform managed `
    --allow-unauthenticated `
    --port 8080 `
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,USE_FIRESTORE_EMULATOR=false,USE_GCS_EMULATOR=false,GCS_BUCKET_NAME=elevendops-bucket,FIRESTORE_DATABASE_ID=elevendops-db" `
    --set-secrets "ELEVENLABS_API_KEY=ELEVENLABS_API_KEY:latest,GOOGLE_API_KEY=GOOGLE_API_KEY:latest"
```

### Explanation of Flags:

- `--allow-unauthenticated`: Makes the web app public. Remove this if you perform your own auth proxy.
- `--port 8080`: Cloud Run expects the container to listen on this port. Our `start.sh` and Dockerfile are configured for it.
- `--set-secrets`: Injects the secret value from Secret Manager into the container as an environment variable at runtime.

---

## Step 5: Verify Deployment

1.  **Get the URL**: The command output will show `Service URL: https://elevendops-service-xyz-run.app`.
2.  **Open in Browser**: You should see the Streamlit interface.
3.  **Check Logs**:
    ```bash
    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=elevendops-service" --limit 20
    ```

## Troubleshooting

- **503 Service Unavailable**:

  - Check if the container started within the timeout.
  - Check logs: `Backend failed to start`.
  - Increase memory if needed: `--memory 2Gi --cpu 2`.

- **Permission Denied (GCS/Firestore)**:
  - Ensure the Cloud Run Service Account has `roles/datastore.user` and `roles/storage.objectAdmin`.
  - Run:
    ```bash
    gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" --role="roles/datastore.user"
    gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" --role="roles/storage.objectAdmin"
    ```
