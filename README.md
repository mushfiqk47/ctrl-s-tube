# Ctrl+S Tube
# Screenshort ![Ctrl+S Tube Application](docs/images/screenshot.png)

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.7%2B-green)

A modern, user-friendly desktop application for downloading high-quality video and audio from YouTube with a clean Qt-based interface. Save YouTube content as easily as hitting `Ctrl+S`!



### 🖥️ Desktop Application (This README)
- Full-featured Python app with PySide6 GUI
- Complete download functionality with yt-dlp and FFmpeg
- No limitations, works offline after setup
- Best for power users and bulk downloads

### 🎯 Core Functionality
- **🎥 High-Quality Video Downloads** - Download videos in multiple resolutions (4K, 1440p, 1080p, 720p, 480p, 360p)
- **🎵 Audio Extraction** - Extract audio-only tracks in high-quality MP3 format (320kbps)
- **📦 Format Selection** - Choose between MP4 (universal compatibility) or MKV (high quality) formats
- **📋 Batch Downloads** - Download multiple videos simultaneously with URL list support
- **⚡ Smart Quality Fallback** - Automatically selects best available quality if preferred option isn't available

### 🎨 User Interface
- **📑 Dual-Tab Interface** 
  - **Single Download Tab** - Download individual videos with auto-fetch on URL paste
  - **Multiple Download Tab** - Batch process multiple URLs with real-time status tracking
- **🖥️ Modern Qt Design** - Clean, dark-mode PySide6 GUI with YouTube-inspired red accents
- **📊 Real-time Progress** - Visual progress bars with download speed and file location display
- **🔄 Type Toggle** - Seamlessly switch between Video and Audio download modes per tab

### ⚙️ Technical Features
- **🧵 Multithreaded Processing** - Non-blocking UI with background worker threads for fetch and download operations
- **🛡️ Robust Error Handling** - Comprehensive validation with user-friendly error messages and detailed logging
- **� URL Parsing** - Intelligent YouTube URL extraction and validation from pasted text
- **📝 Comprehensive Logging** - Detailed logging system for debugging and troubleshooting
- **🎯 Batch Processor** - Thread-safe progress tracking for concurrent multi-video downloads

## 📋 Prerequisites
Before running the application, ensure you have the following installed:

- **Python 3.8 or higher**
  - Download from [python.org](https://www.python.org)
  - Verify installation: `python --version`
- **FFmpeg** - Required for media processing
  - **Windows:**
    - Download from [ffmpeg.org](https://ffmpeg.org)
    - Extract and add to system PATH
    - Or use Chocolatey: `choco install ffmpeg`
  - **macOS:** `brew install ffmpeg`
  - **Linux:** `sudo apt install ffmpeg` (Debian/Ubuntu) or `sudo yum install ffmpeg` (RHEL/CentOS)
  - Verify installation: `ffmpeg -version`

## 🚀 Quick Start

### Automated Setup (Windows)
1. Clone or download this repository
2. Double-click `setup.bat` to automatically:
   - Create a virtual environment
   - Install all dependencies
   - Verify FFmpeg installation
3. Double-click `run.bat` to launch the application

### Manual Installation
```bash
# Navigate to project directory
cd "path/to/ctrl-s-tube"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 📖 Usage Guide

### Single Video Download
1. **Navigate to Single Download Tab** - Select the "Single Download" tab in the interface
2. **Paste URL** - Copy and paste a YouTube video URL into the input field
   - Video metadata automatically fetches when you paste the URL
3. **Select Download Type** - Choose between:
   - 🎥 **Video** - Download video with audio
   - 🎵 **Audio** - Extract audio only (MP3, 320kbps)
4. **Choose Quality** - Pick your desired quality from the dropdown:
   - Video: 4K (2160p), 1440p, 1080p, 720p, 480p, 360p (availability depends on source)
   - Audio: 320kbps MP3
5. **Select Format** (Video only) - Choose video container:
   - **MP4** - Universal compatibility, widely supported
   - **MKV** - High quality, better codec support
6. **Click "Download"** - Select destination folder and start the download
7. **Monitor Progress** - Watch the progress bar showing:
   - Download percentage
   - Download speed (MB/s)
   - File save location

### Multiple Video Downloads (Batch Processing)
1. **Navigate to Multiple Downloads Tab** - Select the "Multiple Downloads" tab
2. **Paste URLs** - Paste multiple YouTube URLs into the text area
   - One URL per line, or paste a list of URLs
   - URLs are automatically extracted and validated
3. **Click "Validate URLs"** - System will:
   - Extract all valid YouTube URLs
   - Remove duplicates
   - Display count of valid/invalid URLs
4. **Select Download Type** - Choose Video or Audio for all items
5. **Choose Quality** - Select preferred quality for batch
   - If a video doesn't have the selected quality, best available quality is used automatically
6. **Select Format** (Video only) - Choose MP4 or MKV for all videos
7. **Click "Download All"** - Choose destination folder and start batch download
8. **Track Progress** - Monitor each video's status:
   - Real-time progress per video
   - Overall batch completion percentage
   - Success/failure status for each item

### Keyboard Shortcuts
- `Ctrl+V` - Paste URL into input field
- `Enter` - Auto-fetches metadata in Single Download tab
- `Ctrl+Q` - Quit application

## 🏗️ Architecture
The application follows a clean, layered architecture for maintainability and testability:

```text
┌─────────────────────────────────────────┐
│          UI Layer (PySide6)             │
│     main_window.py - Qt Widgets         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Core Layer (Business Logic)      │
│  controller.py - Orchestration           │
│  router.py - URL Routing                 │
│  types.py - Type Definitions             │
│  exceptions.py - Custom Exceptions       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Service Layer                    │
│  youtube_metadata_service.py             │
│  youtube_download_service.py             │
│  ffmpeg_processor.py                     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Utilities Layer                  │
│  validators.py - Input Validation        │
│  logger.py - Logging Framework           │
│  config.py - Configuration & Constants   │
│  storage.py - File Operations            │
│  progress_handler.py - Progress Tracking │
└─────────────────────────────────────────┘
```
For detailed architecture documentation, see `ARCHITECTURE.md`.

## 📂 Project Structure
```text
ctrl-s-tube/
├── core/                           # Core business logic
│   ├── controller.py               # Main orchestrator with DI
│   ├── router.py                   # URL platform identification
│   ├── types.py                    # TypedDict definitions
│   └── exceptions.py               # Custom exception hierarchy
│
├── services/                       # Service layer
│   ├── youtube_metadata_service.py # Fetch video/playlist metadata
│   ├── youtube_download_service.py # Download operations
│   ├── ffmpeg_processor.py         # Media processing
│   └── youtube_service.py          # Legacy unified service
│
├── ui/                             # User interface
│   ├── main_window.py              # Main Qt window with dual-tab interface
│   └── asset/                      # UI assets (icons)
│
├── app_utils/                      # Utility modules
│   ├── validators.py               # URL and path validation
│   ├── logger.py                   # Logging configuration
│   ├── config.py                   # App configuration & design tokens
│   ├── storage.py                  # File system operations
│   ├── progress_handler.py         # Progress tracking utilities
│   └── batch_processor.py          # Batch download processing
│
├── tests/                          # Unit tests
│   ├── test_controller.py          # Controller tests
│   ├── test_validators.py          # Validator tests
│   └── conftest.py                 # Pytest configuration
│
├── docs/                           # Documentation
│   ├── API.md                      # API documentation
│   └── ARCHITECTURE.md             # Architecture details
│
├── logs/                           # Application logs
├── build/                          # Build artifacts
├── dist/                           # Distribution files
│
├── main.py                         # Application entry point
├── CtrlSTube.spec                  # PyInstaller spec file
│
├── run.bat                         # Windows launch script
├── run.sh                          # Linux/Mac launch script
├── setup.bat                       # Windows setup script
├── setup.sh                        # Linux/Mac setup script
├── build_exe.bat                   # Windows executable builder
│
├── requirements.txt                # Production dependencies
├── pyproject.toml                  # Development tools configuration
├── .flake8                         # Flake8 configuration
├── .gitignore                      # Git ignore rules
│
├── icon.ico                        # Application icon (Windows)
├── icon.png                        # Application icon (cross-platform)
│
├── LICENSE                         # MIT License
├── README.md                       # This file
├── ARCHITECTURE.md                 # Architecture documentation
├── CHANGELOG.md                    # Version history
└── CONTRIBUTING.md                 # Contribution guidelines
```

## 🛠️ Technology Stack
| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.8+ | Core application language |
| GUI Framework | PySide6 (Qt 6.7+) | Modern cross-platform UI |
| Downloader | yt-dlp 2023.0+ | YouTube video/audio extraction |
| Media Processing | FFmpeg | Video/audio conversion and processing |
| Configuration | python-dotenv 1.0+ | Environment variable management |
| Metadata | mutagen 1.47+ | Audio file tagging |
| Testing | pytest 7.4+ | Unit testing framework |
| Code Formatting | Black 23.0+ | Code style enforcement |
| Linting | Flake8 6.1+ | Code quality checks |
| Type Checking | MyPy 1.5+ | Static type analysis |

## 📦 Building Standalone Executable

### Windows Executable (.exe)
```bash
# Run the automated build script
build_exe.bat

# The executable will be created in the dist/ folder
# Output: dist/CtrlSTube.exe (single file, includes all dependencies)
```

The build script uses PyInstaller to create a standalone executable that includes:
- All Python dependencies bundled
- Application icon (icon.ico)
- One-file executable for easy distribution
- Windows-optimized with proper taskbar icon support

**Note:** The first time you run the executable, Windows SmartScreen may show a warning because the file is unsigned. Click "More info" → "Run anyway" for testing purposes.

### Cross-Platform Support
- **Windows**: Use `build_exe.bat` to create `.exe`
- **macOS/Linux**: Use `setup.sh` and `run.sh` for native Python execution
- Future builds may include `.dmg` (macOS) and `.AppImage` (Linux) support

## 🧪 Development

### Setting Up Development Environment
```bash
# Clone repository
git clone <repository-url>
cd "Yt downloader_v7.0"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install all dependencies (including dev)
pip install -r requirements.txt

# Run tests
pytest

# Run type checking
mypy .

# Format code
black .

# Lint code
flake8
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_controller.py

# Run with verbose output
pytest -v
```

### Code Quality
The project uses several tools to maintain code quality:
- **Black** - Automatic code formatting (line length: 100)
- **Flake8** - Style guide enforcement
- **MyPy** - Static type checking
- **Pytest** - Unit testing with coverage

Configuration files:
- `pyproject.toml` - Black and MyPy settings
- `.flake8` - Flake8 rules

## 🐛 Troubleshooting

### FFmpeg Not Found
**Error:** FFmpeg not found in system PATH

**Solution:**
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org)
2. Extract the archive
3. Add the `bin` folder to your system PATH
4. Restart terminal and application
5. Verify: `ffmpeg -version`

### Application Won't Start
**Symptoms:** Window doesn't appear or immediate crash

**Solutions:**
1. Verify Python version: `python --version` (must be 3.8+)
2. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
3. Check error logs in `logs/` directory
4. Run from terminal to see error messages: `python main.py`

### Download Fails
**Common Causes:**
- **No internet connection** - Check your network
- **Invalid URL** - Ensure it's a valid YouTube URL
- **Age-restricted content** - Some videos cannot be downloaded
- **Region-locked content** - Video may not be available in your region
- **No write permission** - Choose a folder you have access to
- **Disk space** - Ensure sufficient space for download

### Auto-Fetch Not Working (Single Download Tab)
**Solution:**
1. Ensure you're pasting a complete YouTube URL
2. Check internet connection
3. Look for error messages in the status area
4. Check logs for specific errors

### Batch Download Issues
**Problem:** Some videos fail in batch download

**Solution:**
- This is normal - some videos may be unavailable or restricted
- Check the status of each video in the list
- Failed videos will show error messages
- Successfully downloaded videos will show completion status

### Slow Download Speed
**Factors:**
- Your internet connection speed
- YouTube server throttling
- High-resolution downloads require more bandwidth
- Consider downloading lower quality if speed is critical
- Batch downloads process sequentially, not simultaneously

## ❓ FAQ

**Q: What video formats are supported?**
A: Videos can be downloaded in MP4 (universal compatibility) or MKV (high quality) formats. Audio is extracted as MP3 (320kbps).

**Q: Can I download multiple videos at once?**
A: Yes! Use the "Multiple Downloads" tab to paste multiple URLs and download them in batch. The system will process them sequentially with real-time progress tracking.

**Q: What happens if my selected quality isn't available?**
A: The download service automatically falls back to the best available quality for that video. You won't need to manually adjust settings.

**Q: Can I download age-restricted videos?**
A: Some age-restricted or region-locked content may not be downloadable due to YouTube restrictions.

**Q: Is this legal?**
A: This tool is for educational purposes. Users are responsible for respecting copyright laws and YouTube's terms of service.

**Q: Can I download from other platforms?**
A: Currently, only YouTube is supported. Future versions may include additional platforms.

**Q: Where are downloads saved?**
A: You choose the save location when clicking download. The application doesn't have a default download folder for flexibility and user control.

**Q: Why is it called Ctrl+S Tube?**
A: Because downloading YouTube videos should be as easy as saving a file (Ctrl+S)! Plus, it's a fun play on the keyboard shortcut we all know and love.

**Q: Can I pause and resume downloads?**
A: Currently, downloads cannot be paused. This feature may be added in future versions.

**Q: How do I build a standalone executable?**
A: Use the included `build_exe.bat` script. It uses PyInstaller to create a Windows executable with all dependencies bundled.

## 🤝 Contributing
We welcome contributions! Please see `CONTRIBUTING.md` for guidelines on:
- Code style and standards
- Submitting bug reports
- Proposing new features
- Creating pull requests
- Running tests

## 📝 Changelog
See `CHANGELOG.md` for version history and release notes.

## 📄 License
This project is licensed under the MIT License - see the `LICENSE` file for details.

> **Important:** This software is provided for educational purposes. Users must comply with:
> - YouTube's Terms of Service
> - Copyright laws in their jurisdiction
> - Fair use guidelines
> - Content creators' rights

## 🙏 Acknowledgments
- **yt-dlp** - Powerful YouTube downloader library
- **PySide6** - Qt for Python framework
- **FFmpeg** - Multimedia framework for processing
- **Qt Project** - Cross-platform application framework

## 📧 Support
- **Issues:** [GitHub Issues](https://github.com/mushfiqk47/ctrl-s-tube/issues)
- **Discussions:** [GitHub Discussions](https://github.com/mushfiqk47/ctrl-s-tube/discussions)
- **Documentation:** `docs/`

---
*Note: This is an educational project. Please use responsibly and respect content creators' rights.*
