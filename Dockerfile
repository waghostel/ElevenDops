# ElevenDops Cloud Run Dockerfile
# Single container with both FastAPI and Streamlit
# Uses uv for fast, reliable dependency management

FROM python:3.11-slim-bookworm

# Configure environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    APP_ENV=production \
    PORT=8080

# Install system dependencies
# curl: for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (The Astral recommended way)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /app

# Install dependencies
# Copy only files needed for installation first to cache this layer
COPY pyproject.toml uv.lock ./

# Sync dependencies using valid uv.lock
# --frozen: ensure lock file is respected
# --no-dev: production only
# --no-install-project: specific application files are copied later
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code
COPY --chown=appuser:appuser backend/ ./backend/
COPY --chown=appuser:appuser streamlit_app/ ./streamlit_app/
# Note: start.sh is assumed to be in scripts/ based on previous file exploration
COPY --chown=appuser:appuser scripts/start.sh ./start.sh

# Make start script executable
RUN chmod +x ./start.sh

# Switch to non-root user
USER appuser

# Add virtualenv and app root to PATH/PYTHONPATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app"

# Expose port (Cloud Run sets PORT env var, but this documents intent)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start services
CMD ["./start.sh"]
