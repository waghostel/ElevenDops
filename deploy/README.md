# ElevenDops Cloud Run Deployment Guide

This guide covers deploying the ElevenDops medical assistant system to Google Cloud Run.

## Prerequisites

### Required GCP APIs

Enable the following APIs in your GCP project:

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    firestore.googleapis.com \
    storage.googleapis.com
```

### Required Resources

Before deployment, ensure you have:

- [ ] GCP project with billing enabled
- [ ] Firestore database created (Native mode)
- [ ] Cloud Storage bucket for audio files
- [ ] API keys for ElevenLabs, Google AI, and LangSmith

## Secret Setup

Create secrets in Secret Manager for sensitive API keys:

```bash
# Create ElevenLabs API key secret
gcloud secrets create elevenlabs-api-key --replication-policy="automatic"
echo -n "YOUR_ELEVENLABS_API_KEY" | gcloud secrets versions add elevenlabs-api-key --data-file=-

# Create Google API key secret
gcloud secrets create google-api-key --replication-policy="automatic"
echo -n "YOUR_GOOGLE_API_KEY" | gcloud secrets versions add google-api-key --data-file=-

# Create LangSmith API key secret
gcloud secrets create langsmith-api-key --replication-policy="automatic"
echo -n "YOUR_LANGSMITH_API_KEY" | gcloud secrets versions add langsmith-api-key --data-file=-
```

### Verify Secrets

```bash
# List all secrets
gcloud secrets list

# Verify a secret exists
gcloud secrets versions access latest --secret="elevenlabs-api-key"
```

## Service Account Setup

Create and configure the service account with required permissions:

```bash
# Create service account
gcloud iam service-accounts create elevendops-sa \
    --display-name="ElevenDops Service Account" \
    --description="Service account for ElevenDops Cloud Run deployment"

# Grant Firestore access (Requirement 8.3)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/datastore.user"

# Grant Cloud Storage access (Requirement 8.4)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Grant Secret Manager access (Requirement 3.3)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Grant Cloud Logging access
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/logging.logWriter"
```

### Verify Service Account

```bash
# List service account roles
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --format="table(bindings.role)"
```

## Artifact Registry Setup

Create a Docker repository for container images:

```bash
# Set region
export REGION="asia-east1"

# Create Artifact Registry repository
gcloud artifacts repositories create elevendops \
    --repository-format=docker \
    --location=$REGION \
    --description="ElevenDops container images"

# Configure Docker authentication
gcloud auth configure-docker ${REGION}-docker.pkg.dev
```

## Cloud Storage Bucket Setup

Create the audio storage bucket:

```bash
# Create bucket for audio files
gsutil mb -l $REGION gs://elevendops-audio

# Set bucket permissions for service account
gsutil iam ch \
    serviceAccount:elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com:objectAdmin \
    gs://elevendops-audio
```

## Manual Deployment

### Build and Push Image

```bash
# Build the production Docker image
docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/elevendops/app:latest \
    -f Dockerfile.cloudrun .

# Push to Artifact Registry
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/elevendops/app:latest
```

### Deploy to Cloud Run

```bash
# Deploy the service
gcloud run deploy elevendops \
    --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/elevendops/app:latest \
    --region=$REGION \
    --platform=managed \
    --allow-unauthenticated \
    --service-account=elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com \
    --set-secrets=ELEVENLABS_API_KEY=elevenlabs-api-key:latest,GOOGLE_API_KEY=google-api-key:latest,LANGSMITH_API_KEY=langsmith-api-key:latest \
    --set-env-vars=APP_ENV=production,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GCS_BUCKET_NAME=elevendops-audio,LANGSMITH_PROJECT=elevendops-production,LANGSMITH_TRACING_ENABLED=true,USE_FIRESTORE_EMULATOR=false,USE_GCS_EMULATOR=false,BACKEND_API_URL=http://localhost:8000 \
    --cpu=2 \
    --memory=1Gi \
    --min-instances=0 \
    --max-instances=10 \
    --concurrency=80 \
    --timeout=300
```

### Verify Deployment

```bash
# Get service URL
gcloud run services describe elevendops --region=$REGION --format="value(status.url)"

# Check service health
SERVICE_URL=$(gcloud run services describe elevendops --region=$REGION --format="value(status.url)")
curl -s "${SERVICE_URL}/api/health" | jq .
```

## Cloud Build Trigger Setup

Set up automated CI/CD with Cloud Build triggers:

### Create Build Trigger

```bash
# Create trigger for main branch
gcloud builds triggers create github \
    --name="elevendops-deploy" \
    --repo-name="elevendops" \
    --repo-owner="YOUR_GITHUB_USERNAME" \
    --branch-pattern="^main$" \
    --build-config="cloudbuild.yaml" \
    --substitutions="_REGION=asia-east1"
```

### Alternative: Cloud Source Repositories

```bash
# If using Cloud Source Repositories
gcloud builds triggers create cloud-source-repositories \
    --name="elevendops-deploy" \
    --repo="elevendops" \
    --branch-pattern="^main$" \
    --build-config="cloudbuild.yaml" \
    --substitutions="_REGION=asia-east1"
```

### Grant Cloud Build Permissions

```bash
# Get Cloud Build service account
CLOUDBUILD_SA=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")@cloudbuild.gserviceaccount.com

# Grant Cloud Run Admin role
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${CLOUDBUILD_SA}" \
    --role="roles/run.admin"

# Grant Service Account User role (to deploy as elevendops-sa)
gcloud iam service-accounts add-iam-policy-binding \
    elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com \
    --member="serviceAccount:${CLOUDBUILD_SA}" \
    --role="roles/iam.serviceAccountUser"
```

### Manual Build Trigger

```bash
# Trigger a build manually
gcloud builds submit --config=cloudbuild.yaml \
    --substitutions=_REGION=asia-east1
```

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_ENV` | Application environment | `production` |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | Required |
| `GCS_BUCKET_NAME` | Cloud Storage bucket | `elevendops-audio` |
| `CORS_ORIGINS` | Allowed CORS origins | Service URL |
| `LANGSMITH_PROJECT` | LangSmith project name | `elevendops-production` |
| `LANGSMITH_TRACING_ENABLED` | Enable LangSmith tracing | `true` |
| `USE_FIRESTORE_EMULATOR` | Use Firestore emulator | `false` |
| `USE_GCS_EMULATOR` | Use GCS emulator | `false` |
| `BACKEND_API_URL` | Internal backend URL | `http://localhost:8000` |

## Troubleshooting

### View Logs

```bash
# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=elevendops" \
    --limit=50 \
    --format="table(timestamp,severity,textPayload)"

# Stream logs in real-time
gcloud beta run services logs tail elevendops --region=$REGION
```

### Check Container Status

```bash
# Describe service
gcloud run services describe elevendops --region=$REGION

# List revisions
gcloud run revisions list --service=elevendops --region=$REGION
```

### Common Issues

1. **Secret access denied**: Verify service account has `secretmanager.secretAccessor` role
2. **Firestore connection failed**: Verify service account has `datastore.user` role
3. **Health check failing**: Check backend logs for startup errors
4. **Image pull failed**: Verify Artifact Registry repository exists and image is pushed

### Rollback

```bash
# List revisions
gcloud run revisions list --service=elevendops --region=$REGION

# Rollback to previous revision
gcloud run services update-traffic elevendops \
    --region=$REGION \
    --to-revisions=REVISION_NAME=100
```

## Security Considerations

- All API keys are stored in Secret Manager (Requirement 3.1, 3.2)
- Service account follows least-privilege principle (Requirement 6.4)
- Container runs as non-root user
- HTTPS enforced for all external traffic (Requirement 6.3)
- Backend only accepts requests from localhost (internal) and Streamlit frontend

## Cost Optimization

- Auto-scaling configured with min 0 instances (scale to zero when idle)
- Max 10 instances to control costs
- CPU throttling disabled for better performance during requests
- Startup CPU boost enabled for faster cold starts
