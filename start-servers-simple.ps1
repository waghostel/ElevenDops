# start-servers-simple.ps1
# A simple script that starts both FastAPI and Streamlit servers
# with the correct environment variables from .env
#
# Usage: .\start-servers-simple.ps1
# To stop: Close the terminal windows that open

param(
    [int]$FastAPIPort = 8000,
    [int]$StreamlitPort = 8501
)

# Change to the script's directory (project root)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "=== Simple Server Launcher ===" -ForegroundColor Cyan
Write-Host "Working directory: $scriptDir" -ForegroundColor DarkGray
Write-Host ""

# Function to check if a port is in use and return PIDs
function Get-ProcessIdsOnPort {
    param([int]$Port)
    $pids = @()
    $netstatOutput = netstat -ano | Select-String "LISTENING" | Select-String ":$Port "
    foreach ($line in $netstatOutput) {
        if ($line -match "\s+(\d+)$") {
            $pid = $matches[1]
            if ($pid -ne "0" -and $pids -notcontains $pid) {
                $pids += $pid
            }
        }
    }
    return $pids
}

# Function to kill processes on a specific port with retries and verification
function Kill-ProcessOnPort {
    param([int]$Port)
    
    $maxRetries = 3
    $retryCount = 0
    
    Write-Host "Checking port $Port..." -ForegroundColor Blue
    
    while ($retryCount -lt $maxRetries) {
        $processIds = Get-ProcessIdsOnPort -Port $Port
        
        if ($processIds.Count -eq 0) {
            if ($retryCount -eq 0) {
                Write-Host "  Port $Port is free." -ForegroundColor Green
            }
            else {
                Write-Host "  Port $Port cleared after $retryCount attempt(s)." -ForegroundColor Green
            }
            return $true
        }
        
        $retryCount++
        Write-Host "  Found $($processIds.Count) process(es) on port $Port. Attempt $retryCount of $maxRetries..." -ForegroundColor Yellow
        
        foreach ($pid in $processIds) {
            try {
                # First try PowerShell's Stop-Process
                $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($proc) {
                    Write-Host "    Killing PID $pid ($($proc.ProcessName))..." -ForegroundColor DarkYellow
                }
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                
                # If still running, use taskkill /F for forceful termination
                Start-Sleep -Milliseconds 500
                $stillRunning = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($stillRunning) {
                    Write-Host "    Using taskkill /F for stubborn PID $pid..." -ForegroundColor DarkYellow
                    $null = taskkill /F /PID $pid 2>&1
                }
            }
            catch {
                # Silently continue - process might already be gone
            }
        }
        
        # Wait for OS to release the port
        Start-Sleep -Seconds 1
    }
    
    # Final verification
    $remainingPids = Get-ProcessIdsOnPort -Port $Port
    if ($remainingPids.Count -gt 0) {
        Write-Host ""
        Write-Host "  [WARNING] Failed to free port $Port after $maxRetries attempts!" -ForegroundColor Red
        Write-Host "  Remaining PIDs: $($remainingPids -join ', ')" -ForegroundColor Red
        Write-Host "  Try running this script as Administrator, or manually kill the processes." -ForegroundColor Red
        Write-Host ""
        return $false
    }
    
    Write-Host "  Port $Port cleared." -ForegroundColor Green
    return $true
}

# Kill any existing processes on our ports
Kill-ProcessOnPort -Port $FastAPIPort
Kill-ProcessOnPort -Port $StreamlitPort

# Use Python with dotenv to load and export environment variables
# This avoids any hardcoding and uses the same library the app uses
$pythonScript = @'
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Print all relevant env vars in KEY=VALUE format for PowerShell to parse
# This list should match the core variables in backend/config.py Settings class
keys = [
    # GCP & Credentials
    'GOOGLE_CLOUD_PROJECT', 'GOOGLE_APPLICATION_CREDENTIALS', 'GOOGLE_API_KEY',
    # GCS
    'GCS_BUCKET_NAME', 'USE_GCS_EMULATOR', 'GCS_EMULATOR_HOST', 'USE_MOCK_STORAGE',
    # Firestore
    'FIRESTORE_DATABASE_ID', 'USE_FIRESTORE_EMULATOR', 'FIRESTORE_EMULATOR_HOST', 'USE_MOCK_DATA',
    # App & Server
    'APP_ENV', 'DEBUG', 'FASTAPI_PORT', 'STREAMLIT_PORT', 'CORS_ORIGINS',
    # ElevenLabs
    'ELEVENLABS_API_KEY', 'USE_MOCK_ELEVENLABS',
    # LangSmith
    'LANGSMITH_API_KEY', 'LANGSMITH_PROJECT', 'LANGSMITH_TRACING_ENABLED', 'LANGSMITH_TRACE_LEVEL',
]
for key in keys:
    val = os.getenv(key, '')
    if val:
        # Strip trailing/leading spaces to be safe
        print(f'{key}={val.strip()}')
'@


Write-Host "Loading environment from .env using Python dotenv..." -ForegroundColor Blue
$envOutput = uv run python -c $pythonScript

if (-not $envOutput) {
    Write-Host "[ERROR] Failed to load .env file. Make sure .env exists in $scriptDir" -ForegroundColor Red
    exit 1
}

# Build the SET commands for cmd.exe using quoted "KEY=VAL" syntax for safety
# We use no spaces around && to avoid trailing spaces in values
$setCmds = ($envOutput | ForEach-Object { "set `"$_`"" }) -join "&&"

Write-Host "Starting FastAPI on port $FastAPIPort..." -ForegroundColor Blue
Start-Process cmd.exe -ArgumentList "/k", "title FastAPI Backend && cd /d `"$scriptDir`" && $setCmds && uv run uvicorn backend.main:app --host localhost --port $FastAPIPort" -WorkingDirectory $scriptDir

Start-Sleep -Seconds 2

Write-Host "Starting Streamlit on port $StreamlitPort..." -ForegroundColor Blue
Start-Process cmd.exe -ArgumentList "/k", "title Streamlit Frontend && cd /d `"$scriptDir`" && $setCmds && uv run streamlit run streamlit_app/app.py --server.port $StreamlitPort --server.address localhost" -WorkingDirectory $scriptDir

Write-Host ""
Write-Host "=== Servers Starting ===" -ForegroundColor Green
Write-Host "FastAPI:   http://localhost:$FastAPIPort" -ForegroundColor Cyan
Write-Host "Streamlit: http://localhost:$StreamlitPort" -ForegroundColor Cyan
Write-Host ""
Write-Host "Two new terminal windows opened. Close them to stop the servers." -ForegroundColor Yellow
