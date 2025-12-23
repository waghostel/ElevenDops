# ElevenDops

🏥 **Intelligent Medical Assistant System** integrating ElevenLabs voice technology for medical education.

## Overview

ElevenDops is an intelligent medical assistant system designed to enhance medical education through advanced voice technology powered by ElevenLabs. The platform provides realistic patient simulations, natural voice interactions, and comprehensive knowledge management for medical educators and students.

## Architecture

- **Frontend**: Streamlit (MVP prototyping) - designed for future migration to React/TypeScript Next.js
- **Backend**: FastAPI RESTful API
- **Database**: Google Cloud Firestore (mock data service for development)
- **Deployment**: Google Cloud Run

## Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/) for dependency management

## Quick Start

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd ElevenDops

# Install dependencies with Poetry
poetry install
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
# Required for production: ELEVENLABS_API_KEY, GOOGLE_CLOUD_PROJECT
```

### 3. Run Development Servers

**Windows:**

```bash
.\scripts\run_dev.bat
```

**Linux/macOS:**

```bash
chmod +x scripts/run_dev.sh
./scripts/run_dev.sh
```

**Or run individually:**

```bash
# Terminal 1: FastAPI Backend
poetry run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Streamlit Frontend
poetry run streamlit run streamlit_app/app.py --server.port 8501
```

### 3a. Server Management (Recommended for Windows)

Using the PowerShell scripts in `scripts/` provides advanced management features including auto-detection of Docker for emulator support.

```powershell
# Start servers (Auto-detects Docker/Mock Mode)
.\scripts\start_server.ps1

# Stop servers
.\scripts\stop_server.ps1
```

See [Server Modes & Configuration](docs/SERVER_MODES.md) for details on switching between Local Mock Mode and Docker Emulator Mode.

### 4. Access the Application

- **Streamlit Frontend**: http://localhost:8501
- **FastAPI Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Project Structure

```
ElevenDops/
├── backend/                    # FastAPI backend
│   ├── api/                    # API endpoints
│   │   ├── dashboard.py        # Dashboard stats endpoint
│   │   └── health.py           # Health check endpoint
│   ├── models/                 # Pydantic models
│   │   └── schemas.py          # Response schemas
│   ├── services/               # Business logic
│   │   └── data_service.py     # Data access layer
│   ├── config.py               # Configuration management
│   └── main.py                 # FastAPI application
├── streamlit_app/              # Streamlit frontend
│   ├── pages/                  # Streamlit pages
│   │   └── 1_Doctor_Dashboard.py
│   ├── services/               # Frontend services
│   │   ├── backend_api.py      # Backend API client
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── models.py           # Data models
│   ├── components/             # Reusable UI components
│   └── app.py                  # Main application
├── tests/                      # Test suite
│   ├── test_models_props.py    # Pydantic model tests
│   ├── test_endpoints_props.py # API endpoint tests
│   ├── test_backend_api_props.py # API client tests
│   └── test_config_props.py    # Configuration tests
├── scripts/                    # Development scripts
│   ├── run_dev.sh              # Unix dev script
│   └── run_dev.bat             # Windows dev script
├── pyproject.toml              # Poetry configuration
├── Dockerfile                  # Docker configuration
├── .env.example                # Environment template
└── README.md                   # This file
```

## API Endpoints

| Endpoint               | Method | Description                                  |
| ---------------------- | ------ | -------------------------------------------- |
| `/api/health`          | GET    | Health check with status, timestamp, version |
| `/api/dashboard/stats` | GET    | Dashboard statistics                         |

## Running Tests

```bash
# Run all tests
poetry run pytest tests/ -v

# Run with coverage
poetry run pytest tests/ -v --cov=backend --cov=streamlit_app

# Run specific test file
poetry run pytest tests/test_config_props.py -v
```

## Docker Deployment

```bash
# Build the Docker image
docker build -t elevendops:latest .

# Run the container
docker run -p 8501:8501 -p 8000:8000 \
    -e ELEVENLABS_API_KEY=your_key \
    -e GOOGLE_CLOUD_PROJECT=your_project \
    elevendops:latest
```

## Environment Variables

| Variable               | Required | Default                 | Description                                  |
| ---------------------- | -------- | ----------------------- | -------------------------------------------- |
| `APP_ENV`              | No       | `development`           | Environment (development/staging/production) |
| `DEBUG`                | No       | `true`                  | Enable debug mode                            |
| `BACKEND_API_URL`      | No       | `http://localhost:8000` | Backend API URL                              |
| `ELEVENLABS_API_KEY`   | Prod     | -                       | ElevenLabs API key                           |
| `GOOGLE_CLOUD_PROJECT` | Prod     | -                       | Google Cloud project ID                      |
| `STREAMLIT_PORT`       | No       | `8501`                  | Streamlit server port                        |
| `FASTAPI_PORT`         | No       | `8000`                  | FastAPI server port                          |

## License

© 2024 ElevenDops Team. All rights reserved.
