#!/usr/bin/env bash
# Run both Streamlit and FastAPI servers for local development

set -e

echo "🚀 Starting ElevenDops Development Servers..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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
echo -e "${GREEN}📡 FastAPI will run on: http://localhost:${FASTAPI_PORT}${NC}"
echo -e "${GREEN}🖥️  Streamlit will run on: http://localhost:${STREAMLIT_PORT}${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down servers...${NC}"
    kill $(jobs -p) 2>/dev/null
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
echo "Press Ctrl+C to stop both servers."
echo ""

# Wait for all background jobs
wait
