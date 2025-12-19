# ElevenDops Server Management Scripts

This directory contains PowerShell scripts for managing ElevenDops development servers with automatic port conflict resolution.

## 🚀 Quick Start

### Simple Commands (Batch Files)
```cmd
# Start servers (from project root)
start_server.bat

# Stop servers (from project root)
stop_server.bat
```

### PowerShell Commands
```powershell
# Start servers
.\scripts\start_server.ps1

# Stop servers
.\scripts\stop_server.ps1

# Unified management
.\scripts\manage_server.ps1 start
.\scripts\manage_server.ps1 stop
.\scripts\manage_server.ps1 restart
.\scripts\manage_server.ps1 status
```

## 📋 Features

### Automatic Port Management
- **Port Detection**: Automatically detects processes running on target ports
- **Process Cleanup**: Kills existing processes before starting new servers
- **Conflict Resolution**: Ensures clean startup without port conflicts

### Default Ports
- **FastAPI Backend**: `8000`
- **Streamlit Frontend**: `8501`

### Custom Ports
```powershell
# Use custom ports
.\scripts\start_server.ps1 -FastAPIPort 8080 -StreamlitPort 8502
.\scripts\stop_server.ps1 -FastAPIPort 8080 -StreamlitPort 8502
```

## 🛠️ Script Details

### `start_server.ps1`
- Kills processes on target ports
- Starts FastAPI backend in background job
- Starts Streamlit frontend in background job
- Verifies both servers are responding
- Stores job information for cleanup

### `stop_server.ps1`
- Stops PowerShell background jobs
- Kills processes on target ports
- Cleans up job information files
- Supports `-Force` flag for aggressive cleanup

### `manage_server.ps1`
- Unified interface for all server operations
- Status checking with health verification
- Restart functionality with proper sequencing
- Color-coded output for better visibility

## 🔧 Advanced Usage

### Force Stop (Aggressive Cleanup)
```powershell
# Force stop all related processes
.\scripts\stop_server.ps1 -Force
.\scripts\manage_server.ps1 stop -Force
```

### Status Checking
```powershell
# Check if servers are running and responding
.\scripts\manage_server.ps1 status
```

### Restart Servers
```powershell
# Clean restart (stop + start)
.\scripts\manage_server.ps1 restart
```

## 🐛 Troubleshooting

### Port Already in Use
The scripts automatically handle port conflicts, but if you encounter issues:

1. **Check what's using the port**:
   ```cmd
   netstat -an | findstr :8000
   netstat -an | findstr :8501
   ```

2. **Force stop everything**:
   ```powershell
   .\scripts\stop_server.ps1 -Force
   ```

3. **Manual process kill**:
   ```cmd
   taskkill /F /IM python.exe
   taskkill /F /IM uvicorn.exe
   ```

### PowerShell Execution Policy
If you get execution policy errors:
```powershell
# Temporarily allow script execution
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Or run with bypass flag
powershell -ExecutionPolicy Bypass -File "scripts\start_server.ps1"
```

### Job Management
View and manage background jobs:
```powershell
# List all jobs
Get-Job

# View job output
Get-Job | Receive-Job

# Stop specific job
Stop-Job -Id <JobId>
Remove-Job -Id <JobId>
```

## 📁 File Structure

```
scripts/
├── start_server.ps1      # Main startup script
├── stop_server.ps1       # Main stop script
├── manage_server.ps1     # Unified management script
├── .server_jobs.json     # Job tracking (auto-generated)
└── README.md            # This file

# Root level convenience scripts
start_server.bat         # Windows batch wrapper
stop_server.bat          # Windows batch wrapper
```

## 🔄 Integration with Existing Scripts

The new PowerShell scripts complement the existing development scripts:

- `scripts/run_dev.bat` - Original Windows batch script
- `scripts/run_dev.sh` - Original Unix shell script

The PowerShell scripts provide enhanced features:
- Better port conflict handling
- Process management
- Status verification
- Job tracking and cleanup

## 💡 Tips

1. **Use the unified script** for most operations:
   ```powershell
   .\scripts\manage_server.ps1 restart
   ```

2. **Check status before starting**:
   ```powershell
   .\scripts\manage_server.ps1 status
   ```

3. **Use Force flag** if normal stop doesn't work:
   ```powershell
   .\scripts\manage_server.ps1 stop -Force
   ```

4. **Custom ports** for multiple environments:
   ```powershell
   .\scripts\start_server.ps1 -FastAPIPort 8080 -StreamlitPort 8502
   ```