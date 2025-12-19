@echo off
REM Quick stop script for ElevenDops servers
REM This is a simple wrapper around the PowerShell script

echo 🛑 Stopping ElevenDops Servers...
echo.

REM Check if PowerShell is available
where powershell >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ PowerShell is not available. Please install PowerShell.
    pause
    exit /b 1
)

REM Execute the PowerShell stop script
powershell -ExecutionPolicy Bypass -File "scripts\stop_server.ps1"

echo.
echo Press any key to exit...
pause >nul