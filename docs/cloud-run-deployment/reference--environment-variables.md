# Environment Variables Reference

Complete reference for all environment variables used in ElevenDops Cloud Run deployment.

---

## Production Environment Variables

### Application Configuration

| Variable               | Description             | Default      | Required |
| ---------------------- | ----------------------- | ------------ | -------- |
| `APP_ENV`              | Application environment | `production` | ✅       |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID          | -            | ✅       |
| `DEBUG`                | Enable debug mode       | `false`      | ⚠️       |
| `PORT`                 | Cloud Run assigned port | `8080`       | Auto     |

### Backend Configuration

| Variable          | Description          | Default                 | Required |
| ----------------- | -------------------- | ----------------------- | -------- |
| `BACKEND_API_URL` | Internal backend URL | `http://localhost:8000` | ✅       |
| `CORS_ORIGINS`    | Allowed CORS origins | Service URL             | ⚠️       |

### Emulator Settings (Production)

| Variable                 | Description            | Default              | Required |
| ------------------------ | ---------------------- | -------------------- | -------- |
| `USE_FIRESTORE_EMULATOR` | Use Firestore emulator | `false`              | ✅       |
| `FIRESTORE_DATABASE_ID`  | Named Firestore DB ID  | `elevendops-db-test` | ⚠️       |
| `USE_GCS_EMULATOR`       | Use GCS emulator       | `false`              | ✅       |
| `USE_MOCK_DATA`          | Use mock data          | `false`              | ✅       |
| `USE_MOCK_STORAGE`       | Use mock storage       | `false`              | ✅       |

### Cloud Storage

| Variable          | Description               | Default                  | Required |
| ----------------- | ------------------------- | ------------------------ | -------- |
| `GCS_BUCKET_NAME` | Cloud Storage bucket name | `elevendops-bucket-test` | ✅       |

### LangSmith Tracing

| Variable                    | Description              | Default                 | Required |
| --------------------------- | ------------------------ | ----------------------- | -------- |
| `LANGSMITH_PROJECT`         | LangSmith project name   | `elevendops-production` | ⚠️       |
| `LANGSMITH_TRACING_ENABLED` | Enable LangSmith tracing | `true`                  | ⚠️       |

---

## Secret-Based Variables

These are stored in Secret Manager and mounted at runtime:

| Variable             | Secret Name          | Description           | Required |
| -------------------- | -------------------- | --------------------- | -------- |
| `ELEVENLABS_API_KEY` | `elevenlabs-api-key` | ElevenLabs API key    | ✅       |
| `GOOGLE_API_KEY`     | `google-api-key`     | Google Gemini API key | ✅       |
| `LANGSMITH_API_KEY`  | `langsmith-api-key`  | LangSmith API key     | ⚠️       |

---

## Setting Environment Variables

### During Deployment

```bash
gcloud run deploy elevendops \
    --set-env-vars=APP_ENV=production,GOOGLE_CLOUD_PROJECT=your-project,GCS_BUCKET_NAME=elevendops-audio
```

### Update Existing Service

```bash
gcloud run services update elevendops \
    --region=us-central1 \
    --set-env-vars=NEW_VAR=value
```

### Update Single Variable

```bash
gcloud run services update elevendops \
    --region=us-central1 \
    --update-env-vars=LANGSMITH_TRACING_ENABLED=false
```

### Remove Variable

```bash
gcloud run services update elevendops \
    --region=us-central1 \
    --remove-env-vars=UNUSED_VAR
```

---

## Configuration in service.yaml

```yaml
env:
  - name: APP_ENV
    value: "production"
  - name: GOOGLE_CLOUD_PROJECT
    value: "PROJECT_ID"
  - name: GCS_BUCKET_NAME
    value: "elevendops-bucket"
  - name: FIRESTORE_DATABASE_ID
    value: "elevendops-db"
  - name: CORS_ORIGINS
    value: "https://elevendops-HASH-REGION.a.run.app,http://localhost:8000"
  - name: LANGSMITH_PROJECT
    value: "elevendops-production"
  - name: LANGSMITH_TRACING_ENABLED
    value: "true"
  - name: USE_FIRESTORE_EMULATOR
    value: "false"
  - name: USE_GCS_EMULATOR
    value: "false"
  - name: BACKEND_API_URL
    value: "http://localhost:8000"
  - name: DEBUG
    value: "false"
```

---

### Substitution Variables

Used for centralizing configuration values:

```yaml
substitutions:
  _REGION: "us-central1"
  _GCS_BUCKET_NAME: "elevendops-bucket"
  _FIRESTORE_DATABASE_ID: "elevendops-db"
```

### Deploy Step

```yaml
--set-env-vars=APP_ENV=production,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GCS_BUCKET_NAME=${_GCS_BUCKET_NAME},FIRESTORE_DATABASE_ID=${_FIRESTORE_DATABASE_ID},LANGSMITH_PROJECT=elevendops-production,LANGSMITH_TRACING_ENABLED=true,USE_FIRESTORE_EMULATOR=false,USE_GCS_EMULATOR=false,BACKEND_API_URL=http://localhost:8000,DEBUG=false
```

---

## Environment-Specific Configurations

### Production

```bash
APP_ENV=production
USE_FIRESTORE_EMULATOR=false
USE_GCS_EMULATOR=false
USE_MOCK_DATA=false
LANGSMITH_TRACING_ENABLED=true
```

### Staging

```bash
APP_ENV=staging
USE_FIRESTORE_EMULATOR=false
USE_GCS_EMULATOR=false
USE_MOCK_DATA=false
LANGSMITH_TRACING_ENABLED=true
LANGSMITH_PROJECT=elevendops-staging
```

### Development (Local)

```bash
APP_ENV=development
USE_FIRESTORE_EMULATOR=true
USE_GCS_EMULATOR=true
USE_MOCK_DATA=false
LANGSMITH_TRACING_ENABLED=false
```

---

## Dockerfile Defaults

These defaults are set in `Dockerfile.cloudrun`:

```dockerfile
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    USE_FIRESTORE_EMULATOR=false \
    USE_GCS_EMULATOR=false \
    USE_MOCK_DATA=false \
    USE_MOCK_STORAGE=false \
    BACKEND_API_URL=http://localhost:8000
```

These can be overridden at deployment time.

---

## Viewing Current Configuration

```bash
# View all environment variables
gcloud run services describe elevendops \
    --region=us-central1 \
    --format="yaml(spec.template.spec.containers[0].env)"

# View specific variable
gcloud run services describe elevendops \
    --region=us-central1 \
    --format="value(spec.template.spec.containers[0].env.value)" \
    --filter="spec.template.spec.containers[0].env.name=APP_ENV"
```

---

## Best Practices

1. **Never hardcode secrets** - Always use Secret Manager
2. **Use descriptive names** - Make variable purpose clear
3. **Document all variables** - Keep this reference updated
4. **Use consistent naming** - Follow `SCREAMING_SNAKE_CASE`
5. **Minimize differences** - Keep environments as similar as possible
6. **Validate at startup** - Check required variables exist

---

## Related Documentation

- [Configuration Files Reference](./reference--configuration-files.md)
- [Secret Management Guide](./guide--secret-management.md)
- [Architecture Reference](./reference--architecture.md)
