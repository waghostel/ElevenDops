@echo off
REM Quick start script for ElevenDops servers
REM This is a simple wrapper around the PowerShell script

echo 🚀 Starting ElevenDops Servers...
echo.

REM Check if PowerShell is available
where powershell >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ PowerShell is not available. Please install PowerShell.
    pause
    exit /b 1
)

REM Execute the PowerShell start script
powershell -ExecutionPolicy Bypass -File "scripts\start_server.ps1"

echo.
echo Press any key to exit...
pause >nul