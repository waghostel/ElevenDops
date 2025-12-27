# Server Modes: Mock vs. Emulator

ElevenDops supports two primary local development modes: **Local Mock Mode** and **Docker Emulator Mode**.

## 1. Local Mock Mode (Default Fallback)

This mode allows you to run the application **without Docker** or any external dependencies. It uses in-memory data structures and the local file system.

- **Status**: Data is **NOT persistent** (lost on restart). Files are stored in `temp_storage/`.
- **Requirements**: None (just Python).
- **Activation**: Automatically enabled if Docker is missing.
- **Manual Configuration** (`.env`):
  ```properties
  USE_MOCK_DATA=true
  USE_MOCK_STORAGE=true
  USE_FIRESTORE_EMULATOR=false
  USE_GCS_EMULATOR=false
  ```

## 2. Docker Emulator Mode (Recommended)

This mode uses the official Google Cloud Emulators running in Docker containers to simulate a production-like environment.

- **Status**: Data is persistent (if volume mounted) or follows container lifecycle.
- **Requirements**: Docker Desktop installed and running.
- **Activation**: Automatically enabled by `start_server.ps1` if Docker is detected and `.env` is configured correctly.
- **Manual Configuration** (`.env`):

  ```properties
  USE_MOCK_DATA=false
  USE_MOCK_STORAGE=false
  USE_FIRESTORE_EMULATOR=true
  USE_GCS_EMULATOR=true

  # Emulator Hosts (Standard Docker Ports)
  FIRESTORE_EMULATOR_HOST=localhost:8080
  STORAGE_EMULATOR_HOST=http://localhost:4443
  ```

## Switching Modes

1. **Edit `.env`**: Change the variables as shown above.
2. **Restart Server**:
   ```powershell
   .\scripts\stop_server.ps1 -Force
   .\scripts\start_server.ps1
   ```

### Troubleshooting

- If you have Docker running but the app stays in Mock Mode, check your `.env` file and ensure `USE_MOCK_DATA=false`.
- Check the health status at `http://localhost:8000/api/health`.
