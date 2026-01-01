# Secret Management Guide

This guide covers how to securely manage API keys and sensitive credentials for ElevenDops using Google Cloud Secret Manager.

## Overview

ElevenDops requires the following secrets for production deployment:

| Secret Name          | Description                              | Required    |
| -------------------- | ---------------------------------------- | ----------- |
| `elevenlabs-api-key` | ElevenLabs API key for voice AI services | ✅          |
| `google-api-key`     | Google Gemini API key for LLM            | ✅          |
| `langsmith-api-key`  | LangSmith API key for tracing            | ⚠️ Optional |

---

## Creating Secrets

### 1. ElevenLabs API Key

```bash
# Create the secret
gcloud secrets create elevenlabs-api-key \
    --replication-policy="automatic" \
    --labels="app=elevendops,env=production"

# Add the secret value
echo -n "sk-your-elevenlabs-api-key" | \
    gcloud secrets versions add elevenlabs-api-key --data-file=-
```

### 2. Google API Key

```bash
# Create the secret
gcloud secrets create google-api-key \
    --replication-policy="automatic" \
    --labels="app=elevendops,env=production"

# Add the secret value
echo -n "your-google-api-key" | \
    gcloud secrets versions add google-api-key --data-file=-
```

### 3. LangSmith API Key

```bash
# Create the secret
gcloud secrets create langsmith-api-key \
    --replication-policy="automatic" \
    --labels="app=elevendops,env=production"

# Add the secret value
echo -n "ls-your-langsmith-api-key" | \
    gcloud secrets versions add langsmith-api-key --data-file=-
```

---

## Verifying Secrets

### List All Secrets

```bash
gcloud secrets list --filter="labels.app=elevendops"
```

### View Secret Versions

```bash
# List versions for a secret
gcloud secrets versions list elevenlabs-api-key

# Access the latest version (for verification only - be careful with output!)
gcloud secrets versions access latest --secret="elevenlabs-api-key"
```

> [!CAUTION]
> Be careful when accessing secret values. Never log or expose them in shared terminals or CI/CD logs.

---

## Updating Secrets

### Add a New Version

When you need to rotate or update an API key:

```bash
# Add a new version
echo -n "new-api-key-value" | \
    gcloud secrets versions add elevenlabs-api-key --data-file=-
```

### Redeploy to Use New Secret

After updating a secret, redeploy the Cloud Run service to use the new version:

```bash
gcloud run services update elevendops \
    --region=asia-east1 \
    --set-secrets=ELEVENLABS_API_KEY=elevenlabs-api-key:latest
```

### Disable Old Versions

After verifying the new version works:

```bash
# Disable an old version
gcloud secrets versions disable 1 --secret="elevenlabs-api-key"
```

---

## Secret Rotation Best Practices

### 1. Regular Rotation Schedule

- Rotate API keys every 90 days
- Keep at least 2 versions enabled during rotation
- Disable old versions only after confirming new version works

### 2. Rotation Process

```bash
# Step 1: Generate new API key from the provider (ElevenLabs, Google, LangSmith)

# Step 2: Add new version
echo -n "new-api-key" | gcloud secrets versions add elevenlabs-api-key --data-file=-

# Step 3: Redeploy application
gcloud run services update elevendops --region=asia-east1

# Step 4: Verify application works with new key

# Step 5: Disable old version
gcloud secrets versions disable OLD_VERSION_NUMBER --secret="elevenlabs-api-key"
```

---

## Granting Access

### Service Account Access

The `elevendops-sa` service account needs access to read secrets:

```bash
# Already done in prerequisites, but verify with:
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com AND bindings.role:roles/secretmanager.secretAccessor"
```

### Individual Secret Access

For more granular control, grant access per secret:

```bash
gcloud secrets add-iam-policy-binding elevenlabs-api-key \
    --member="serviceAccount:elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

---

## Using Secrets in Cloud Run

### Declarative Configuration (service.yaml)

```yaml
env:
  - name: ELEVENLABS_API_KEY
    valueFrom:
      secretKeyRef:
        name: elevenlabs-api-key
        key: latest
  - name: GOOGLE_API_KEY
    valueFrom:
      secretKeyRef:
        name: google-api-key
        key: latest
  - name: LANGSMITH_API_KEY
    valueFrom:
      secretKeyRef:
        name: langsmith-api-key
        key: latest
```

### Command Line Configuration

```bash
gcloud run deploy elevendops \
    --set-secrets=ELEVENLABS_API_KEY=elevenlabs-api-key:latest,GOOGLE_API_KEY=google-api-key:latest,LANGSMITH_API_KEY=langsmith-api-key:latest
```

---

## Troubleshooting

### Secret Access Denied

If you see "Permission denied accessing secret":

```bash
# Verify service account has access
gcloud secrets get-iam-policy elevenlabs-api-key

# Grant access if missing
gcloud secrets add-iam-policy-binding elevenlabs-api-key \
    --member="serviceAccount:elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### Secret Not Found

```bash
# List all secrets to verify name
gcloud secrets list

# Check if secret has versions
gcloud secrets versions list elevenlabs-api-key
```

### Application Fails to Start

If the application fails due to missing required secrets:

1. Check Cloud Run logs for specific error messages
2. Verify all required secrets exist and have at least one enabled version
3. Verify the secret names match exactly (case-sensitive)

```bash
# View Cloud Run logs for secret-related errors
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=elevendops AND textPayload:secret" \
    --limit=20
```

---

## Security Best Practices

1. **Never commit secrets to version control**
2. **Use Secret Manager for all production credentials**
3. **Rotate keys regularly (every 90 days recommended)**
4. **Use least-privilege access** - grant secret access only to required service accounts
5. **Enable audit logging** to track secret access
6. **Disable unused versions** to reduce attack surface

---

## Related Documentation

- [Google Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Cloud Run Secrets Integration](https://cloud.google.com/run/docs/configuring/secrets)
- [Upload to Cloud Run Guide](./guide--upload-to-cloud-run.md)
