@echo off
setlocal enabledelayedexpansion

TITLE Media Downloader Launcher

REM Check if virtual environment exists
if not exist "venv" (
    echo [INFO] First run detected or venv missing.
    echo [INFO] Running setup...
    call setup.bat
    if errorlevel 1 exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Launch the application
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application crashed or closed with an error.
    pause
)

deactivate
endlocal
