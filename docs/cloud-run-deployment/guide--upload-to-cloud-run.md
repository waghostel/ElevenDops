# Upload to Cloud Run - Complete Guide

This guide provides step-by-step instructions for uploading and deploying ElevenDops to Google Cloud Run.

## Overview

There are two methods to upload to Cloud Run:

1. **Manual Deployment** - Build and deploy from your local machine
2. **Automated CI/CD** - Trigger deployment via Git push to main branch

## Prerequisites Checklist

Before proceeding, ensure you have completed all items in the [Prerequisites Guide](./guide--prerequisites.md):

- [ ] GCP project created with billing enabled
- [ ] Required APIs enabled (Cloud Run, Cloud Build, Artifact Registry, Secret Manager)
- [ ] Firestore database created
- [ ] Cloud Storage bucket created
- [ ] Secrets configured in Secret Manager
- [ ] Service account created with required permissions
- [ ] Artifact Registry repository created
- [ ] Docker configured to authenticate with Artifact Registry

---

## Method 1: Manual Deployment

Use this method for first-time deployments or when you need direct control.

### Step 1: Set Environment Variables

```bash
# Set your project configuration
export PROJECT_ID="your-project-id"
export REGION="us-central1"

# Verify configuration
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
```

### Step 2: Authenticate with GCP

```bash
# Login to Google Cloud
gcloud auth login

# Set the active project
gcloud config set project $PROJECT_ID

# Configure Docker for Artifact Registry
gcloud auth configure-docker ${REGION}-docker.pkg.dev
```

### Step 3: Build the Docker Image

```bash
# Navigate to project root
cd /path/to/ElevenDops

# Build the production image using Dockerfile.cloudrun
docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/elevendops/app:latest \
    -f Dockerfile.cloudrun .
```

> [!TIP]
> The build uses multi-stage builds to minimize image size. The first build may take several minutes.

### Step 4: Push Image to Artifact Registry

```bash
# Push the image to Google Cloud Artifact Registry
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/elevendops/app:latest
```

> [!NOTE]
> Ensure your Artifact Registry repository `elevendops` exists. See the [Prerequisites Guide](./guide--prerequisites.md) for setup.

### Step 5: Deploy to Cloud Run

```bash
# Deploy the service with all configurations
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

### Step 6: Verify Deployment

```bash
# Get the service URL
SERVICE_URL=$(gcloud run services describe elevendops \
    --region=$REGION \
    --format="value(status.url)")

echo "Service URL: $SERVICE_URL"

# Test the health endpoint
curl -s "${SERVICE_URL}/api/health" | jq .
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### Step 7: Access the Application

Open your browser and navigate to the service URL. The Streamlit frontend should load and be fully functional.

---

## Method 2: Automated CI/CD Deployment

Use this method for ongoing development and team collaboration.

### Initial Setup (One-Time)

#### 1. Grant Cloud Build Permissions

```bash
# Get Cloud Build service account
CLOUDBUILD_SA=$(gcloud projects describe $PROJECT_ID \
    --format="value(projectNumber)")@cloudbuild.gserviceaccount.com

# Grant Cloud Run Admin role
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${CLOUDBUILD_SA}" \
    --role="roles/run.admin"

# Grant Service Account User role
gcloud iam service-accounts add-iam-policy-binding \
    elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com \
    --member="serviceAccount:${CLOUDBUILD_SA}" \
    --role="roles/iam.serviceAccountUser"
```

#### 2. Create Cloud Build Trigger

**Option A: GitHub Repository**

```bash
gcloud builds triggers create github \
    --name="elevendops-deploy" \
    --repo-name="ElevenDops" \
    --repo-owner="YOUR_GITHUB_USERNAME" \
    --branch-pattern="^main$" \
    --build-config="cloudbuild.yaml" \
    --substitutions="_REGION=us-central1"
```

**Option B: Cloud Source Repositories**

```bash
gcloud builds triggers create cloud-source-repositories \
    --name="elevendops-deploy" \
    --repo="elevendops" \
    --branch-pattern="^main$" \
    --build-config="cloudbuild.yaml" \
    --substitutions="_REGION=us-central1"
```

### Deploying with CI/CD

Once the trigger is set up, simply push to the main branch:

```bash
# Commit your changes
git add .
git commit -m "Deploy: your deployment message"

# Push to main branch - this triggers automatic deployment
git push origin main
```

### Monitor Build Progress

```bash
# List recent builds
gcloud builds list --limit=5

# View build logs for a specific build
gcloud builds log BUILD_ID
```

### Manual Trigger

You can also manually trigger a build:

```bash
gcloud builds submit --config=cloudbuild.yaml \
    --substitutions=_REGION=us-central1
```

---

## Deployment Verification

### Check Service Status

```bash
# Describe the deployed service
gcloud run services describe elevendops --region=$REGION

# List all revisions
gcloud run revisions list --service=elevendops --region=$REGION
```

### View Real-Time Logs

```bash
# Stream logs in real-time
gcloud beta run services logs tail elevendops --region=$REGION
```

### Test All Endpoints

```bash
SERVICE_URL=$(gcloud run services describe elevendops \
    --region=$REGION --format="value(status.url)")

# Test health endpoint
curl -s "${SERVICE_URL}/api/health"

# Test if Streamlit is serving
curl -s -I "${SERVICE_URL}/" | head -n 5
```

---

## Updating the Deployment

### Update with New Image

```bash
# Build new image with version tag
docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/elevendops/app:v1.2.0 \
    -f Dockerfile.cloudrun .

# Push new image
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/elevendops/app:v1.2.0

# Update Cloud Run service
gcloud run deploy elevendops \
    --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/elevendops/app:v1.2.0 \
    --region=$REGION
```

### Update Environment Variables Only

```bash
gcloud run services update elevendops \
    --region=$REGION \
    --set-env-vars=NEW_VAR=value
```

### Update Secrets

```bash
# Update secret value
echo -n "NEW_API_KEY" | gcloud secrets versions add elevenlabs-api-key --data-file=-

# Redeploy to pick up new secret version
gcloud run services update elevendops \
    --region=$REGION \
    --set-secrets=ELEVENLABS_API_KEY=elevenlabs-api-key:latest
```

---

## Rollback

If a deployment has issues, rollback to a previous revision:

```bash
# List available revisions
gcloud run revisions list --service=elevendops --region=$REGION

# Rollback to a specific revision
gcloud run services update-traffic elevendops \
    --region=$REGION \
    --to-revisions=elevendops-00003-xyz=100
```

---

## Troubleshooting

If you encounter issues during deployment, refer to the [Troubleshooting Guide](./guide--troubleshooting.md).

### Quick Checks

1. **Build failed**: Check Docker build logs
2. **Push failed**: Verify Artifact Registry authentication
3. **Deploy failed**: Check service account permissions
4. **Container unhealthy**: View container logs
5. **Secrets unavailable**: Verify Secret Manager access

```bash
# Check container logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=elevendops" \
    --limit=50 --format="table(timestamp,severity,textPayload)"
```

---

## Next Steps

- [Configure CI/CD Pipeline](./guide--cicd-pipeline.md) for automated deployments
- [Set up monitoring](./guide--troubleshooting.md#monitoring) for production alerts
- [Review architecture](./reference--architecture.md) for scaling considerations
