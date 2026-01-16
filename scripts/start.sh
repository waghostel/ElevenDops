#!/bin/bash
# ElevenDops Cloud Run Process Manager
# Manages both FastAPI backend and Streamlit frontend in a single container
# Requirements: 1.4, 1.5, 1.6, 9.1, 9.2, 9.3, 9.4, 9.5

set -e

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=${PORT:-8501}
HEALTH_CHECK_TIMEOUT=30
HEALTH_CHECK_INTERVAL=1
MONITOR_INTERVAL=5
MAX_RESTART_ATTEMPTS=3

# Set PYTHONPATH to current directory to allow module imports from the root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Process tracking
BACKEND_PID=""
FRONTEND_PID=""
BACKEND_RESTART_COUNT=0
FRONTEND_RESTART_COUNT=0
SHUTDOWN_REQUESTED=false

# Logging functions for structured output (Requirement 9.5)
log_info() {
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] INFO: $1"
}

log_error() {
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] ERROR: $1" >&2
}

log_warn() {
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] WARN: $1"
}

# Start FastAPI backend (Requirement 1.5 - listen on internal port 8000)
start_backend() {
    log_info "Starting FastAPI backend on port $BACKEND_PORT..."
    uvicorn backend.main:app --host 0.0.0.0 --port $BACKEND_PORT &
    BACKEND_PID=$!
    log_info "Backend started with PID $BACKEND_PID"
}

# Wait for backend health check (Requirement 9.1 - start backend before frontend)
wait_for_backend() {
    log_info "Waiting for backend to be ready..."
    local attempts=0
    
    while [ $attempts -lt $HEALTH_CHECK_TIMEOUT ]; do
        if curl -s http://localhost:$BACKEND_PORT/api/health > /dev/null 2>&1; then
            log_info "Backend is ready and healthy"
            return 0
        fi
        attempts=$((attempts + 1))
        sleep $HEALTH_CHECK_INTERVAL
    done
    
    log_error "Backend failed to start within $HEALTH_CHECK_TIMEOUT seconds"
    return 1
}

# Start Streamlit frontend (Requirement 1.6 - listen on PORT env variable)
start_frontend() {
    log_info "Starting Streamlit frontend on port $FRONTEND_PORT..."
    streamlit run streamlit_app/app.py \
        --server.port=$FRONTEND_PORT \
        --server.address=0.0.0.0 \
        --server.headless=true \
        --browser.gatherUsageStats=false &
    FRONTEND_PID=$!
    log_info "Frontend started with PID $FRONTEND_PID"
}


# Graceful shutdown handler (Requirement 9.4)
graceful_shutdown() {
    log_info "Received shutdown signal, initiating graceful shutdown..."
    SHUTDOWN_REQUESTED=true
    
    # Send SIGTERM to both processes
    if [ -n "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
        log_info "Stopping frontend (PID $FRONTEND_PID)..."
        kill -TERM $FRONTEND_PID 2>/dev/null || true
    fi
    
    if [ -n "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
        log_info "Stopping backend (PID $BACKEND_PID)..."
        kill -TERM $BACKEND_PID 2>/dev/null || true
    fi
    
    # Wait for processes to terminate (up to 10 seconds)
    local wait_count=0
    while [ $wait_count -lt 10 ]; do
        local still_running=false
        
        if [ -n "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
            still_running=true
        fi
        
        if [ -n "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
            still_running=true
        fi
        
        if [ "$still_running" = false ]; then
            break
        fi
        
        sleep 1
        wait_count=$((wait_count + 1))
    done
    
    # Force kill if still running
    if [ -n "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
        log_warn "Force killing frontend..."
        kill -9 $FRONTEND_PID 2>/dev/null || true
    fi
    
    if [ -n "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
        log_warn "Force killing backend..."
        kill -9 $BACKEND_PID 2>/dev/null || true
    fi
    
    log_info "Shutdown complete"
    exit 0
}

# Set up signal traps (Requirement 9.4)
trap graceful_shutdown SIGTERM SIGINT SIGQUIT

# Check if a process is running
is_process_running() {
    local pid=$1
    if [ -n "$pid" ] && kill -0 $pid 2>/dev/null; then
        return 0
    fi
    return 1
}

# Monitor and restart processes (Requirements 9.2, 9.3)
monitor_processes() {
    while [ "$SHUTDOWN_REQUESTED" = false ]; do
        # Check backend process (Requirement 9.2)
        if ! is_process_running $BACKEND_PID; then
            if [ $BACKEND_RESTART_COUNT -lt $MAX_RESTART_ATTEMPTS ]; then
                log_warn "Backend process died, restarting (attempt $((BACKEND_RESTART_COUNT + 1))/$MAX_RESTART_ATTEMPTS)..."
                BACKEND_RESTART_COUNT=$((BACKEND_RESTART_COUNT + 1))
                start_backend
                
                # Wait for backend to be healthy before continuing
                if ! wait_for_backend; then
                    log_error "Backend failed to restart properly"
                fi
            else
                log_error "Backend exceeded maximum restart attempts ($MAX_RESTART_ATTEMPTS), exiting..."
                graceful_shutdown
            fi
        fi
        
        # Check frontend process (Requirement 9.3)
        if ! is_process_running $FRONTEND_PID; then
            if [ $FRONTEND_RESTART_COUNT -lt $MAX_RESTART_ATTEMPTS ]; then
                log_warn "Frontend process died, restarting (attempt $((FRONTEND_RESTART_COUNT + 1))/$MAX_RESTART_ATTEMPTS)..."
                FRONTEND_RESTART_COUNT=$((FRONTEND_RESTART_COUNT + 1))
                start_frontend
            else
                log_error "Frontend exceeded maximum restart attempts ($MAX_RESTART_ATTEMPTS), exiting..."
                graceful_shutdown
            fi
        fi
        
        sleep $MONITOR_INTERVAL
    done
}


# Main execution
main() {
    log_info "=========================================="
    log_info "ElevenDops Cloud Run Process Manager"
    log_info "=========================================="
    log_info "Backend port: $BACKEND_PORT"
    log_info "Frontend port: $FRONTEND_PORT"
    log_info "Health check timeout: ${HEALTH_CHECK_TIMEOUT}s"
    log_info "Monitor interval: ${MONITOR_INTERVAL}s"
    log_info "Max restart attempts: $MAX_RESTART_ATTEMPTS"
    log_info "=========================================="
    
    # Requirement 9.1: Start backend first
    start_backend
    
    # Wait for backend to be healthy before starting frontend
    if ! wait_for_backend; then
        log_error "Backend failed to start, exiting..."
        exit 1
    fi
    
    # Start frontend after backend is ready
    start_frontend
    
    log_info "All services started successfully"
    log_info "Backend PID: $BACKEND_PID, Frontend PID: $FRONTEND_PID"
    
    # Enter monitoring loop
    monitor_processes
}

# Run main function
main
