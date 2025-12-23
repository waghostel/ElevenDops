# ElevenDops API Verification Script
# Tests key backend endpoints to ensure the server is responding correctly

param(
    [string]$BaseUrl = "http://localhost:8000"
)

Write-Host "🚀 Testing ElevenDops Backend API at $BaseUrl" -ForegroundColor Blue
Write-Host ""

function Test-Endpoint {
    param(
        [string]$Path,
        [string]$Description
    )

    $url = "$BaseUrl$Path"
    Write-Host "🔍 Testing $Description ($Path)..." -NoNewline

    try {
        $response = Invoke-WebRequest -Uri $url -Method Get -UseBasicParsing -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            Write-Host " OK (200)" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host " Failed ($($response.StatusCode))" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host " Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# 1. Root Endpoint
Test-Endpoint -Path "/" -Description "Root Endpoint"

# 2. Health Check
Test-Endpoint -Path "/api/health" -Description "Health Check"

# 3. Dashboard Stats
Test-Endpoint -Path "/api/dashboard/stats" -Description "Dashboard Statistics"

# 4. Agent List
Test-Endpoint -Path "/api/agent" -Description "Agent List"

# 5. Conversation Logs
Test-Endpoint -Path "/api/conversations" -Description "Conversation Logs"

Write-Host ""
Write-Host "✅ API Test Complete" -ForegroundColor Blue
