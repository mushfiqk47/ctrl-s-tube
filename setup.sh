#!/bin/bash

# Comprehensive setup script for Ctrl+S Tube (macOS/Linux)
# This script will:
#   1. Check Python installation
#   2. Create virtual environment
#   3. Install all dependencies
#   4. Check FFmpeg availability
#   5. Build executable (optional)
#   6. Clean unnecessary files

# Text colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=====================================================${NC}"
echo -e "${GREEN}          Ctrl+S Tube - Setup Script (macOS/Linux)${NC}"
echo -e "${GREEN}=====================================================${NC}"
echo ""
echo "This script will set up everything you need to run"
echo "Ctrl+S Tube on your machine."
echo ""

# ============================================================
# Step 1: Check Python Installation
# ============================================================
echo -e "${YELLOW}[1/6] Checking Python installation...${NC}"

if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    # Check if python is version 3
    VER=$(python -c"import sys; print(sys.version_info.major)")
    if [ $VER -eq 3 ]; then
        PYTHON_CMD=python
    else
        echo -e "${RED}[ERROR] Python 3 is not installed or not in your PATH.${NC}"
        echo "Please install Python 3.8 or higher."
        exit 1
    fi
else
    echo -e "${RED}[ERROR] Python 3 is not installed or not in your PATH.${NC}"
    echo "Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version)
echo -e "${GREEN}[OK] $PYTHON_VERSION found${NC}"
echo ""

# ============================================================
# Step 2: Create/Verify Virtual Environment
# ============================================================
echo -e "${YELLOW}[2/6] Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to create virtual environment.${NC}"
        echo "Make sure you have the 'venv' module installed."
        echo "On Ubuntu/Debian: sudo apt install python3-venv"
        exit 1
    fi
    echo -e "${GREEN}[OK] Virtual environment created${NC}"
else
    echo -e "${GREEN}[OK] Virtual environment already exists${NC}"
fi
echo ""

# ============================================================
# Step 3: Activate Virtual Environment
# ============================================================
echo -e "${YELLOW}[3/6] Activating virtual environment...${NC}"
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Failed to activate virtual environment.${NC}"
    exit 1
fi
echo -e "${GREEN}[OK] Virtual environment activated${NC}"
echo ""

# ============================================================
# Step 4: Install/Update Dependencies
# ============================================================
echo -e "${YELLOW}[4/6] Installing dependencies from requirements.txt...${NC}"
echo "This may take a few minutes..."
echo ""
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Failed to install dependencies.${NC}"
    echo "Check your internet connection and try again."
    exit 1
fi
echo -e "${GREEN}[OK] All dependencies installed successfully${NC}"
echo ""

# ============================================================
# Step 5: Check FFmpeg Installation
# ============================================================
echo -e "${YELLOW}[5/6] Checking FFmpeg installation...${NC}"
if command -v ffmpeg &>/dev/null; then
    echo -e "${GREEN}[OK] FFmpeg is installed and available${NC}"
else
    echo -e "${YELLOW}[WARNING] FFmpeg is not installed or not in PATH.${NC}"
    echo ""
    echo "FFmpeg is REQUIRED for Ctrl+S Tube to work properly."
    echo ""
    echo "Please install FFmpeg:"
    echo "  - macOS (Homebrew): brew install ffmpeg"
    echo "  - Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  - Fedora: sudo dnf install ffmpeg"
    echo "  - Arch: sudo pacman -S ffmpeg"
    echo ""
    echo "After installing FFmpeg, restart this script."
fi
echo ""

# ============================================================
# Step 6: Ask User if They Want to Build Executable
# ============================================================
echo -e "${YELLOW}[6/6] Build executable?${NC}"
echo ""
echo "Do you want to build a standalone executable file?"
echo "This is optional - you can run the app with ./run.sh without building."
echo ""
echo "Building the executable will take 5-10 minutes."
echo ""
read -p "Build executable now? (y/n): " BUILD_EXE

if [[ "$BUILD_EXE" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Building executable with PyInstaller..."
    echo "This may take several minutes, please be patient..."
    echo ""
    
    # Clean previous build files
    rm -rf build dist
    
    # Build using the spec file
    # Note: We use the same spec file, but PyInstaller handles platform differences automatically
    pyinstaller --clean --noconfirm CtrlSTube.spec
    
    if [ -f "dist/CtrlSTube" ] || [ -d "dist/CtrlSTube.app" ]; then
        echo ""
        echo -e "${GREEN}==========================================${NC}"
        echo -e "${GREEN} BUILD SUCCESSFUL!${NC}"
        echo -e "${GREEN}==========================================${NC}"
        echo ""
        echo "Executable created in 'dist/' directory."
        echo ""
        echo "You can now distribute this file to anyone!"
        echo "No Python installation required to run the executable."
        echo ""
    else
        echo ""
        echo -e "${RED}==========================================${NC}"
        echo -e "${RED} BUILD FAILED!${NC}"
        echo -e "${RED}==========================================${NC}"
        echo ""
        echo "The build may have failed. Check the output above."
        echo "You can still run the app using ./run.sh"
        echo ""
    fi
else
    echo ""
    echo "Skipping executable build."
    echo ""
fi

# ============================================================
# Step 7: Clean Unnecessary Files
# ============================================================
echo ""
echo "Cleaning unnecessary files..."
echo ""

# Remove Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

echo -e "${GREEN}[OK] Cleanup complete${NC}"
echo ""

# ============================================================
# Setup Complete
# ============================================================
echo -e "${GREEN}=====================================================${NC}"
echo -e "${GREEN}          SETUP COMPLETED SUCCESSFULLY!${NC}"
echo -e "${GREEN}=====================================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Make sure FFmpeg is installed (if not already)"
echo "  2. Run the application using: ./run.sh"
echo "  3. Or run the built executable in dist/ (if you built it)"
echo ""
echo "For help and documentation, see README.md"
echo ""
echo "Thank you for using Ctrl+S Tube!"
echo ""
