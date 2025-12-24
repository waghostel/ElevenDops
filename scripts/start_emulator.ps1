# ElevenDops Emulator Startup Script
# Starts the Firestore and GCS emulators using Docker Compose

Write-Host "🚀 Starting ElevenDops Development Emulators..." -ForegroundColor Blue
Write-Host ""

# Check if Docker is running
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker is not running"
    }
    Write-Host "✅ Docker is running" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Start emulators with Docker Compose
Write-Host "🔧 Starting Firestore Emulator and GCS Emulator..." -ForegroundColor Blue
try {
    $startOutput = docker-compose -f docker-compose.dev.yml up -d 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker-compose up failed:" -ForegroundColor Red
        Write-Host "   $startOutput" -ForegroundColor Gray
        exit 1
    }
}
catch {
    Write-Host "❌ Failed to start emulators: $_" -ForegroundColor Red
    exit 1
}

# Wait for services to initialize
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Verify containers are actually running
$maxRetries = 10
$retryCount = 0
$emulatorsReady = $false

while ($retryCount -lt $maxRetries -and -not $emulatorsReady) {
    $retryCount++
    
    # Use docker ps to check for running containers from our compose file
    $runningContainers = docker ps --filter "name=elevendops" --format "{{.Names}}" 2>&1
    $containerList = @($runningContainers -split "`n" | Where-Object { $_ -match "elevendops" })
    
    if ($containerList.Count -ge 2) {
        $emulatorsReady = $true
        Write-Host "✅ Both emulator containers are running" -ForegroundColor Green
        foreach ($container in $containerList) {
            Write-Host "   - $container" -ForegroundColor Cyan
        }
    }
    else {
        Write-Host "⏳ Waiting for containers... ($retryCount/$maxRetries) - found $($containerList.Count)" -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
}

if (-not $emulatorsReady) {
    Write-Host "❌ Not all emulators started properly" -ForegroundColor Red
    $containerStatus = docker ps -a --filter "name=elevendops" --format "table {{.Names}}\t{{.Status}}" 2>&1
    Write-Host "Container status:" -ForegroundColor Gray
    Write-Host "$containerStatus" -ForegroundColor Gray
    exit 1
}

# Test emulator connectivity
Write-Host ""
Write-Host "🔍 Testing emulator connectivity..." -ForegroundColor Blue

# Test Firestore emulator
$firestoreOk = $false
try {
    $firestoreResponse = Invoke-WebRequest -Uri "http://localhost:8080/" -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($firestoreResponse.StatusCode -eq 200 -or $firestoreResponse.StatusCode -eq 404) {
        $firestoreOk = $true
        Write-Host "   ✅ Firestore emulator responding at http://localhost:8080" -ForegroundColor Green
    }
}
catch {
    Write-Host "   ⚠️  Firestore emulator not responding yet" -ForegroundColor Yellow
}

# Test GCS emulator
$gcsOk = $false
try {
    $gcsResponse = Invoke-WebRequest -Uri "http://localhost:4443/storage/v1/b" -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($gcsResponse.StatusCode -eq 200) {
        $gcsOk = $true
        Write-Host "   ✅ GCS emulator responding at http://localhost:4443" -ForegroundColor Green
    }
}
catch {
    Write-Host "   ⚠️  GCS emulator not responding yet" -ForegroundColor Yellow
}

Write-Host ""
if ($firestoreOk -and $gcsOk) {
    Write-Host "🎉 Emulators are running and responding!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some emulators may not be fully ready. They may still be starting up." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🌐 Emulator URLs:" -ForegroundColor Blue
Write-Host "   Firestore Emulator: http://localhost:8080" -ForegroundColor Cyan
Write-Host "   GCS Emulator:       http://localhost:4443" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 To stop emulators run:" -ForegroundColor Blue
Write-Host "   docker-compose -f docker-compose.dev.yml down" -ForegroundColor Cyan
