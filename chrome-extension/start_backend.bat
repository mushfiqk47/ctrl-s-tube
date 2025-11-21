@echo off
echo Starting Ctrl+S Tube Backend Service...
echo.

cd /d "%~dp0"

:: Check if python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

:: Create venv if it doesn't exist
if not exist "backend\venv" (
    echo Creating virtual environment...
    python -m venv backend\venv
)

:: Activate venv
call backend\venv\Scripts\activate

:: Install dependencies
echo Installing dependencies...
pip install -r backend\requirements.txt

:: Run server
echo.
echo Backend server is ready!
echo Keep this window open while using the Chrome Extension.
echo.
python backend\server.py

pause
