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

# Function to kill processes on a specific port
function Kill-ProcessOnPort {
    param([int]$Port)
    Write-Host "Checking port $Port..." -ForegroundColor Blue
    $netstatOutput = netstat -ano | Select-String ":$Port "
    if ($netstatOutput) {
        Write-Host "  Found processes on port $Port. Cleaning up..." -ForegroundColor Yellow
        foreach ($line in $netstatOutput) {
            if ($line -match "\s+(\d+)$") {
                $processId = $matches[1]
                if ($processId -ne "0") {
                    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                }
            }
        }
        Start-Sleep -Seconds 1
        Write-Host "  Port $Port cleared." -ForegroundColor Green
    }
    else {
        Write-Host "  Port $Port is free." -ForegroundColor Green
    }
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
keys = [
    'GOOGLE_CLOUD_PROJECT', 'GCS_BUCKET_NAME', 'FIRESTORE_DATABASE_ID',
    'USE_MOCK_DATA', 'USE_FIRESTORE_EMULATOR', 'USE_GCS_EMULATOR',
    'APP_ENV', 'GOOGLE_API_KEY', 'ELEVENLABS_API_KEY',
    'LANGSMITH_API_KEY', 'LANGSMITH_PROJECT', 'LANGSMITH_TRACING_ENABLED'
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
