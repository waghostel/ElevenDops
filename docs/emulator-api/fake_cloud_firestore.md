# Fake Cloud Firestore Emulator

**Library**: `atn832/fake_cloud_firestore`

## Overview

Provides an in-memory fake implementation of Cloud Firestore. It is useful for unit testing and local development without needing the heavy official Java-based emulator.

## Installation & Usage

### 1. Install Firebase CLI

The official emulator is part of Firebase tools.

```bash
curl -sL https://firebase.tools | bash
```

### 2. Start Emulator

```bash
firebase emulators:start --only firestore
```

By default, it runs on `http://localhost:8080`.

## Docker Usage

We use the official Google Cloud SDK image in keeping with `docker-compose.dev.yml`:

```yaml
firestore-emulator:
  image: google/cloud-sdk:emulators
  command: >
    gcloud emulators firestore start
    --host-port=0.0.0.0:8080
    --project=elevenlabs-local
  ports:
    - "8080:8080"
```

## Client Connection (Python)

To connect your python client to the emulator, set the `FIRESTORE_EMULATOR_HOST` environment variable.

```python
import os
from google.cloud import firestore

# Set emulator host
os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"

# Initialize client (project ID is required but can be anything)
db = firestore.Client(project="elevenlabs-local")
```
