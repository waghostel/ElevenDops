# Fake GCS Server

**Library**: `fsouza/fake-gcs-server`

## Overview

`fake-gcs-server` provides an emulator for the Google Cloud Storage API. It is written in Go and can be used as a standalone binary or Docker image.

## Docker Usage

We use this image in our `docker-compose.dev.yml`:

```yaml
gcs-emulator:
  image: fsouza/fake-gcs-server
  ports:
    - "4443:4443"
  command: -scheme http -port 4443 -backend memory
```

- **Port**: 4443
- **Backend**: Memory (data lost on restart)

## Client Connection (Python)

To connect to this emulator, you need to use `AnonymousCredentials` and override the `_base_url`.

```python
from google.cloud import storage
from google.auth.credentials import AnonymousCredentials

# Connect to emulator
client = storage.Client(
    credentials=AnonymousCredentials(),
    project="elevenlabs-local",
)

# CRITICAL: Override the API endpoint to point to localhost
client._http._base_url = "http://localhost:4443"

# Create a bucket
bucket = client.create_bucket("my-bucket")
```

## Known Limitations

- Does not support all GCS features (e.g. some complex IAM policies).
- By default uses in-memory storage, so data persists only as long as the container runs.
