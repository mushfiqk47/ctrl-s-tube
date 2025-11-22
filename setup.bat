@echo off
REM Comprehensive setup script for Ctrl+S Tube
REM This script will:
REM   1. Check Python installation
REM   2. Create virtual environment
REM   3. Install all dependencies
REM   4. Check FFmpeg availability
REM   5. Build executable (optional)
REM   6. Clean unnecessary files

setlocal enabledelayedexpansion

TITLE Ctrl+S Tube - Comprehensive Setup
color 0A

echo =====================================================
echo           Ctrl+S Tube - Setup Script
echo =====================================================
echo.
echo This script will set up everything you need to run
echo Ctrl+S Tube on your machine.
echo.

REM ============================================================
REM Step 1: Check Python Installation
REM ============================================================
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found
echo.

REM ============================================================
REM Step 2: Create/Verify Virtual Environment
REM ============================================================
echo [2/6] Setting up virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment.
        echo Make sure you have the 'venv' module installed.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)
echo.

REM ============================================================
REM Step 3: Activate Virtual Environment
REM ============================================================
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM ============================================================
REM Step 4: Install/Update Dependencies
REM ============================================================
echo [4/6] Installing dependencies from requirements.txt...
echo This may take a few minutes...
echo.
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    echo Check your internet connection and try again.
    pause
    exit /b 1
)
echo [OK] All dependencies installed successfully
echo.

REM ============================================================
REM Step 5: Check FFmpeg Installation
REM ============================================================
echo [5/6] Checking FFmpeg installation...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] FFmpeg is not installed or not in PATH.
    echo.
    echo FFmpeg is REQUIRED for Ctrl+S Tube to work properly.
    echo.
    echo Please install FFmpeg from:
    echo https://ffmpeg.org/download.html
    echo.
    echo OR use Chocolatey: choco install ffmpeg
    echo.
    echo After installing FFmpeg, restart this script.
    echo.
) else (
    echo [OK] FFmpeg is installed and available
)
echo.

REM ============================================================
REM Step 6: Ask User if They Want to Build Executable
REM ============================================================
echo [6/6] Build executable?
echo.
echo Do you want to build a standalone .exe file?
echo This is optional - you can run the app with run.bat without building.
echo.
echo Building the executable will take 5-10 minutes.
echo.
set /p BUILD_EXE="Build executable now? (y/n): "

if /i "%BUILD_EXE%"=="y" (
    echo.
    echo Building executable with PyInstaller...
    echo This may take several minutes, please be patient...
    echo.
    
    REM Clean previous build files
    if exist build rd /s /q build
    if exist dist rd /s /q dist
    
    REM Build using the new spec file
    pyinstaller --clean --noconfirm CtrlSTube.spec
    
    if exist "dist\CtrlSTube.exe" (
        echo.
        echo ==========================================
        echo  BUILD SUCCESSFUL!
        echo ==========================================
        echo.
        echo Executable created: dist\CtrlSTube.exe
        echo.
        echo You can now distribute this .exe file to anyone!
        echo No Python installation required to run the .exe
        echo.
    ) else (
        echo.
        echo ==========================================
        echo  BUILD FAILED!
        echo ==========================================
        echo.
        echo The build may have failed. Check the output above.
        echo You can still run the app using run.bat
        echo.
    )
) else (
    echo.
    echo Skipping executable build.
    echo You can build later by running: build_exe.bat
    echo.
)

REM ============================================================
REM Step 7: Clean Unnecessary Files
REM ============================================================
echo.
echo Cleaning unnecessary files...
echo.

REM Remove Python cache files
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    echo Removing: %%d
    rd /s /q "%%d" 2>nul
)

REM Remove .pyc files
del /s /q *.pyc 2>nul

REM Remove old spec file if exists
if exist "YouTube_Downloader.spec" (
    echo Removing old spec file: YouTube_Downloader.spec
    del /q "YouTube_Downloader.spec"
)

echo [OK] Cleanup complete
echo.

REM ============================================================
REM Setup Complete
REM ============================================================
echo =====================================================
echo           SETUP COMPLETED SUCCESSFULLY!
echo =====================================================
echo.
echo Next steps:
echo   1. Make sure FFmpeg is installed (if not already)
echo   2. Run the application using: run.bat
echo   3. Or double-click: dist\CtrlSTube.exe (if you built it)
echo.
echo For help and documentation, see README.md
echo.
echo Thank you for using Ctrl+S Tube!
echo.
pause
endlocal
