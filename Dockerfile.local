# ElevenDops Docker Configuration
# Multi-stage build for Python application

FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install Poetry
RUN pip install poetry==1.7.1

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies without dev packages
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-interaction --no-ansi

# Production stage
FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    STREAMLIT_PORT=8501 \
    FASTAPI_PORT=8000

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser backend/ ./backend/
COPY --chown=appuser:appuser streamlit_app/ ./streamlit_app/
COPY --chown=appuser:appuser .env.example ./.env.example

# Switch to non-root user
USER appuser

# Expose ports for Streamlit and FastAPI
EXPOSE 8501 8000

# Health check - check FastAPI health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default command - run both services
# For Cloud Run, you may want to run only one service per container
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${FASTAPI_PORT} & streamlit run streamlit_app/app.py --server.port ${STREAMLIT_PORT} --server.address 0.0.0.0"]
