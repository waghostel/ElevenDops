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
}
catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Start emulators with Docker Compose
Write-Host "🔧 Starting Firestore Emulator and GCS Emulator..." -ForegroundColor Blue
try {
    docker-compose -f docker-compose.dev.yml up -d
}
catch {
    Write-Host "❌ Failed to start emulators: $_" -ForegroundColor Red
    exit 1
}

# Wait a moment for services to initialize
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check service health
Write-Host ""
Write-Host "🔍 Checking service status..." -ForegroundColor Blue
docker-compose -f docker-compose.dev.yml ps

Write-Host ""
Write-Host "✅ Emulators are running!" -ForegroundColor Green
Write-Host "   Firestore Emulator: http://localhost:8080" -ForegroundColor Cyan
Write-Host "   GCS Emulator:       http://localhost:4443" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 To stop emulators run:" -ForegroundColor Blue
Write-Host "   docker-compose -f docker-compose.dev.yml down" -ForegroundColor Cyan
