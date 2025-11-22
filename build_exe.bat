@echo off
REM Build script for Ctrl+S Tube executable

echo ==========================================
echo  Ctrl+S Tube - Build Script
echo ==========================================
echo.

echo Cleaning previous build files...
if exist build rd /s /q build
if exist dist rd /s /q dist

echo.
echo Building executable with PyInstaller...
echo This may take a few minutes...
echo.

pyinstaller --clean --noconfirm CtrlSTube.spec

echo.
if exist "dist\CtrlSTube.exe" (
    echo ==========================================
    echo  BUILD SUCCESSFUL!
    echo ==========================================
    echo.
    echo Executable created: dist\CtrlSTube.exe
    echo Size: ~58 MB
    echo.
    echo Copying executable to main folder...
    copy "dist\CtrlSTube.exe" "Ctrl+S Tube.exe" >nul
    echo Copied to: Ctrl+S Tube.exe
    echo.
    echo You can now run the application by double-clicking:
    echo   - dist\CtrlSTube.exe
    echo   - Ctrl+S Tube.exe (in main folder)
    echo.
    echo This .exe can be distributed to other users!
    echo No Python installation required to run it.
    echo.
) else (
    echo ==========================================
    echo  BUILD FAILED!
    echo ==========================================
    echo.
    echo Please check the error messages above.
    echo Make sure PyInstaller is installed: pip install pyinstaller
    echo.
)

pause
