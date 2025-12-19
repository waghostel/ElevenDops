#!/bin/bash
set -e

echo "Starting ElevenDops Development Emulators..."
echo

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running. Please start Docker first."
    exit 1
fi

# Start emulators with Docker Compose
echo "Starting Firestore Emulator and GCS Emulator..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be healthy
echo "Waiting for services to be ready..."
sleep 10

# Check service health
echo
echo "Checking service status..."
docker-compose -f docker-compose.dev.yml ps

echo
echo "Emulators are running!"
echo "- Firestore Emulator: http://localhost:8080"
echo "- GCS Emulator: http://localhost:4443"
echo
echo "To stop emulators, run: docker-compose -f docker-compose.dev.yml down"
