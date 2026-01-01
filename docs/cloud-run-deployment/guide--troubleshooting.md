# Troubleshooting Guide

This guide covers common issues and solutions when deploying ElevenDops to Cloud Run.

## Quick Diagnostics

### Check Service Status

```bash
export REGION="asia-east1"

# Get service status
gcloud run services describe elevendops --region=$REGION

# Check if service is serving traffic
gcloud run services describe elevendops --region=$REGION \
    --format="value(status.conditions)"
```

### View Recent Logs

```bash
# View last 50 log entries
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=elevendops" \
    --limit=50 \
    --format="table(timestamp,severity,textPayload)"

# Stream logs in real-time
gcloud beta run services logs tail elevendops --region=$REGION
```

---

## Common Issues

### Container Startup Failures

#### Issue: Container fails to start

**Symptoms:**

- Service shows "Container failed to start"
- Health checks fail continuously

**Solutions:**

1. **Check process manager logs:**

   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND textPayload:start.sh" --limit=20
   ```

2. **Verify backend starts correctly:**

   ```bash
   # Look for backend startup errors
   gcloud logging read "resource.type=cloud_run_revision AND textPayload:uvicorn" --limit=20
   ```

3. **Check for missing dependencies:**

   ```bash
   # Look for import errors
   gcloud logging read "resource.type=cloud_run_revision AND textPayload:ImportError" --limit=20
   ```

4. **Increase startup timeout if needed:**
   ```bash
   gcloud run services update elevendops \
       --region=$REGION \
       --timeout=600
   ```

---

#### Issue: Health check failures

**Symptoms:**

- Container starts but Cloud Run reports unhealthy
- Repeated restarts

**Solutions:**

1. **Test health endpoint locally:**

   ```bash
   # Build and run locally
   docker build -t elevendops-test -f Dockerfile.cloudrun .
   docker run -p 8080:8080 -p 8000:8000 elevendops-test

   # Test health endpoint
   curl http://localhost:8000/api/health
   ```

2. **Check startup probe configuration in service.yaml:**

   ```yaml
   startupProbe:
     httpGet:
       path: /api/health
       port: 8000
     initialDelaySeconds: 10
     periodSeconds: 5
     failureThreshold: 12 # Increase if startup takes longer
   ```

3. **Increase startup CPU boost:**
   ```bash
   gcloud run services update elevendops \
       --region=$REGION \
       --cpu-boost
   ```

---

### Secret and Permission Issues

#### Issue: Secret access denied

**Symptoms:**

- Error: "Permission denied accessing secret"
- Service fails to start due to missing API keys

**Solutions:**

1. **Verify service account has secret access:**

   ```bash
   gcloud secrets get-iam-policy elevenlabs-api-key
   ```

2. **Grant access if missing:**

   ```bash
   gcloud secrets add-iam-policy-binding elevenlabs-api-key \
       --member="serviceAccount:elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
       --role="roles/secretmanager.secretAccessor"
   ```

3. **Verify secret exists and has versions:**
   ```bash
   gcloud secrets versions list elevenlabs-api-key
   ```

---

#### Issue: Firestore connection failed

**Symptoms:**

- Error: "Could not connect to Firestore"
- 503 Service Unavailable errors

**Solutions:**

1. **Verify service account has Firestore access:**

   ```bash
   gcloud projects get-iam-policy $PROJECT_ID \
       --flatten="bindings[].members" \
       --filter="bindings.members:elevendops-sa AND bindings.role:roles/datastore.user"
   ```

2. **Grant access if missing:**

   ```bash
   gcloud projects add-iam-policy-binding $PROJECT_ID \
       --member="serviceAccount:elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
       --role="roles/datastore.user"
   ```

3. **Verify Firestore database exists:**
   ```bash
   gcloud firestore databases list
   ```

---

#### Issue: Cloud Storage access denied

**Symptoms:**

- Error: "Access denied to GCS bucket"
- Audio files not saving/loading

**Solutions:**

1. **Verify bucket exists:**

   ```bash
   gsutil ls gs://elevendops-audio
   ```

2. **Grant access if missing:**
   ```bash
   gsutil iam ch \
       serviceAccount:elevendops-sa@${PROJECT_ID}.iam.gserviceaccount.com:objectAdmin \
       gs://elevendops-audio
   ```

---

### Deployment Issues

#### Issue: Image push failed

**Symptoms:**

- Error: "unauthorized: permission denied" during push
- Build succeeds but push fails

**Solutions:**

1. **Reconfigure Docker authentication:**

   ```bash
   gcloud auth configure-docker ${REGION}-docker.pkg.dev
   ```

2. **Verify Artifact Registry repository exists:**

   ```bash
   gcloud artifacts repositories list --location=$REGION
   ```

3. **Create repository if missing:**
   ```bash
   gcloud artifacts repositories create elevendops \
       --repository-format=docker \
       --location=$REGION
   ```

---

#### Issue: Deployment fails with quota error

**Symptoms:**

- Error: "Resource exhausted" or "Quota exceeded"

**Solutions:**

1. **Check project quotas:**

   ```bash
   gcloud compute project-info describe --project=$PROJECT_ID
   ```

2. **Reduce resource requests:**

   ```bash
   gcloud run services update elevendops \
       --region=$REGION \
       --cpu=1 \
       --memory=512Mi \
       --max-instances=5
   ```

3. **Request quota increase in [Cloud Console](https://console.cloud.google.com/iam-admin/quotas)**

---

### Runtime Issues

#### Issue: Application timeout errors

**Symptoms:**

- 504 Gateway Timeout errors
- Requests taking too long

**Solutions:**

1. **Increase request timeout:**

   ```bash
   gcloud run services update elevendops \
       --region=$REGION \
       --timeout=300
   ```

2. **Enable CPU throttling off:**

   ```bash
   gcloud run services update elevendops \
       --region=$REGION \
       --no-cpu-throttling
   ```

3. **Increase concurrency if overloaded:**
   ```bash
   gcloud run services update elevendops \
       --region=$REGION \
       --concurrency=100
   ```

---

#### Issue: Cold start too slow

**Symptoms:**

- First request takes 10+ seconds
- Intermittent slow responses

**Solutions:**

1. **Keep minimum instances warm:**

   ```bash
   gcloud run services update elevendops \
       --region=$REGION \
       --min-instances=1
   ```

2. **Enable startup CPU boost:**

   ```bash
   gcloud run services update elevendops \
       --region=$REGION \
       --cpu-boost
   ```

3. **Optimize container image size** - Use multi-stage builds (already configured)

---

#### Issue: CORS errors in browser

**Symptoms:**

- Browser blocks requests with CORS errors
- API calls fail from frontend

**Solutions:**

1. **Update CORS origins:**

   ```bash
   SERVICE_URL=$(gcloud run services describe elevendops \
       --region=$REGION --format="value(status.url)")

   gcloud run services update elevendops \
       --region=$REGION \
       --set-env-vars="CORS_ORIGINS=${SERVICE_URL},http://localhost:8000"
   ```

---

## Monitoring

### Set Up Alerts

```bash
# Create an alert policy for error rate
gcloud alpha monitoring policies create \
    --policy-from-file=alert-policy.yaml
```

### View Metrics

Access metrics in the [Cloud Console Monitoring](https://console.cloud.google.com/monitoring):

- Request count
- Latency percentiles
- Error rate
- Instance count

### Custom Dashboards

Create dashboards for:

- Application health
- Request patterns
- Resource utilization

---

## Rollback Procedures

### List Available Revisions

```bash
gcloud run revisions list --service=elevendops --region=$REGION
```

### Rollback to Previous Revision

```bash
# Identify the revision to rollback to
gcloud run revisions list --service=elevendops --region=$REGION

# Route 100% traffic to that revision
gcloud run services update-traffic elevendops \
    --region=$REGION \
    --to-revisions=elevendops-00003-abc=100
```

### Gradual Rollback

```bash
# Route 50% to old revision, 50% to new
gcloud run services update-traffic elevendops \
    --region=$REGION \
    --to-revisions=elevendops-00003-abc=50,elevendops-00004-xyz=50
```

---

## Debug Checklist

When troubleshooting, work through this checklist:

- [ ] Check service status: `gcloud run services describe elevendops`
- [ ] View recent logs for errors
- [ ] Verify all secrets exist and have versions
- [ ] Verify service account permissions
- [ ] Test health endpoint directly
- [ ] Check resource usage (CPU, memory)
- [ ] Verify environment variables are set correctly
- [ ] Check if issue is reproducible locally

---

## Getting Help

1. **Cloud Run Documentation**: [https://cloud.google.com/run/docs](https://cloud.google.com/run/docs)
2. **Cloud Run Troubleshooting**: [https://cloud.google.com/run/docs/troubleshooting](https://cloud.google.com/run/docs/troubleshooting)
3. **Stack Overflow**: Tag questions with `google-cloud-run`
4. **GCP Support**: For production issues, contact [GCP Support](https://cloud.google.com/support)

---

## Related Documentation

- [Upload to Cloud Run Guide](./guide--upload-to-cloud-run.md)
- [Secret Management Guide](./guide--secret-management.md)
- [Architecture Reference](./reference--architecture.md)
