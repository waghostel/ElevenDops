@echo off
REM Run both Streamlit and FastAPI servers for local development (Windows)

echo.
echo 🚀 Starting ElevenDops Development Servers...
echo.

REM Check if poetry is available
where poetry >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Poetry is not installed. Please install it first.
    echo    Install with: pip install poetry
    exit /b 1
)

REM Load environment variables if .env exists
if exist .env (
    echo 📁 Loading .env file...
    for /f "tokens=*" %%a in ('type .env ^| findstr /v "^#"') do set %%a
) else (
    echo ⚠️  No .env file found. Using default configuration.
    echo    Copy .env.example to .env to customize settings.
)

REM Set default ports
if not defined FASTAPI_PORT set FASTAPI_PORT=8000
if not defined STREAMLIT_PORT set STREAMLIT_PORT=8501

echo.
echo 📡 FastAPI will run on: http://localhost:%FASTAPI_PORT%
echo 🖥️  Streamlit will run on: http://localhost:%STREAMLIT_PORT%
echo.

REM Start FastAPI in a new window
echo 🔧 Starting FastAPI backend...
start "ElevenDops FastAPI" cmd /c "poetry run uvicorn backend.main:app --host 0.0.0.0 --port %FASTAPI_PORT% --reload"

REM Wait a moment for FastAPI to start
timeout /t 2 /nobreak >nul

REM Start Streamlit in a new window
echo 🎨 Starting Streamlit frontend...
start "ElevenDops Streamlit" cmd /c "poetry run streamlit run streamlit_app/app.py --server.port %STREAMLIT_PORT% --server.address 0.0.0.0"

echo.
echo ✅ Both servers are starting in separate windows!
echo.
echo Close the server windows to stop the servers.
echo.
