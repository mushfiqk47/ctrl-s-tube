# Architecture Documentation

This document provides a comprehensive overview of the Ctrl+S Tube application architecture, design patterns, and data flow.

## 📑 Table of Contents

- [Overview](#overview)
- [Architectural Principles](#architectural-principles)
- [System Architecture](#system-architecture)
- [Layer Details](#layer-details)
- [Data Flow](#data-flow)
- [Threading Model](#threading-model)
- [Error Handling Strategy](#error-handling-strategy)
- [Design Patterns](#design-patterns)
- [Dependencies](#dependencies)

## 🎯 Overview

Ctrl+S Tube is built using a **layered architecture** that separates concerns into distinct layers, promoting:

- **Maintainability** - Each layer has clear responsibilities
- **Testability** - Dependency injection enables unit testing
- **Scalability** - Easy to add new platforms or features
- **Modularity** - Components can be modified independently

## 🏛️ Architectural Principles

### 1. Separation of Concerns

Each layer has a specific responsibility:
- **UI Layer** - User interaction only
- **Core Layer** - Business logic and orchestration
- **Service Layer** - External API integration
- **Utils Layer** - Reusable utilities

### 2. Dependency Injection

Components accept dependencies through constructors, enabling:
- Easy mocking for unit tests
- Flexible configuration
- Loose coupling

```python
class Controller:
    def __init__(
        self,
        metadata_service: Optional[YouTubeMetadataService] = None,
        download_service: Optional[YouTubeDownloadService] = None
    ):
        self.metadata_service = metadata_service or YouTubeMetadataService()
        self.download_service = download_service or YouTubeDownloadService()
```

### 3. Type Safety

TypedDict and type hints ensure:
- Clear data contracts
- IDE autocomplete support
- Early error detection

```python
class VideoMetadata(TypedDict):
    platform: Literal["youtube"]
    type: Literal["video", "playlist"]
    title: str
    duration: Optional[int]
    formats: list[FormatInfo]
```

### 4. Single Responsibility

Each class/module has one clear purpose:
- `Controller` - Orchestrates operations
- `URLRouter` - Platform identification
- `URLValidator` - URL validation
- `YouTubeMetadataService` - Metadata fetching

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              MainWindow (PySide6 / Qt)                   │  │
│  │                                                          │  │
│  │  • URL Input Field                                       │  │
│  │  • Fetch Button → FetchWorker (QThread)                 │  │
│  │  • Video/Audio Toggle                                    │  │
│  │  • Quality Dropdown                                      │  │
│  │  • Download Button → DownloadWorker (QThread)           │  │
│  │  • Progress Bar                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │ Qt Signals/Slots
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                         CORE LAYER                              │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                      Controller                           │ │
│  │                                                           │ │
│  │  • fetch_metadata(url) → VideoMetadata                   │ │
│  │  • download(url, path, quality, callback) → str          │ │
│  │                                                           │ │
│  │  Responsibilities:                                        │ │
│  │  - Input validation via URLValidator                     │ │
│  │  - Platform routing via URLRouter                        │ │
│  │  - Service orchestration                                 │ │
│  │  - Error handling and logging                            │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │    URLRouter      │  │      Types       │  │ Exceptions  │ │
│  │                   │  │                  │  │             │ │
│  │ • identify_       │  │ • VideoMetadata  │  │ • Invalid   │ │
│  │   platform()      │  │ • FormatInfo     │  │   URL       │ │
│  │                   │  │ • ProgressCallback│  │ • Fetch     │ │
│  └───────────────────┘  └──────────────────┘  │ • Download  │ │
│                                                └─────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       SERVICE LAYER                             │
│                                                                 │
│  ┌──────────────────────────────┐  ┌────────────────────────┐  │
│  │ YouTubeMetadataService       │  │ YouTubeDownloadService │  │
│  │                              │  │                        │  │
│  │ • fetch_metadata()           │  │ • download()           │  │
│  │   - Extract video info       │  │   - Quality selection  │  │
│  │   - Parse formats            │  │   - Progress tracking  │  │
│  │   - Handle playlists         │  │   - File naming        │  │
│  └──────────────────────────────┘  └────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────┐                              │
│  │    FFmpegProcessor           │                              │
│  │                              │                              │
│  │ • convert_to_mkv()           │                              │
│  │ • extract_audio()            │                              │
│  │ • merge_streams()            │                              │
│  └──────────────────────────────┘                              │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      UTILITIES LAYER                            │
│                                                                 │
│  ┌─────────────┐ ┌──────────┐ ┌────────┐ ┌─────────────────┐  │
│  │ Validators  │ │  Logger  │ │ Config │ │ ProgressHandler │  │
│  │             │ │          │ │        │ │                 │  │
│  │ • URL       │ │ • File   │ │ • UI   │ │ • Normalize     │  │
│  │ • Path      │ │   logging│ │   Theme│ │   progress      │  │
│  │ • Format    │ │ • Console│ │ • Paths│ │ • Calculate %   │  │
│  └─────────────┘ └──────────┘ └────────┘ └─────────────────┘  │
│                                                                 │
│  ┌─────────────┐                                                │
│  │  Storage    │                                                │
│  │             │                                                │
│  │ • Safe file │                                                │
│  │   operations│                                                │
│  └─────────────┘                                                │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   EXTERNAL DEPENDENCIES                         │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌────────┐  ┌─────────────────┐  │
│  │  yt-dlp  │  │  FFmpeg  │  │ PySide6│  │  python-dotenv  │  │
│  └──────────┘  └──────────┘  └────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 📚 Layer Details

### UI Layer (`ui/`)

**Purpose**: Handle all user interactions and visual presentation.

**Components**:
- `MainWindow` - Main application window
- `FetchWorker` - Background thread for metadata fetching
- `DownloadWorker` - Background thread for downloads

**Responsibilities**:
- Render Qt widgets
- Handle user input events
- Display progress and status
- Manage worker threads
- Show error/success messages

**Key Design Decisions**:
- Uses **QThread** for background operations to prevent UI freezing
- **Signals/Slots** for thread-safe communication
- **No business logic** - delegates to Controller

```python
class FetchWorker(QObject):
    finished = Signal(dict)
    error = Signal(str)
    
    def run(self):
        try:
            metadata = self.controller.fetch_metadata(self.url)
            self.finished.emit(metadata)
        except Exception as e:
            self.error.emit(str(e))
```

### Core Layer (`core/`)

**Purpose**: Implement business logic and orchestration.

#### Controller (`controller.py`)

**Central orchestrator** that coordinates between UI and services.

**Key Methods**:
```python
def fetch_metadata(url: str) -> VideoMetadata:
    """
    1. Validate URL via URLValidator
    2. Identify platform via URLRouter
    3. Delegate to appropriate metadata service
    4. Return standardized metadata
    """

def download(url: str, output_path: str, quality: str, callback) -> str:
    """
    1. Validate URL and path
    2. Identify platform
    3. Delegate to download service with progress callback
    4. Return file path
    """
```

**Dependency Injection**:
```python
def __init__(
    self,
    metadata_service: Optional[YouTubeMetadataService] = None,
    download_service: Optional[YouTubeDownloadService] = None
):
    # Allows injecting mock services for testing
```

#### URLRouter (`router.py`)

**Platform identification** based on URL patterns.

```python
YOUTUBE_DOMAINS = ["youtube.com", "youtu.be", "m.youtube.com"]

def identify_platform(url: str) -> Platform:
    """Returns 'youtube' or raises InvalidURLException"""
```

**Future extensibility**: Easy to add Spotify, Vimeo, etc.

#### Types (`types.py`)

**Type definitions** for data contracts:

```python
class FormatInfo(TypedDict):
    label: str        # "1080p", "720p", etc.
    height: int
    format_id: str
    quality: str
    # ... more fields

class VideoMetadata(TypedDict):
    platform: Literal["youtube"]
    type: Literal["video", "playlist"]
    title: str
    formats: list[FormatInfo]
    count: Optional[int]  # For playlists
```

#### Exceptions (`exceptions.py`)

**Custom exception hierarchy**:

```
MediaDownloaderException (base)
├── InvalidURLException
├── FetchException
├── DownloadException
├── FFmpegException
└── SpotifyAuthException
```

### Service Layer (`services/`)

**Purpose**: Interact with external APIs and tools.

#### YouTubeMetadataService (`youtube_metadata_service.py`)

**Fetches video/playlist information** using yt-dlp.

```python
def fetch_metadata(url: str) -> VideoMetadata:
    """
    1. Use yt-dlp to extract info
    2. Detect if video or playlist
    3. Parse available formats
    4. Normalize quality labels (4K, 1080p, etc.)
    5. Return VideoMetadata TypedDict
    """
```

**Key Features**:
- Playlist support with entry count
- Format filtering and sorting
- Resolution normalization

#### YouTubeDownloadService (`youtube_download_service.py`)

**Downloads videos/audio** with progress tracking.

```python
def download(
    url: str,
    output_path: str,
    quality: Optional[str],
    progress_callback: Optional[ProgressCallback]
) -> str:
    """
    1. Configure yt-dlp options based on quality
    2. Set up progress hooks
    3. Download media
    4. Return final file path
    """
```

**Features**:
- Quality-based format selection
- Audio-only MP3 extraction
- Video MKV downloads
- Real-time progress callbacks
- Playlist batch downloading

#### FFmpegProcessor (`ffmpeg_processor.py`)

**Media processing operations** (currently unused, reserved for future features).

### Utils Layer (`utils/`)

#### Validators (`validators.py`)

**Input validation** with detailed error messages:

```python
class URLValidator:
    @staticmethod
    def validate_youtube_url(url: str) -> str:
        """Validates and returns cleaned URL"""

class PathValidator:
    @staticmethod
    def validate_output_path(path: str) -> Path:
        """Validates destination path"""
```

#### Logger (`logger.py`)

**Centralized logging** with file and console outputs:

```python
def get_logger(name: str) -> logging.Logger:
    """
    Returns configured logger:
    - File: logs/app_YYYYMMDD_HHMMSS.log
    - Console: INFO level
    - File: DEBUG level
    """
```

#### Config (`config.py`)

**Application configuration** and design tokens:

```python
class Config:
    WINDOW_WIDTH = 480
    WINDOW_HEIGHT = 600
    WINDOW_TITLE = "Ctrl+S Tube"

class Colors:
    BACKGROUND = "#0F0F0F"
    TEXT = "#FFFFFF"
    ACCENT = "#FF0000"  # YouTube red

class Fonts:
    FAMILY = "Poppins"
    SIZE_LARGE = 24
```

#### ProgressHandler (`progress_handler.py`)

**Progress calculation helpers**:

```python
def normalize_progress(current: int, total: int) -> float:
    """Converts bytes to percentage"""
```

## 🔄 Data Flow

### Fetch Metadata Flow

```
User enters URL → Click Fetch
    │
    ▼
MainWindow._on_fetch()
    │
    ├─ Create FetchWorker(controller, url)
    ├─ Start QThread
    │
    ▼
FetchWorker.run()
    │
    ▼
Controller.fetch_metadata(url)
    │
    ├─ URLValidator.validate_youtube_url()
    ├─ URLRouter.identify_platform()
    │
    ▼
YouTubeMetadataService.fetch_metadata()
    │
    ├─ yt-dlp extracts info
    ├─ Parse formats
    ├─ Build VideoMetadata
    │
    ▼
Return metadata via Signal
    │
    ▼
MainWindow._on_fetch_success(metadata)
    │
    ├─ Display video title
    ├─ Populate quality dropdown
    └─ Enable download button
```

### Download Flow

```
User clicks Download → Select folder
    │
    ▼
MainWindow._on_download()
    │
    ├─ Create DownloadWorker(controller, url, path, quality)
    ├─ Start QThread
    │
    ▼
DownloadWorker.run()
    │
    ├─ Define progress_callback(percent, status)
    │   └─ Emit progress signal
    │
    ▼
Controller.download(url, path, quality, callback)
    │
    ├─ URLValidator.validate_youtube_url()
    ├─ PathValidator.validate_output_path()
    ├─ URLRouter.identify_platform()
    │
    ▼
YouTubeDownloadService.download(url, path, quality, callback)
    │
    ├─ Configure yt-dlp options
    ├─ Set up progress hooks
    │   └─ Call progress_callback during download
    ├─ Execute download
    │
    ▼
Return file path via Signal
    │
    ▼
MainWindow._on_download_success(file_path)
    │
    ├─ Show success message
    ├─ Reset progress bar
    └─ Enable buttons
```

## 🧵 Threading Model

### Why Threading?

**Problem**: yt-dlp operations are **blocking** and can take minutes.

**Solution**: Use **QThread** to run operations in background.

### Implementation

```python
# UI Thread (Main)
class MainWindow(QMainWindow):
    def _on_fetch(self):
        # Create worker
        self.fetch_worker = FetchWorker(self.controller, url)
        self.fetch_thread = QThread()
        
        # Move worker to thread
        self.fetch_worker.moveToThread(self.fetch_thread)
        
        # Connect signals
        self.fetch_thread.started.connect(self.fetch_worker.run)
        self.fetch_worker.finished.connect(self._on_fetch_success)
        self.fetch_worker.error.connect(self._on_fetch_error)
        
        # Start thread
        self.fetch_thread.start()

# Worker Thread
class FetchWorker(QObject):
    finished = Signal(dict)  # Thread-safe communication
    error = Signal(str)
    
    def run(self):
        # Runs in background thread
        result = self.controller.fetch_metadata(self.url)
        self.finished.emit(result)  # Send back to UI thread
```

### Thread Safety

- **Signals/Slots** ensure thread-safe communication
- **No shared state** between threads
- **Progress callbacks** use signals to update UI

## 🛡️ Error Handling Strategy

### Layered Error Handling

Each layer catches and re-raises with context:

```python
# Service Layer
try:
    ydl.extract_info(url)
except yt_dlp.utils.DownloadError as e:
    raise FetchException(f"yt-dlp error: {str(e)}")

# Core Layer
try:
    self.metadata_service.fetch_metadata(url)
except FetchException:
    logger.error("Failed to fetch")
    raise  # Propagate to UI

# UI Layer
try:
    metadata = controller.fetch_metadata(url)
except FetchException as e:
    QMessageBox.critical(self, "Error", str(e))
```

### Exception Hierarchy

```python
MediaDownloaderException         # Base - never raised directly
├── InvalidURLException           # 400-style errors
├── FetchException               # Metadata fetch failures
├── DownloadException            # Download failures
└── FFmpegException              # Processing failures
```

### Validation Before Execution

```python
# Validate early to fail fast
def download(url, path, quality):
    url = URLValidator.validate_youtube_url(url)      # Raises InvalidURLException
    path = PathValidator.validate_output_path(path)   # Raises ValueError
    # ... proceed with download
```

## 🎨 Design Patterns

### 1. Dependency Injection

**Used in**: Controller, Services

**Benefits**:
- Testability (mock dependencies)
- Flexibility (swap implementations)
- Loose coupling

### 2. Service Layer Pattern

**Used in**: All services

**Benefits**:
- Encapsulates external API logic
- Easy to add new platforms
- Centralized error handling

### 3. Repository Pattern (partial)

**Used in**: Storage utilities

**Benefits**:
- Abstracts file system operations
- Consistent error handling

### 4. Strategy Pattern (implicit)

**Used in**: Download quality selection

**Benefits**:
- Different download strategies per quality
- Easy to add new quality options

### 5. Observer Pattern

**Used in**: Qt Signals/Slots, Progress callbacks

**Benefits**:
- Decoupled components
- Event-driven architecture

## 📦 Dependencies

### Production Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| yt-dlp | ≥2023.0.0 | YouTube downloading |
| PySide6 | ≥6.7.0 | Qt GUI framework |
| python-dotenv | ≥1.0.0 | Environment config |
| mutagen | ≥1.47.0 | Audio metadata |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | ≥7.4.0 | Testing framework |
| pytest-cov | ≥4.1.0 | Coverage reporting |
| black | ≥23.0.0 | Code formatting |
| flake8 | ≥6.1.0 | Linting |
| mypy | ≥1.5.0 | Type checking |

### External Tools

- **FFmpeg** - Required for media processing
- **Python 3.8+** - Runtime environment

## 🔮 Future Architecture Considerations

### Planned Enhancements

1. **Plugin System** - Allow third-party platform integrations
2. **Database Layer** - Track download history
3. **Configuration Service** - User preferences persistence
4. **Async/Await** - Replace threading with asyncio
5. **REST API** - Headless mode for automation

### Scalability

The current architecture supports:
- Adding new platforms (Spotify, Vimeo, etc.)
- Multiple UI implementations (CLI, Web)
- Advanced features (scheduling, batch operations)

---

**Last Updated**: 2025-11-21  
**Version**: 7.0
