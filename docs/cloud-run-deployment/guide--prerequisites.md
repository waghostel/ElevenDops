# Prerequisites Guide

This guide covers all the prerequisites needed before deploying ElevenDops to Google Cloud Run.

## GCP Project Setup

### 1. Create or Select a GCP Project

```bash
# Set your project ID
export PROJECT_ID="your-project-id"

# Create a new project (optional)
gcloud projects create $PROJECT_ID --name="ElevenDops"

# Set as active project
gcloud config set project $PROJECT_ID
```

### 2. Enable Billing

Ensure billing is enabled for your project. Visit the [Google Cloud Console](https://console.cloud.google.com/billing) to enable billing.

### 3. Enable Required APIs

```bash
# Enable all required APIs
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    firestore.googleapis.com \
    storage.googleapis.com
```

> [!IMPORTANT]
> All these APIs must be enabled before proceeding with deployment.

---

## Service Account Setup

Create a dedicated service account with minimal required permissions.

### 1. Create Service Account

```bash
gcloud iam service-accounts create elevendops-sa \
    --display-name="ElevenDops Service Account" \
    --description="Service account for ElevenDops Cloud Run deployment"
```

### 2. Grant Required Roles

```bash
# Grant Firestore access
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/datastore.user"

# Grant Cloud Storage access
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Grant Secret Manager access
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Grant Cloud Logging access
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/logging.logWriter"
```

### 3. Verify Service Account Roles

```bash
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --format="table(bindings.role)"
```

Expected output:

```
ROLE
roles/datastore.user
roles/logging.logWriter
roles/secretmanager.secretAccessor
roles/storage.objectAdmin
```

---

## Artifact Registry Setup

Create a Docker repository to store container images.

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

### Verify Repository

```bash
gcloud artifacts repositories list --location=$REGION
```

---

## Secret Manager Setup

Store sensitive API keys securely in Secret Manager.

### 1. Create Secrets

```bash
# Create ElevenLabs API key secret
gcloud secrets create elevenlabs-api-key \
    --replication-policy="automatic"
echo -n "YOUR_ELEVENLABS_API_KEY" | \
    gcloud secrets versions add elevenlabs-api-key --data-file=-

# Create Google API key secret
gcloud secrets create google-api-key \
    --replication-policy="automatic"
echo -n "YOUR_GOOGLE_API_KEY" | \
    gcloud secrets versions add google-api-key --data-file=-

# Create LangSmith API key secret
gcloud secrets create langsmith-api-key \
    --replication-policy="automatic"
echo -n "YOUR_LANGSMITH_API_KEY" | \
    gcloud secrets versions add langsmith-api-key --data-file=-
```

> [!CAUTION]
> Never commit API keys to version control. Always use Secret Manager for production deployments.

### 2. Verify Secrets

```bash
# List all secrets
gcloud secrets list

# Verify a secret has versions
gcloud secrets versions list elevenlabs-api-key
```

For more details, see the [Secret Management Guide](./guide--secret-management.md).

---

## Firestore Setup

### 1. Create Firestore Database

```bash
# Create Firestore in Native mode
gcloud firestore databases create \
    --location=$REGION \
    --type=firestore-native
```

> [!NOTE]
> If you already have a Firestore database, you can skip this step. Firestore cannot be deleted once created in a project.

### 2. Verify Firestore

Visit the [Firestore Console](https://console.cloud.google.com/firestore) to verify the database is created.

---

## Cloud Storage Setup

### 1. Create Storage Bucket

```bash
# Create bucket for audio files
gsutil mb -l $REGION gs://elevendops-audio

# Set bucket permissions for service account
gsutil iam ch \
    serviceAccount:elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com:objectAdmin \
    gs://elevendops-audio
```

### 2. Verify Bucket

```bash
gsutil ls
```

---

## Local Development Tools

Ensure you have the following installed locally:

### Required Tools

| Tool     | Purpose                   | Installation                                               |
| -------- | ------------------------- | ---------------------------------------------------------- |
| `gcloud` | Google Cloud CLI          | [Install Guide](https://cloud.google.com/sdk/docs/install) |
| `docker` | Container runtime         | [Install Guide](https://docs.docker.com/get-docker/)       |
| `jq`     | JSON processor (optional) | `brew install jq` or `apt install jq`                      |

### Verify Installation

```bash
# Check gcloud
gcloud version

# Check Docker
docker --version

# Authenticate gcloud
gcloud auth login
gcloud auth configure-docker ${REGION}-docker.pkg.dev
```

---

## Prerequisites Checklist

Before proceeding to deployment, verify all items are complete:

- [ ] GCP Project created with billing enabled
- [ ] Required APIs enabled
- [ ] Service account created with roles:
  - [ ] `roles/datastore.user`
  - [ ] `roles/storage.objectAdmin`
  - [ ] `roles/secretmanager.secretAccessor`
  - [ ] `roles/logging.logWriter`
- [ ] Artifact Registry repository created
- [ ] Docker configured for Artifact Registry
- [ ] Secrets created in Secret Manager:
  - [ ] `elevenlabs-api-key`
  - [ ] `google-api-key`
  - [ ] `langsmith-api-key`
- [ ] Firestore database created (Native mode)
- [ ] Cloud Storage bucket created

---

## Next Steps

Once all prerequisites are complete, proceed to the [Upload to Cloud Run Guide](./guide--upload-to-cloud-run.md).
