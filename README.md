# Ctrl+S Tube

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.7%2B-green)

A modern, user-friendly desktop application for downloading high-quality video and audio from YouTube with a clean Qt-based interface. Save YouTube content as easily as hitting `Ctrl+S`!

## 🌐 Two Versions Available
Choose your preferred platform:

### 🖥️ Desktop Application (This README)
- Full-featured Python app with PySide6 GUI
- Complete download functionality with yt-dlp and FFmpeg
- No limitations, works offline after setup
- Best for power users and bulk downloads

### 🌐 Chrome Extension → [See chrome-extension/README.md](chrome-extension/README.md)
- Browser-integrated UI for quick access
- Auto-detects YouTube videos on current tab
- Adds download button directly to YouTube pages
- Requires backend service or desktop app for full downloads
- Perfect for casual, on-the-go downloads

## ✨ Features
- **🎥 High-Quality Video Downloads** - Download videos in multiple resolutions including 4K, 1080p, 720p, and 480p in MKV format
- **🎵 Audio Extraction** - Extract audio-only tracks in high-quality MP3 format (320kbps)
- **🎨 Modern Qt Interface** - Clean, responsive PySide6 GUI with intuitive controls
- **📊 Real-time Progress Tracking** - Visual progress bar with detailed status updates
- **🔄 Video/Audio Toggle** - Seamlessly switch between video and audio download modes
- **📋 Playlist Support** - Download entire YouTube playlists with batch processing
- **⚡ Multithreaded Downloads** - Non-blocking UI with background download tasks
- **🛡️ Robust Error Handling** - Comprehensive validation and user-friendly error messages
- **📝 Logging System** - Detailed logging for debugging and troubleshooting

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

### Downloading Videos
1. **Paste URL** - Copy and paste a YouTube video URL into the input field
2. **Click "Fetch"** - Retrieve video information and available quality options
3. **Select Type** - Choose between Video or Audio download
4. **Choose Quality** - Pick your desired quality from the dropdown menu
   - Video: 4K, 1080p, 720p, 480p (availability depends on source)
   - Audio: 320kbps MP3
5. **Click "Download"** - Select destination folder and start the download
6. **Monitor Progress** - Watch the progress bar for download status

### Downloading Playlists
1. Paste a YouTube playlist URL
2. Click "Fetch" to load playlist information
3. The app will display the number of videos in the playlist
4. Select quality and click "Download" to download all videos sequentially

### Keyboard Shortcuts
- `Ctrl+V` - Paste URL into input field
- `Enter` - Trigger fetch when URL field is focused
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
│   ├── controller.py              # Main orchestrator with DI
│   ├── router.py                  # URL platform identification
│   ├── types.py                   # TypedDict definitions
│   └── exceptions.py              # Custom exception hierarchy
│
├── services/                       # Service layer
│   ├── youtube_metadata_service.py # Fetch video/playlist metadata
│   ├── youtube_download_service.py # Download operations
│   ├── ffmpeg_processor.py        # Media processing (future use)
│   └── youtube_service.py         # Legacy unified service
│
├── ui/                            # User interface
│   └── main_window.py            # Main Qt window implementation
│
├── utils/                         # Utility modules
│   ├── validators.py             # URL and path validation
│   ├── logger.py                 # Logging configuration
│   ├── config.py                 # App configuration & design tokens
│   ├── storage.py                # File system operations
│   └── progress_handler.py       # Progress tracking utilities
│
├── tests/                         # Unit tests
│   ├── test_controller.py        # Controller tests
│   ├── test_validators.py        # Validator tests
│   └── conftest.py               # Pytest configuration
│
├── logs/                          # Application logs
├── main.py                        # Application entry point
├── run.bat                        # Windows launch script
├── setup.bat                      # Windows setup script
├── requirements.txt               # Production dependencies
├── pyproject.toml                # Development tools configuration
├── .env.example                  # Environment variables template
├── .flake8                       # Flake8 configuration
└── .gitignore                    # Git ignore rules
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
- No internet connection - Check your network
- Invalid URL - Ensure it's a valid YouTube URL
- Age-restricted content - Some videos cannot be downloaded
- Region-locked content - Video may not be available in your region
- No write permission - Choose a folder you have access to
- Disk space - Ensure sufficient space for download

### Quality Options Not Showing
**Solution:**
1. Click "Fetch" button after pasting URL
2. Wait for metadata to load
3. Some videos may not have all quality options available
4. Check logs for specific errors

### Slow Download Speed
**Factors:**
- Your internet connection speed
- YouTube server throttling
- High-resolution downloads require more bandwidth
- Consider downloading lower quality if speed is critical

## ❓ FAQ

**Q: What video formats are supported?**
A: Videos are downloaded in MKV format, which preserves high quality. Audio is extracted as MP3.

**Q: Can I download age-restricted videos?**
A: Some age-restricted or region-locked content may not be downloadable due to YouTube restrictions.

**Q: Is this legal?**
A: This tool is for educational purposes. Users are responsible for respecting copyright laws and YouTube's terms of service.

**Q: Can I download from other platforms?**
A: Currently, only YouTube is supported. Future versions may include additional platforms.

**Q: Where are downloads saved?**
A: You choose the save location when clicking download. The application doesn't have a default download folder.

**Q: Why is it called Ctrl+S Tube?**
A: Because downloading YouTube videos should be as easy as saving a file (Ctrl+S)! Plus, it's a fun play on the keyboard shortcut we all know and love.

**Q: Can I pause and resume downloads?**
A: Currently, downloads cannot be paused. This feature may be added in future versions.

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
