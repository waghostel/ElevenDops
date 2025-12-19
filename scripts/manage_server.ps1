# ElevenDops Server Management Script
# Unified script to start, stop, restart, and check server status

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status")]
    [string]$Action,
    
    [int]$FastAPIPort = 8000,
    [int]$StreamlitPort = 8501,
    [switch]$Force
)

function Show-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Blue
    Write-Host "  $Title" -ForegroundColor Blue
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Blue
    Write-Host ""
}

function Test-ServerStatus {
    param([int]$Port, [string]$ServiceName)
    
    try {
        $processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($processes) {
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:$Port/" -TimeoutSec 3 -UseBasicParsing -ErrorAction SilentlyContinue
                if ($response.StatusCode -eq 200) {
                    Write-Host "✅ $ServiceName is running on port $Port" -ForegroundColor Green
                    return $true
                }
            } catch {}
            Write-Host "⚠️  Process found on port $Port but $ServiceName not responding" -ForegroundColor Yellow
            return $false
        } else {
            Write-Host "❌ $ServiceName is not running on port $Port" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ $ServiceName is not running on port $Port" -ForegroundColor Red
        return $false
    }
}

function Show-Status {
    Show-Header "🔍 ElevenDops Server Status"
    
    Write-Host "Checking server status..." -ForegroundColor Cyan
    Write-Host ""
    
    $fastApiRunning = Test-ServerStatus -Port $FastAPIPort -ServiceName "FastAPI Backend"
    $streamlitRunning = Test-ServerStatus -Port $StreamlitPort -ServiceName "Streamlit Frontend"
    
    Write-Host ""
    
    if ($fastApiRunning -and $streamlitRunning) {
        Write-Host "🎉 All services are running!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🌐 Access URLs:" -ForegroundColor Cyan
        Write-Host "   FastAPI Backend:    http://localhost:$FastAPIPort" -ForegroundColor White
        Write-Host "   Streamlit Frontend: http://localhost:$StreamlitPort" -ForegroundColor White
    } elseif ($fastApiRunning -or $streamlitRunning) {
        Write-Host "⚠️  Partial service availability" -ForegroundColor Yellow
    } else {
        Write-Host "❌ No services are running" -ForegroundColor Red
    }
    
    Write-Host ""
}

function Start-Servers {
    Show-Header "🚀 Starting ElevenDops Servers"
    
    # Check current status first
    $fastApiRunning = Test-ServerStatus -Port $FastAPIPort -ServiceName "FastAPI Backend"
    $streamlitRunning = Test-ServerStatus -Port $StreamlitPort -ServiceName "Streamlit Frontend"
    
    if ($fastApiRunning -and $streamlitRunning) {
        Write-Host "✅ Both servers are already running!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🌐 Access URLs:" -ForegroundColor Cyan
        Write-Host "   FastAPI Backend:    http://localhost:$FastAPIPort" -ForegroundColor White
        Write-Host "   Streamlit Frontend: http://localhost:$StreamlitPort" -ForegroundColor White
        return
    }
    
    Write-Host "Starting servers with automatic port cleanup..." -ForegroundColor Blue
    Write-Host ""
    
    # Execute the start script
    & ".\scripts\start_server.ps1" -FastAPIPort $FastAPIPort -StreamlitPort $StreamlitPort
}

function Stop-Servers {
    Show-Header "🛑 Stopping ElevenDops Servers"
    
    Write-Host "Stopping all ElevenDops servers..." -ForegroundColor Blue
    Write-Host ""
    
    # Execute the stop script
    if ($Force) {
        & ".\scripts\stop_server.ps1" -FastAPIPort $FastAPIPort -StreamlitPort $StreamlitPort -Force
    } else {
        & ".\scripts\stop_server.ps1" -FastAPIPort $FastAPIPort -StreamlitPort $StreamlitPort
    }
}

function Restart-Servers {
    Show-Header "🔄 Restarting ElevenDops Servers"
    
    Write-Host "Performing server restart..." -ForegroundColor Blue
    Write-Host ""
    
    # Stop first
    Write-Host "Step 1: Stopping existing servers..." -ForegroundColor Yellow
    if ($Force) {
        & ".\scripts\stop_server.ps1" -FastAPIPort $FastAPIPort -StreamlitPort $StreamlitPort -Force
    } else {
        & ".\scripts\stop_server.ps1" -FastAPIPort $FastAPIPort -StreamlitPort $StreamlitPort
    }
    
    Write-Host ""
    Write-Host "Step 2: Waiting for cleanup..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    
    Write-Host ""
    Write-Host "Step 3: Starting servers..." -ForegroundColor Yellow
    & ".\scripts\start_server.ps1" -FastAPIPort $FastAPIPort -StreamlitPort $StreamlitPort
}

# Main execution
switch ($Action.ToLower()) {
    "start" { Start-Servers }
    "stop" { Stop-Servers }
    "restart" { Restart-Servers }
    "status" { Show-Status }
}

Write-Host ""
Write-Host "📝 Available commands:" -ForegroundColor Blue
Write-Host "   .\scripts\manage_server.ps1 start    # Start servers" -ForegroundColor Cyan
Write-Host "   .\scripts\manage_server.ps1 stop     # Stop servers" -ForegroundColor Cyan
Write-Host "   .\scripts\manage_server.ps1 restart  # Restart servers" -ForegroundColor Cyan
Write-Host "   .\scripts\manage_server.ps1 status   # Check status" -ForegroundColor Cyan
Write-Host "   Add -Force for aggressive cleanup" -ForegroundColor Cyan
Write-Host ""