# ElevenDops Server Stop Script
# Stops all running ElevenDops servers and cleans up processes

param(
    [int]$FastAPIPort = 8000,
    [int]$StreamlitPort = 8501,
    [switch]$Force
)

Write-Host "🛑 ElevenDops Server Stop Script" -ForegroundColor Blue
Write-Host ""

# Function to kill processes on a specific port
function Kill-ProcessOnPort {
    param([int]$Port, [string]$ServiceName)
    
    try {
        $processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | 
                    Select-Object -ExpandProperty OwningProcess -Unique
        
        if ($processes) {
            Write-Host "🔍 Found $ServiceName processes on port $Port" -ForegroundColor Yellow
            $killedCount = 0
            foreach ($pid in $processes) {
                try {
                    $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                    if ($process) {
                        Write-Host "   Stopping: $($process.ProcessName) (PID: $pid)" -ForegroundColor Yellow
                        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                        $killedCount++
                        Start-Sleep -Milliseconds 300
                    }
                } catch {
                    Write-Host "   Could not stop process PID: $pid" -ForegroundColor Red
                }
            }
            if ($killedCount -gt 0) {
                Write-Host "✅ Stopped $killedCount $ServiceName process(es)" -ForegroundColor Green
            }
        } else {
            Write-Host "✅ No $ServiceName processes found on port $Port" -ForegroundColor Green
        }
    } catch {
        Write-Host "✅ No $ServiceName processes found on port $Port" -ForegroundColor Green
    }
}

# Function to stop PowerShell jobs
function Stop-ServerJobs {
    # Try to read job IDs from the stored file
    if (Test-Path "scripts/.server_jobs.json") {
        try {
            $jobInfo = Get-Content "scripts/.server_jobs.json" | ConvertFrom-Json
            Write-Host "📋 Found stored job information" -ForegroundColor Blue
            
            # Stop FastAPI job
            if ($jobInfo.FastAPI) {
                $job = Get-Job -Id $jobInfo.FastAPI -ErrorAction SilentlyContinue
                if ($job) {
                    Write-Host "   Stopping FastAPI job (ID: $($jobInfo.FastAPI))" -ForegroundColor Yellow
                    Stop-Job -Id $jobInfo.FastAPI -ErrorAction SilentlyContinue
                    Remove-Job -Id $jobInfo.FastAPI -Force -ErrorAction SilentlyContinue
                }
            }
            
            # Stop Streamlit job
            if ($jobInfo.Streamlit) {
                $job = Get-Job -Id $jobInfo.Streamlit -ErrorAction SilentlyContinue
                if ($job) {
                    Write-Host "   Stopping Streamlit job (ID: $($jobInfo.Streamlit))" -ForegroundColor Yellow
                    Stop-Job -Id $jobInfo.Streamlit -ErrorAction SilentlyContinue
                    Remove-Job -Id $jobInfo.Streamlit -Force -ErrorAction SilentlyContinue
                }
            }
            
            # Update ports from stored info if available
            if ($jobInfo.FastAPIPort) { $script:FastAPIPort = $jobInfo.FastAPIPort }
            if ($jobInfo.StreamlitPort) { $script:StreamlitPort = $jobInfo.StreamlitPort }
            
            # Clean up the job file
            Remove-Item "scripts/.server_jobs.json" -Force -ErrorAction SilentlyContinue
            Write-Host "✅ Cleaned up job information" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Could not read job information file" -ForegroundColor Yellow
        }
    }
    
    # Stop any remaining PowerShell jobs that might be related to our servers
    $allJobs = Get-Job -ErrorAction SilentlyContinue
    if ($allJobs) {
        Write-Host "🧹 Cleaning up remaining PowerShell jobs..." -ForegroundColor Blue
        foreach ($job in $allJobs) {
            if ($job.Command -like "*uvicorn*" -or $job.Command -like "*streamlit*") {
                Write-Host "   Stopping job: $($job.Name) (ID: $($job.Id))" -ForegroundColor Yellow
                Stop-Job -Id $job.Id -ErrorAction SilentlyContinue
                Remove-Job -Id $job.Id -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

# Function to kill processes by name (more aggressive cleanup)
function Kill-ProcessByName {
    param([string[]]$ProcessNames)
    
    foreach ($processName in $ProcessNames) {
        $processes = Get-Process -Name $processName -ErrorAction SilentlyContinue
        if ($processes) {
            Write-Host "🔍 Found $($processes.Count) $processName process(es)" -ForegroundColor Yellow
            foreach ($process in $processes) {
                # Check if this process is likely related to our servers
                $commandLine = ""
                try {
                    $commandLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($process.Id)").CommandLine
                } catch {}
                
                if ($commandLine -like "*backend.main:app*" -or 
                    $commandLine -like "*streamlit_app/app.py*" -or 
                    $commandLine -like "*uvicorn*backend*" -or
                    $commandLine -like "*streamlit*run*streamlit_app*") {
                    Write-Host "   Stopping ElevenDops ${processName}: PID $($process.Id)" -ForegroundColor Yellow
                    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
                }
            }
        }
    }
}

# Main execution
Write-Host "🔍 Stopping ElevenDops servers..." -ForegroundColor Blue
Write-Host ""

# Step 1: Stop PowerShell jobs first
Stop-ServerJobs

# Step 2: Kill processes on specific ports
Kill-ProcessOnPort -Port $FastAPIPort -ServiceName "FastAPI"
Kill-ProcessOnPort -Port $StreamlitPort -ServiceName "Streamlit"

# Step 3: If Force flag is used, do more aggressive cleanup
if ($Force) {
    Write-Host ""
    Write-Host "⚡ Force mode: Performing aggressive cleanup..." -ForegroundColor Yellow
    Kill-ProcessByName -ProcessNames @("python", "uvicorn", "streamlit")
}

# Step 4: Final verification
Write-Host ""
Write-Host "🔍 Final verification..." -ForegroundColor Blue

$fastApiStill = $false
$streamlitStill = $false

try {
    $fastApiProcesses = Get-NetTCPConnection -LocalPort $FastAPIPort -ErrorAction SilentlyContinue
    if ($fastApiProcesses) { $fastApiStill = $true }
} catch {}

try {
    $streamlitProcesses = Get-NetTCPConnection -LocalPort $StreamlitPort -ErrorAction SilentlyContinue
    if ($streamlitProcesses) { $streamlitStill = $true }
} catch {}

if (-not $fastApiStill -and -not $streamlitStill) {
    Write-Host "🎉 All ElevenDops servers stopped successfully!" -ForegroundColor Green
    Write-Host "✅ Ports $FastAPIPort and $StreamlitPort are now available" -ForegroundColor Green
} else {
    if ($fastApiStill) {
        Write-Host "⚠️  Some processes may still be running on port $FastAPIPort" -ForegroundColor Red
    }
    if ($streamlitStill) {
        Write-Host "⚠️  Some processes may still be running on port $StreamlitPort" -ForegroundColor Red
    }
    Write-Host "💡 Try running with -Force flag for aggressive cleanup" -ForegroundColor Yellow
}

Write-Host ""

# Stop Docker emulators
Write-Host "🐳 Stopping Docker emulators..." -ForegroundColor Blue
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ℹ️  Docker is not running. No emulators to stop." -ForegroundColor Gray
    } else {
        # Check if emulators are running
        $runningContainers = docker-compose -f docker-compose.dev.yml ps -q 2>&1
        if ($runningContainers) {
            Write-Host "   🛑 Stopping emulators..." -ForegroundColor Yellow
            docker-compose -f docker-compose.dev.yml down 2>&1 | Out-Null
            Write-Host "   ✅ Emulators stopped successfully" -ForegroundColor Green
        } else {
            Write-Host "   ℹ️  No emulators running" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "   ⚠️  Could not stop emulators: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Blue
Write-Host "   To start servers: .\scripts\start_server.ps1" -ForegroundColor Cyan
Write-Host "   To check ports: netstat -an | findstr :$FastAPIPort" -ForegroundColor Cyan
Write-Host ""