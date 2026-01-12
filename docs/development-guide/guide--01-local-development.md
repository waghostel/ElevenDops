# Local Development Infrastructure Guide

This guide describes how to set up and run the ElevenDops development environment using local emulators for Google Cloud services. This ensures you can develop without an internet connection or incurring cloud costs.

## Prerequisites

1. **Docker Desktop**: Must be installed and running.
2. **Python 3.10+**: With Poetry installed.
3. **Environment**: Windows, macOS, or Linux.

## Quick Start

1. **Clone the repository** (if not already done).
2. **Install dependencies**:
   ```bash
   poetry install
   ```
3. **Configure Environment**:
   Copy `.env.example` to `.env`:

   ```bash
   cp .env.example .env
   ```

   _Note: Default settings are pre-configured for local emulators. For detailed parameter management, see [Configuration Management Guide](./guide--configuration-management.md)._

4. **Start Emulators**:

   **Windows**:

   ```batch
   scripts\start_emulators.bat
   ```

   **Linux/Mac**:

   ```bash
   ./scripts/start_emulators.sh
   ```

   This will start:

   - **Firestore Emulator**: `http://localhost:8080`
   - **GCS Emulator**: `http://localhost:4443`

## Verifying Setup

### 1. Check Service Status

Run `docker-compose -f docker-compose.dev.yml ps` to see running containers.

### 2. Check API Health

Start the backend server (if not already running):

```bash
poetry run uvicorn backend.main:app --reload
```

Visit `http://localhost:8000/api/health`. You should see:

```json
{
  "status": "healthy",
  "services": {
    "firestore": { "status": "healthy", "emulator": true },
    "storage": { "status": "healthy", "emulator": true }
  }
}
```

### 3. Check Emulator Access

- **Firestore**: Open `http://localhost:8080` (might show "Ok" or similar)
- **GCS**: Open `http://localhost:4443/storage/v1/b` (lists buckets)

## Using in Code

The infrastructure is abstracted via service wrappers. Always use these services instead of initializing clients directly.

### Firestore

```python
from backend.services.firestore_service import get_firestore_service

service = get_firestore_service()
doc = service.db.collection("users").document("test").get()
```

### storage

```python
from backend.services.storage_service import get_storage_service

service = get_storage_service()
url = service.upload_file(b"data", "test.txt")
```

## Troubleshooting

### "Docker is not running"

Ensure Docker Desktop is started.

### "Connection Refused"

Ensure emulators are running via the start script. Check `docker logs` if containers exit immediately.

### "Buckets do not exist"

The `StorageService` automatically creates the default bucket (`elevenlabs-audio`) on initialization. Ensure you initialize the service at least once.
