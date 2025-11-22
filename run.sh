#!/bin/bash

# Wrapper script to run Ctrl+S Tube on macOS/Linux

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the application
python main.py
