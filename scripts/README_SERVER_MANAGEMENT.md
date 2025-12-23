# Server Management Scripts - Updated

## Summary of Changes

I've enhanced both `start_server.ps1` and `stop_server.ps1` to **automatically manage Docker emulators** for you.

## What's New

### `start_server.ps1`

✅ **Automatically starts Docker emulators** before launching servers

- Checks if Docker is running
- Starts Firestore Emulator (port 8080) and GCS Emulator (port 4443)
- Restarts emulators if they're already running
- Gracefully continues without emulators if Docker isn't available

### `stop_server.ps1`

✅ **Automatically stops Docker emulators** after stopping servers

- Stops and removes emulator containers
- Cleans up Docker resources
- Gracefully handles cases where Docker isn't running

## Usage

### Start Everything (Servers + Emulators)

```powershell
.\scripts\start_server.ps1
```

This will:

1. ✅ Start Docker emulators (Firestore + GCS)
2. ✅ Kill any processes on ports 8000 and 8501
3. ✅ Start FastAPI backend (port 8000)
4. ✅ Start Streamlit frontend (port 8501)

### Stop Everything (Servers + Emulators)

```powershell
.\scripts\stop_server.ps1
```

For aggressive cleanup:

```powershell
.\scripts\stop_server.ps1 -Force
```

This will:

1. ✅ Stop PowerShell background jobs
2. ✅ Kill processes on ports 8000 and 8501
3. ✅ Stop and remove Docker emulators
4. ✅ (With -Force) Kill all Python/uvicorn/streamlit processes

## Requirements

- **Docker Desktop** must be installed and running for emulators to work
- If Docker isn't running, the scripts will continue without emulators (backend may fail to connect)

## Testing the Backend

After starting the servers, test with:

```powershell
.\scripts\test_api.ps1
```

## Next Steps

1. **Start Docker Desktop** (if not already running)
2. Run `.\scripts\start_server.ps1`
3. Wait for all services to start (~10-15 seconds)
4. Test the backend with `.\scripts\test_api.ps1`
5. Access the frontend at http://localhost:8501

## Troubleshooting

**If emulators don't start:**

- Ensure Docker Desktop is running
- Check `docker-compose.dev.yml` exists in the project root
- Manually test: `docker-compose -f docker-compose.dev.yml up -d`

**If backend hangs:**

- The emulators might not be ready yet (wait a few more seconds)
- Check emulator status: `docker-compose -f docker-compose.dev.yml ps`
- View emulator logs: `docker-compose -f docker-compose.dev.yml logs`
