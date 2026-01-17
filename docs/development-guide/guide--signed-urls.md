# Using Signed URLs for GCS

This guide explains how to generate and use Google Cloud Storage (GCS) signed URLs in the ElevenDops application, both locally and in Cloud Run.

---

## Overview

Signed URLs provide time-limited, secure access to private GCS objects without requiring users to authenticate with Google Cloud. This is essential for:

- **Audio playback** in the browser
- **File downloads** for private documents
- **Secure sharing** without exposing bucket contents publicly

---

## IAM Permissions Required

### For Cloud Run Deployment

The Cloud Run service account needs **two** IAM bindings:

1. **Project-Level**: Storage Object Admin (for reading files)
2. **Self-Impersonation**: Service Account Token Creator (for signing URLs)

```bash
# Get project variables
$PROJECT_ID = gcloud config get-value project
$PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"
$SA_EMAIL = "${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# 1. Grant Storage Object Admin (read/write bucket)
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SA_EMAIL" `
    --role="roles/storage.objectAdmin"

# 2. Grant Token Creator at PROJECT level
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SA_EMAIL" `
    --role="roles/iam.serviceAccountTokenCreator"

# 3. Grant Token Creator for SELF-IMPERSONATION (critical for signBlob API)
gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL `
    --member="serviceAccount:$SA_EMAIL" `
    --role="roles/iam.serviceAccountTokenCreator" `
    --project=$PROJECT_ID
```

> [!IMPORTANT]
> Step 3 (self-impersonation) is often missed. Without it, the IAM `signBlob` API returns `INVALID_ARGUMENT`.

---

## Backend Code

### Core Function: `get_signed_url()`

Location: `backend/services/storage_service.py`

```python
from datetime import timedelta
from google.cloud import storage
import google.auth
from google.auth import compute_engine

def get_signed_url(storage_path: str, expiration_seconds: int = 3600) -> str:
    """Generate a signed URL for temporary GCS access."""
    bucket = storage.Client().bucket("your-bucket-name")
    blob = bucket.blob(storage_path)

    credentials, _ = google.auth.default()

    # Check if running on Compute Engine (Cloud Run/GCE)
    if isinstance(credentials, compute_engine.Credentials):
        # Cloud Run: Use IAM signBlob API
        service_account_email = credentials.service_account_email

        # Handle 'default' placeholder
        if service_account_email == "default":
            import requests
            url = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email"
            response = requests.get(url, headers={"Metadata-Flavor": "Google"}, timeout=2)
            service_account_email = response.text.strip()

        # Refresh token if needed
        if not credentials.token:
            import google.auth.transport.requests
            credentials.refresh(google.auth.transport.requests.Request())

        return blob.generate_signed_url(
            version="v4",
            expiration=timedelta(seconds=expiration_seconds),
            method="GET",
            service_account_email=service_account_email,
            access_token=credentials.token
        )
    else:
        # Local dev with SA key file: Sign locally
        return blob.generate_signed_url(
            version="v4",
            expiration=timedelta(seconds=expiration_seconds),
            method="GET",
        )
```

### Usage in Audio Service

Location: `backend/services/audio_service.py`

```python
from backend.services.storage_service import get_signed_url

class AudioService:
    async def get_audio_files(self, doctor_id: str) -> List[AudioMetadata]:
        audio_files = await self.db.get_audio_files(doctor_id)

        # Sign each audio URL before returning
        for audio in audio_files:
            audio.audio_url = get_signed_url(audio.storage_path)

        return audio_files
```

---

## Frontend Code

### API Client

Location: `streamlit_app/services/backend_api.py`

```python
def _resolve_audio_url(base_url: str, audio_url: str) -> str:
    """Resolve audio URL - signed URLs are already absolute."""
    # Signed GCS URLs and emulator URLs are already absolute
    if audio_url.startswith("http://") or audio_url.startswith("https://"):
        return audio_url
    # Fallback for relative paths (shouldn't happen in production)
    return f"{base_url}/api/storage/files/{audio_url}"
```

### Streamlit Audio Player

Location: `streamlit_app/pages/3_Education_Audio.py`

```python
# The audio_url from backend is already a signed URL
st.audio(audio.audio_url, format="audio/mpeg")
```

---

## Environment Differences

| Environment        | Signing Method                               | IAM Required                   |
| :----------------- | :------------------------------------------- | :----------------------------- |
| **Local (SA Key)** | Signs locally using private key in JSON file | None (key has signing power)   |
| **Cloud Run**      | Uses IAM `signBlob` API with access token    | Token Creator (self + project) |
| **GCS Emulator**   | No signing - returns direct emulator URL     | None                           |

---

## Troubleshooting

### Error: "you need a private key to sign credentials"

**Cause**: Code is trying to sign locally but credentials don't have a private key (Cloud Run).
**Fix**: Use IAM signing with `service_account_email` and `access_token` parameters.

### Error: "INVALID_ARGUMENT" from IAM signBytes API

**Cause**: Service account email is `"default"` instead of actual email.
**Fix**: Fetch actual email from metadata server (see code above).

### Error: "Permission denied on signBlob"

**Cause**: Missing self-impersonation IAM binding.
**Fix**: Run the self-impersonation command from Step 3 above.

### Audio shows 0:00 / 0:00 in browser

**Cause**: URL is not signed (raw GCS URL) and bucket is private.
**Fix**: Verify backend is returning signed URLs (check for `Signature=` in URL).

---

## Quick Reference

```bash
# Verify a URL is signed (should see Signature parameter)
curl -I "YOUR_SIGNED_URL" | grep -i "content-type"

# Check Cloud Run logs for signing issues
gcloud logging read "resource.labels.service_name=YOUR_SERVICE AND textPayload:signed" --limit 10
```
