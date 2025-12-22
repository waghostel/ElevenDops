# ElevenDops Server Startup Script
# Automatically detects and kills processes on target ports before starting servers

param(
    [int]$FastAPIPort = 8000,
    [int]$StreamlitPort = 8501
)

Write-Host "🚀 ElevenDops Server Startup Script" -ForegroundColor Blue
Write-Host "FastAPI Port: $FastAPIPort" -ForegroundColor Cyan
Write-Host "Streamlit Port: $StreamlitPort" -ForegroundColor Cyan
Write-Host ""

# Function to kill processes on a specific port
function Kill-ProcessOnPort {
    param([int]$Port)
    
    Write-Host "🔍 Checking port $Port..." -ForegroundColor Blue
    
    # First attempt: Use netstat to find processes
    try {
        $netstatOutput = netstat -ano | Select-String ":$Port "
        if ($netstatOutput) {
            Write-Host "⚠️  Found processes on port $Port" -ForegroundColor Yellow
            
            foreach ($line in $netstatOutput) {
                if ($line -match "\s+(\d+)$") {
                    $pid = $matches[1]
                    try {
                        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                        if ($process) {
                            Write-Host "   🔪 Killing process: $($process.ProcessName) (PID: $pid)" -ForegroundColor Yellow
                            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                            Start-Sleep -Milliseconds 200
                        }
                    } catch {
                        Write-Host "   ⚠️  Could not kill process PID: $pid" -ForegroundColor Red
                    }
                }
            }
        }
    } catch {
        # Fallback to Get-NetTCPConnection
        try {
            $processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | 
                        Select-Object -ExpandProperty OwningProcess -Unique
            
            if ($processes) {
                Write-Host "⚠️  Found processes on port $Port (via NetTCP)" -ForegroundColor Yellow
                foreach ($pid in $processes) {
                    try {
                        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                        if ($process) {
                            Write-Host "   🔪 Killing process: $($process.ProcessName) (PID: $pid)" -ForegroundColor Yellow
                            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                            Start-Sleep -Milliseconds 200
                        }
                    } catch {
                        Write-Host "   ⚠️  Could not kill process PID: $pid" -ForegroundColor Red
                    }
                }
            }
        } catch {
            # Silent fallback
        }
    }
    
    # Wait a moment for processes to fully terminate
    Start-Sleep -Milliseconds 1000
    
    # Verify port is now free
    try {
        $stillRunning = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($stillRunning) {
            Write-Host "   ⚠️  Some processes may still be running on port $Port" -ForegroundColor Yellow
            # Try one more aggressive kill
            $pids = $stillRunning | Select-Object -ExpandProperty OwningProcess -Unique
            foreach ($pid in $pids) {
                try {
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                } catch { }
            }
            Start-Sleep -Milliseconds 500
        }
    } catch { }
    
    Write-Host "✅ Port $Port should now be available" -ForegroundColor Green
}

# Function to check if Poetry is installed
function Test-Poetry {
    try {
        $null = Get-Command poetry -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# Check Poetry installation
if (-not (Test-Poetry)) {
    Write-Host "❌ Poetry is not installed. Please install it first." -ForegroundColor Red
    Write-Host "   Install with: pip install poetry" -ForegroundColor Red
    exit 1
}

# Load environment variables from .env if it exists
if (Test-Path ".env") {
    Write-Host "📁 Loading .env file..." -ForegroundColor Green
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
} else {
    Write-Host "⚠️  No .env file found. Using default configuration." -ForegroundColor Yellow
    Write-Host "   Copy .env.example to .env to customize settings." -ForegroundColor Yellow
}

Write-Host ""

# Kill processes on target ports
Write-Host "🔍 Checking for existing processes..." -ForegroundColor Blue
Kill-ProcessOnPort -Port $FastAPIPort
Kill-ProcessOnPort -Port $StreamlitPort

Write-Host ""

# Start FastAPI server
Write-Host "🔧 Starting FastAPI backend on port $FastAPIPort..." -ForegroundColor Blue
$fastApiJob = Start-Job -ScriptBlock {
    param($port)
    Set-Location $using:PWD
    
    # Add more verbose output for debugging
    Write-Host "FastAPI Job: Starting uvicorn on port $port"
    Write-Host "FastAPI Job: Current directory: $(Get-Location)"
    Write-Host "FastAPI Job: Python path: $(poetry run python -c 'import sys; print(sys.executable)')"
    
    try {
        poetry run uvicorn backend.main:app --host 0.0.0.0 --port $port --reload
    } catch {
        Write-Host "FastAPI Job Error: $_"
        throw
    }
} -ArgumentList $FastAPIPort

# Wait for FastAPI to start
Write-Host "   ⏳ Waiting for FastAPI to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if FastAPI started successfully
$fastApiRunning = $false
$attempts = 0
$maxAttempts = 6

while ($attempts -lt $maxAttempts -and -not $fastApiRunning) {
    $attempts++
    try {
        Write-Host "   🔍 Attempt $attempts/$maxAttempts: Testing FastAPI connection..." -ForegroundColor Yellow
        $response = Invoke-WebRequest -Uri "http://localhost:$FastAPIPort/" -TimeoutSec 3 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $fastApiRunning = $true
            Write-Host "✅ FastAPI backend started successfully" -ForegroundColor Green
        }
    } catch {
        if ($attempts -eq $maxAttempts) {
            Write-Host "❌ FastAPI backend failed to start after $maxAttempts attempts" -ForegroundColor Red
            Write-Host "   📋 FastAPI Job Output:" -ForegroundColor Yellow
            $jobOutput = Receive-Job -Job $fastApiJob -Keep
            if ($jobOutput) {
                $jobOutput | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
            } else {
                Write-Host "   No output from FastAPI job" -ForegroundColor Gray
            }
        } else {
            Start-Sleep -Seconds 2
        }
    }
}

# Start Streamlit server
Write-Host "🎨 Starting Streamlit frontend on port $StreamlitPort..." -ForegroundColor Blue
$streamlitJob = Start-Job -ScriptBlock {
    param($port)
    Set-Location $using:PWD
    poetry run streamlit run streamlit_app/app.py --server.port $port --server.address 0.0.0.0
} -ArgumentList $StreamlitPort

# Wait for Streamlit to start
Start-Sleep -Seconds 5

# Check if Streamlit started successfully
$streamlitRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:$StreamlitPort/" -TimeoutSec 10 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        $streamlitRunning = $true
        Write-Host "✅ Streamlit frontend started successfully" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Streamlit frontend failed to start" -ForegroundColor Red
}

Write-Host ""
Write-Host "🌐 Server URLs:" -ForegroundColor Green
Write-Host "   FastAPI Backend:  http://localhost:$FastAPIPort" -ForegroundColor Cyan
Write-Host "   Streamlit Frontend: http://localhost:$StreamlitPort" -ForegroundColor Cyan
Write-Host ""

if ($fastApiRunning -and $streamlitRunning) {
    Write-Host "� Both servers are rrunning successfully!" -ForegroundColor Green
} elseif ($fastApiRunning) {
    Write-Host "⚠️  Only FastAPI is running. Check Streamlit logs." -ForegroundColor Yellow
} elseif ($streamlitRunning) {
    Write-Host "⚠️  Only Streamlit is running. Check FastAPI logs." -ForegroundColor Yellow
} else {
    Write-Host "❌ Both servers failed to start. Check the logs." -ForegroundColor Red
}

Write-Host ""
Write-Host "📝 Server Management:" -ForegroundColor Blue
Write-Host "   To stop servers: .\scripts\stop_server.ps1" -ForegroundColor Cyan
Write-Host "   To view logs: Get-Job | Receive-Job" -ForegroundColor Cyan
Write-Host "   Job IDs: FastAPI=$($fastApiJob.Id), Streamlit=$($streamlitJob.Id)" -ForegroundColor Cyan
Write-Host ""

# Store job IDs for the stop script
$jobIds = @{
    FastAPI = $fastApiJob.Id
    Streamlit = $streamlitJob.Id
    FastAPIPort = $FastAPIPort
    StreamlitPort = $StreamlitPort
}
$jobIds | ConvertTo-Json | Out-File -FilePath "scripts/.server_jobs.json" -Encoding UTF8

Write-Host "✅ Server startup complete!" -ForegroundColor Green