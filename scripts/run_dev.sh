#!/usr/bin/env bash
# Run both Streamlit and FastAPI servers for local development
# Also starts Docker emulators for Firestore and GCS

set -e

echo "🚀 Starting ElevenDops Development Environment..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}❌ Poetry is not installed. Please install it first.${NC}"
    echo "   Install with: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Load environment variables if .env exists
if [ -f .env ]; then
    echo -e "${GREEN}📁 Loading .env file...${NC}"
    export $(grep -v '^#' .env | xargs)
else
    echo -e "${YELLOW}⚠️  No .env file found. Using default configuration.${NC}"
    echo "   Copy .env.example to .env to customize settings."
fi

# Set default ports
FASTAPI_PORT=${FASTAPI_PORT:-8000}
STREAMLIT_PORT=${STREAMLIT_PORT:-8501}

echo ""

# ==========================================
# Start Docker Emulators
# ==========================================
echo -e "${CYAN}🐳 Starting Docker emulators...${NC}"

if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Docker is running${NC}"
    
    # Start emulators
    echo -e "${CYAN}   🚀 Starting/ensuring emulators are running...${NC}"
    if docker-compose -f docker-compose.dev.yml up -d 2>&1; then
        sleep 5
        
        # Verify containers are running
        container_count=$(docker ps --filter "name=elevendops" --format "{{.Names}}" | grep -c "elevendops" || echo "0")
        
        if [ "$container_count" -ge 2 ]; then
            echo -e "${GREEN}   ✅ Both emulator containers are running${NC}"
            # Set environment variables for emulator mode
            export FIRESTORE_EMULATOR_HOST="localhost:8080"
            export STORAGE_EMULATOR_HOST="http://localhost:4443"
            export USE_FIRESTORE_EMULATOR="true"
            export USE_GCS_EMULATOR="true"
            export GOOGLE_CLOUD_PROJECT="elevenlabs-local"
            export USE_MOCK_DATA="false"
            export USE_MOCK_STORAGE="false"
        else
            echo -e "${YELLOW}   ⚠️  Not all emulators started, falling back to mock mode${NC}"
            export USE_MOCK_DATA="true"
            export USE_MOCK_STORAGE="true"
        fi
    else
        echo -e "${YELLOW}   ⚠️  Failed to start emulators, falling back to mock mode${NC}"
        export USE_MOCK_DATA="true"
        export USE_MOCK_STORAGE="true"
    fi
else
    echo -e "${YELLOW}   ⚠️  Docker is not running. Using mock mode.${NC}"
    export USE_MOCK_DATA="true"
    export USE_MOCK_STORAGE="true"
fi

echo ""
echo -e "${GREEN}📡 FastAPI will run on: http://localhost:${FASTAPI_PORT}${NC}"
echo -e "${GREEN}🖥️  Streamlit will run on: http://localhost:${STREAMLIT_PORT}${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down servers...${NC}"
    kill $(jobs -p) 2>/dev/null
    
    # Also stop Docker emulators
    if docker info > /dev/null 2>&1; then
        echo -e "${YELLOW}🐳 Stopping Docker emulators...${NC}"
        docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
    fi
    
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start FastAPI in background
echo -e "${GREEN}🔧 Starting FastAPI backend...${NC}"
poetry run uvicorn backend.main:app --host 0.0.0.0 --port $FASTAPI_PORT --reload &

# Give FastAPI a moment to start
sleep 2

# Start Streamlit in background
echo -e "${GREEN}🎨 Starting Streamlit frontend...${NC}"
poetry run streamlit run streamlit_app/app.py --server.port $STREAMLIT_PORT --server.address 0.0.0.0 &

echo ""
echo -e "${GREEN}✅ Both servers are running!${NC}"
echo ""
echo "Press Ctrl+C to stop all servers and emulators."
echo ""

# Wait for all background jobs
wait
