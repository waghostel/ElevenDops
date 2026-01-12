# start-backend.ps1 - Helper script for verify--gcp-migration.ps1
# This script is called with environment variables already set

param(
    [int]$Port = 8000
)

# The calling script sets these env vars before invoking us
Write-Host "Starting FastAPI backend on port $Port..."
Write-Host "  Project: $env:GOOGLE_CLOUD_PROJECT"
Write-Host "  DB: $env:FIRESTORE_DATABASE_ID"
Write-Host "  Mock: $env:USE_MOCK_DATA"

uv run uvicorn backend.main:app --host localhost --port $Port
