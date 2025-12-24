#!/bin/bash
set -e

echo "🚀 Starting ElevenDops Development Emulators..."
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"

# Start emulators with Docker Compose
echo -e "${CYAN}🔧 Starting Firestore Emulator and GCS Emulator...${NC}"
if ! docker-compose -f docker-compose.dev.yml up -d 2>&1; then
    echo -e "${RED}❌ Failed to start emulators${NC}"
    exit 1
fi

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 5

# Verify containers are actually running
max_retries=10
retry_count=0
emulators_ready=false

while [ $retry_count -lt $max_retries ] && [ "$emulators_ready" = false ]; do
    retry_count=$((retry_count + 1))
    
    # Count running containers
    container_count=$(docker ps --filter "name=elevendops" --format "{{.Names}}" | grep -c "elevendops" || echo "0")
    
    if [ "$container_count" -ge 2 ]; then
        emulators_ready=true
        echo -e "${GREEN}✅ Both emulator containers are running${NC}"
        docker ps --filter "name=elevendops" --format "   - {{.Names}}"
    else
        echo -e "${YELLOW}⏳ Waiting for containers... ($retry_count/$max_retries) - found $container_count${NC}"
        sleep 2
    fi
done

if [ "$emulators_ready" = false ]; then
    echo -e "${RED}❌ Not all emulators started properly${NC}"
    echo "Container status:"
    docker ps -a --filter "name=elevendops" --format "table {{.Names}}\t{{.Status}}"
    exit 1
fi

# Test emulator connectivity
echo
echo -e "${CYAN}🔍 Testing emulator connectivity...${NC}"

# Test Firestore emulator
firestore_ok=false
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ | grep -qE "200|404"; then
    firestore_ok=true
    echo -e "   ${GREEN}✅ Firestore emulator responding at http://localhost:8080${NC}"
else
    echo -e "   ${YELLOW}⚠️  Firestore emulator not responding yet${NC}"
fi

# Test GCS emulator
gcs_ok=false
if curl -s -o /dev/null -w "%{http_code}" http://localhost:4443/storage/v1/b | grep -q "200"; then
    gcs_ok=true
    echo -e "   ${GREEN}✅ GCS emulator responding at http://localhost:4443${NC}"
else
    echo -e "   ${YELLOW}⚠️  GCS emulator not responding yet${NC}"
fi

echo
if [ "$firestore_ok" = true ] && [ "$gcs_ok" = true ]; then
    echo -e "${GREEN}🎉 Emulators are running and responding!${NC}"
else
    echo -e "${YELLOW}⚠️  Some emulators may not be fully ready. They may still be starting up.${NC}"
fi

echo
echo -e "${CYAN}🌐 Emulator URLs:${NC}"
echo "   - Firestore Emulator: http://localhost:8080"
echo "   - GCS Emulator: http://localhost:4443"
echo
echo "To stop emulators, run: docker-compose -f docker-compose.dev.yml down"
