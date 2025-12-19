@echo off
echo Starting ElevenDops Development Emulators...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Start emulators with Docker Compose
echo Starting Firestore Emulator and GCS Emulator...
docker-compose -f docker-compose.dev.yml up -d

REM Wait for services to be healthy
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check service health
echo.
echo Checking service status...
docker-compose -f docker-compose.dev.yml ps

echo.
echo Emulators are running!
echo - Firestore Emulator: http://localhost:8080
echo - GCS Emulator: http://localhost:4443
echo.
echo To stop emulators, run: docker-compose -f docker-compose.dev.yml down
pause
