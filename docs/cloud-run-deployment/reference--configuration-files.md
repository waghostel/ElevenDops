# Configuration Files Reference

This document provides detailed reference for all configuration files used in ElevenDops Cloud Run deployment.

---

## File Overview

| File                  | Location        | Purpose                         |
| --------------------- | --------------- | ------------------------------- |
| `Dockerfile.cloudrun` | Repository root | Production Docker image build   |
| `cloudbuild.yaml`     | Repository root | CI/CD pipeline configuration    |
| `service.yaml`        | `deploy/`       | Cloud Run service configuration |
| `start.sh`            | `scripts/`      | Process manager script          |

---

## Dockerfile.cloudrun

**Location:** `Dockerfile.cloudrun`

### Overview

Multi-stage Dockerfile for building the production container image.

### Structure

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder
# Install Poetry and dependencies

# Stage 2: Production
FROM python:3.11-slim AS production
# Copy dependencies and application code
# Run as non-root user
```

### Key Sections

#### Builder Stage

```dockerfile
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install poetry==1.7.1

WORKDIR /app
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-interaction --no-ansi
```

**Purpose:** Install all dependencies using Poetry, excluding dev dependencies.

#### Production Stage

```dockerfile
FROM python:3.11-slim AS production

# Production environment variables
ENV APP_ENV=production \
    USE_FIRESTORE_EMULATOR=false \
    USE_GCS_EMULATOR=false \
    BACKEND_API_URL=http://localhost:8000

# Install curl for health checks
RUN apt-get update && apt-get install -y curl

# Create non-root user
RUN useradd --create-home appuser

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application code
COPY --chown=appuser:appuser backend/ ./backend/
COPY --chown=appuser:appuser streamlit_app/ ./streamlit_app/
COPY --chown=appuser:appuser scripts/start.sh ./start.sh

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["./start.sh"]
```

**Key Features:**

- Non-root user for security
- Minimal runtime dependencies
- Health check configured
- Process manager as entrypoint

---

## cloudbuild.yaml

**Location:** `cloudbuild.yaml`

### Overview

Cloud Build CI/CD pipeline configuration for automated builds and deployments.

### Complete Configuration

```yaml
steps:
  # Step 1: Build Docker image
  - name: "gcr.io/cloud-builders/docker"
    id: "build"
    args:
      - "build"
      - "-t"
      - "${_REGION}-docker.pkg.dev/${PROJECT_ID}/elevendops/app:${SHORT_SHA}"
      - "-t"
      - "${_REGION}-docker.pkg.dev/${PROJECT_ID}/elevendops/app:latest"
      - "-f"
      - "Dockerfile.cloudrun"
      - "."

  # Step 2: Push to Artifact Registry
  - name: "gcr.io/cloud-builders/docker"
    id: "push"
    args:
      - "push"
      - "--all-tags"
      - "${_REGION}-docker.pkg.dev/${PROJECT_ID}/elevendops/app"
    waitFor: ["build"]

  # Step 3: Deploy to Cloud Run
  - name: "gcr.io/google.com/cloudsdktool/cloud-sdk"
    id: "deploy"
    entrypoint: "gcloud"
    args:
      - "run"
      - "deploy"
      - "elevendops"
      - "--image"
      - "${_REGION}-docker.pkg.dev/${PROJECT_ID}/elevendops/app:${SHORT_SHA}"
      - "--region"
      - "${_REGION}"
      - "--platform"
      - "managed"
      - "--allow-unauthenticated"
      - "--service-account"
      - "elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com"
      - "--set-secrets"
      - "ELEVENLABS_API_KEY=elevenlabs-api-key:latest,..."
      - "--set-env-vars"
      - "APP_ENV=production,..."
      - "--cpu"
      - "2"
      - "--memory"
      - "1Gi"
      - "--min-instances"
      - "0"
      - "--max-instances"
      - "10"
    waitFor: ["push"]

substitutions:
  _REGION: "us-central1"

options:
  logging: CLOUD_LOGGING_ONLY
  machineType: "E2_HIGHCPU_8"

images:
  - "${_REGION}-docker.pkg.dev/${PROJECT_ID}/elevendops/app:${SHORT_SHA}"
  - "${_REGION}-docker.pkg.dev/${PROJECT_ID}/elevendops/app:latest"

timeout: "900s"
```

### Substitution Variables

| Variable     | Description          | Default        |
| ------------ | -------------------- | -------------- |
| `_REGION`    | Deployment region    | `us-central1`  |
| `PROJECT_ID` | GCP project ID       | Auto-detected  |
| `SHORT_SHA`  | Git commit short SHA | Auto-generated |

### Customizing

Override variables at build time:

```bash
gcloud builds submit --substitutions=_REGION=us-central1
```

---

## service.yaml

**Location:** `deploy/service.yaml`

### Overview

Declarative Cloud Run service configuration using Knative serving API.

### Complete Configuration

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: elevendops
  labels:
    cloud.googleapis.com/location: us-central1
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
        run.googleapis.com/startup-cpu-boost: "true"
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      serviceAccountName: elevendops-sa@PROJECT_ID.iam.gserviceaccount.com
      containers:
        - image: REGION-docker.pkg.dev/PROJECT_ID/elevendops/app:latest
          ports:
            - containerPort: 8080
          resources:
            limits:
              cpu: "2"
              memory: "1Gi"
          env:
            - name: APP_ENV
              value: "production"
            # ... other env vars
            - name: ELEVENLABS_API_KEY
              valueFrom:
                secretKeyRef:
                  name: elevenlabs-api-key
                  key: latest
          startupProbe:
            httpGet:
              path: /api/health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
            failureThreshold: 12
          livenessProbe:
            httpGet:
              path: /api/health
              port: 8000
            periodSeconds: 30
            failureThreshold: 3
```

### Key Annotations

| Annotation                             | Value   | Purpose                  |
| -------------------------------------- | ------- | ------------------------ |
| `autoscaling.knative.dev/minScale`     | `0`     | Scale to zero when idle  |
| `autoscaling.knative.dev/maxScale`     | `10`    | Maximum instances        |
| `run.googleapis.com/cpu-throttling`    | `false` | Full CPU during requests |
| `run.googleapis.com/startup-cpu-boost` | `true`  | Faster cold starts       |

### Deploying with service.yaml

```bash
# Replace placeholders
sed -e "s/PROJECT_ID/$PROJECT_ID/g" \
    -e "s/REGION/$REGION/g" \
    deploy/service.yaml > /tmp/service-deploy.yaml

# Deploy
gcloud run services replace /tmp/service-deploy.yaml --region=$REGION
```

---

## start.sh

**Location:** `scripts/start.sh`

### Overview

Process manager script that runs both FastAPI and Streamlit within the container.

### Key Functions

#### Process Startup

```bash
# Start backend
start_backend() {
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
}

# Wait for health check
wait_for_backend() {
    for i in {1..30}; do
        if curl -s http://localhost:8000/api/health > /dev/null; then
            return 0
        fi
        sleep 1
    done
    return 1
}

# Start frontend
start_frontend() {
    streamlit run streamlit_app/app.py \
        --server.port=${PORT:-8501} \
        --server.address=0.0.0.0 \
        --server.headless=true &
    FRONTEND_PID=$!
}
```

#### Graceful Shutdown

```bash
graceful_shutdown() {
    kill -TERM $FRONTEND_PID $BACKEND_PID 2>/dev/null

    # Wait up to 10 seconds
    for i in {1..10}; do
        if ! kill -0 $BACKEND_PID $FRONTEND_PID 2>/dev/null; then
            break
        fi
        sleep 1
    done

    # Force kill if needed
    kill -9 $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap graceful_shutdown SIGTERM SIGINT
```

#### Process Monitoring

```bash
monitor_processes() {
    while true; do
        # Check and restart backend if crashed
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            start_backend
            wait_for_backend
        fi

        # Check and restart frontend if crashed
        if ! kill -0 $FRONTEND_PID 2>/dev/null; then
            start_frontend
        fi

        sleep 5
    done
}
```

### Configuration Variables

| Variable               | Default | Purpose                        |
| ---------------------- | ------- | ------------------------------ |
| `BACKEND_PORT`         | `8000`  | Backend listening port         |
| `PORT`                 | `8501`  | Frontend port (from Cloud Run) |
| `HEALTH_CHECK_TIMEOUT` | `30`    | Seconds to wait for health     |
| `MONITOR_INTERVAL`     | `5`     | Seconds between health checks  |
| `MAX_RESTART_ATTEMPTS` | `3`     | Max restarts before exit       |

---

## .streamlit/config.toml

**Location:** `.streamlit/config.toml`

### Production Configuration

```toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
serverAddress = "0.0.0.0"

[theme]
# Custom theme configuration
```

---

## Validation

### Validate YAML Files

```bash
# Validate service.yaml
yamllint deploy/service.yaml

# Validate cloudbuild.yaml
gcloud builds submit --config=cloudbuild.yaml --dry-run
```

### Test Dockerfile Locally

```bash
# Build locally
docker build -t elevendops-test -f Dockerfile.cloudrun .

# Run locally
docker run -p 8080:8080 -e PORT=8080 elevendops-test
```

---

## Related Documentation

- [Architecture Reference](./reference--architecture.md)
- [Environment Variables Reference](./reference--environment-variables.md)
- [Upload to Cloud Run Guide](./guide--upload-to-cloud-run.md)
