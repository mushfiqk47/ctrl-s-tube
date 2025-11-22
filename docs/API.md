# API Documentation

Complete API reference for the Ctrl+S Tube application.

## 📑 Table of Contents

- [Core API](#core-api)
  - [Controller](#controller)
  - [URLRouter](#urlrouter)
- [Services API](#services-api)
  - [YouTubeMetadataService](#youtubemetadataservice)
  - [YouTubeDownloadService](#youtubedownloadservice)
  - [FFmpegProcessor](#ffmpegprocessor)
- [Utilities API](#utilities-api)
  - [Validators](#validators)
  - [Logger](#logger)
  - [Config](#config)
  - [Storage](#storage)
  - [ProgressHandler](#progresshandler)
- [Type Definitions](#type-definitions)
- [Exceptions](#exceptions)

---

## Core API

### Controller

**Location**: `core/controller.py`

The main orchestrator that coordinates between UI and services.

#### Class: `Controller`

```python
class Controller:
    def __init__(
        self,
        metadata_service: Optional[YouTubeMetadataService] = None,
        download_service: Optional[YouTubeDownloadService] = None
    )
```

**Orchestrates fetch and download operations with dependency injection.**

##### Parameters

- `metadata_service` (Optional[YouTubeMetadataService]): Custom metadata service instance for dependency injection/testing. Defaults to `YouTubeMetadataService()`.
- `download_service` (Optional[YouTubeDownloadService]): Custom download service instance for dependency injection/testing. Defaults to `YouTubeDownloadService()`.

##### Methods

#### `fetch_metadata(url: str) -> VideoMetadata`

Fetch metadata for a given YouTube URL.

**Parameters:**
- `url` (str): YouTube video or playlist URL

**Returns:**
- `VideoMetadata`: Dictionary containing:
  - `platform`: "youtube"
  - `type`: "video" or "playlist"
  - `title`: Video/playlist title
  - `duration`: Video duration in seconds (videos only)
  - `thumbnail`: Thumbnail URL
  - `formats`: List of available formats
  - `count`: Number of videos (playlists only)

**Raises:**
- `InvalidURLException`: If URL is invalid or not a YouTube URL
- `FetchException`: If fetching metadata fails

**Example:**

```python
from core.controller import Controller

controller = Controller()

# Fetch video metadata
metadata = controller.fetch_metadata("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
print(metadata["title"])  # Video title
print(metadata["formats"])  # Available qualities

# Fetch playlist metadata
playlist = controller.fetch_metadata("https://www.youtube.com/playlist?list=...")
print(playlist["count"])  # Number of videos
```

#### `download(url: str, output_path: str, quality: Optional[str] = None, progress_callback: Optional[ProgressCallback] = None) -> str`

Download media from YouTube URL.

**Parameters:**
- `url` (str): YouTube video or playlist URL
- `output_path` (str): Directory path to save downloaded files
- `quality` (Optional[str]): Quality selection ("4K", "1080p", "720p", "480p", "Audio Only"). Defaults to best available.
- `progress_callback` (Optional[ProgressCallback]): Callback function for progress updates. Signature: `(percent: float, status: str) -> None`

**Returns:**
- `str`: Path to downloaded file (for videos) or directory (for playlists)

**Raises:**
- `InvalidURLException`: If URL is invalid
- `DownloadException`: If download fails
- `ValueError`: If output path is invalid

**Example:**

```python
def on_progress(percent: float, status: str):
    print(f"Progress: {percent:.1f}% - {status}")

# Download video
file_path = controller.download(
    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    output_path="C:/Downloads",
    quality="1080p",
    progress_callback=on_progress
)
print(f"Downloaded to: {file_path}")

# Download audio only
audio_path = controller.download(
    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    output_path="C:/Downloads",
    quality="Audio Only"
)
```

---

### URLRouter

**Location**: `core/router.py`

Routes URLs to appropriate service based on platform identification.

#### Class: `URLRouter`

```python
class URLRouter:
    YOUTUBE_DOMAINS = ["youtube.com", "youtu.be", "m.youtube.com"]
```

##### Class Methods

#### `identify_platform(url: str) -> Platform`

Identify which platform a URL belongs to.

**Parameters:**
- `url` (str): The URL to check

**Returns:**
- `Platform`: "youtube" (currently only YouTube is supported)

**Raises:**
- `InvalidURLException`: If URL doesn't match any supported platform

**Example:**

```python
from core.router import URLRouter

platform = URLRouter.identify_platform("https://www.youtube.com/watch?v=...")
# Returns: "youtube"

platform = URLRouter.identify_platform("https://vimeo.com/...")
# Raises: InvalidURLException
```

---

## Services API

### YouTubeMetadataService

**Location**: `services/youtube_metadata_service.py`

Fetches video and playlist metadata from YouTube.

#### Class: `YouTubeMetadataService`

```python
class YouTubeMetadataService:
    def __init__(self)
```

##### Methods

#### `fetch_metadata(url: str) -> VideoMetadata`

Fetch comprehensive metadata for a YouTube video or playlist.

**Parameters:**
- `url` (str): YouTube URL (validated)

**Returns:**
- `VideoMetadata`: Complete metadata including formats

**Raises:**
- `FetchException`: If yt-dlp fails to extract info

**Example:**

```python
from services.youtube_metadata_service import YouTubeMetadataService

service = YouTubeMetadataService()
metadata = service.fetch_metadata("https://www.youtube.com/watch?v=...")

print(f"Title: {metadata['title']}")
print(f"Type: {metadata['type']}")
for format in metadata['formats']:
    print(f"Quality: {format['quality']} - {format['resolution']}")
```

---

### YouTubeDownloadService

**Location**: `services/youtube_download_service.py`

Downloads videos and audio from YouTube.

#### Class: `YouTubeDownloadService`

```python
class YouTubeDownloadService:
    def __init__(self)
```

##### Methods

#### `download(url: str, output_path: str, quality: Optional[str] = None, progress_callback: Optional[ProgressCallback] = None) -> str`

Download video or audio from YouTube.

**Parameters:**
- `url` (str): YouTube URL
- `output_path` (str): Destination directory
- `quality` (Optional[str]): Quality selection
- `progress_callback` (Optional[ProgressCallback]): Progress updates

**Returns:**
- `str`: Path to downloaded file(s)

**Raises:**
- `DownloadException`: If download fails

**Quality Options:**
- `"Audio Only"` - MP3 320kbps audio extraction
- `"4K"`, `"1080p"`, `"720p"`, `"480p"` - Video qualities in MKV format
- `None` - Best available quality

**Example:**

```python
from services.youtube_download_service import YouTubeDownloadService

service = YouTubeDownloadService()

# Download 1080p video
file_path = service.download(
    url="https://www.youtube.com/watch?v=...",
    output_path="C:/Downloads",
    quality="1080p",
    progress_callback=lambda p, s: print(f"{p:.1f}%")
)

# Download audio
audio_path = service.download(
    url="https://www.youtube.com/watch?v=...",
    output_path="C:/Downloads",
    quality="Audio Only"
)
```

---

### FFmpegProcessor

**Location**: `services/ffmpeg_processor.py`

Media processing operations using FFmpeg (currently unused, reserved for future features).

#### Class: `FFmpegProcessor`

```python
class FFmpegProcessor:
    @staticmethod
    def check_ffmpeg() -> bool
```

##### Methods

#### `check_ffmpeg() -> bool`

Check if FFmpeg is installed and accessible.

**Returns:**
- `bool`: True if FFmpeg is available, False otherwise

**Example:**

```python
from services.ffmpeg_processor import FFmpegProcessor

if FFmpegProcessor.check_ffmpeg():
    print("FFmpeg is installed")
else:
    print("FFmpeg not found")
```

---

## Utilities API

### Validators

**Location**: `utils/validators.py`

Input validation utilities for URLs and paths.

#### Class: `URLValidator`

```python
class URLValidator:
    @staticmethod
    def validate_youtube_url(url: str) -> str
    
    @staticmethod
    def is_youtube_playlist(url: str) -> bool
```

##### Methods

#### `validate_youtube_url(url: str) -> str`

Validate and clean a YouTube URL.

**Parameters:**
- `url` (str): URL to validate

**Returns:**
- `str`: Cleaned and validated URL

**Raises:**
- `InvalidURLException`: If URL is invalid or not YouTube

**Example:**

```python
from utils.validators import URLValidator

# Valid URL
url = URLValidator.validate_youtube_url("https://www.youtube.com/watch?v=...")
# Returns: cleaned URL

# Invalid URL
url = URLValidator.validate_youtube_url("not a url")
# Raises: InvalidURLException
```

#### `is_youtube_playlist(url: str) -> bool`

Check if URL is a YouTube playlist.

**Parameters:**
- `url` (str): URL to check

**Returns:**
- `bool`: True if playlist, False if single video

#### Class: `PathValidator`

```python
class PathValidator:
    @staticmethod
    def validate_output_path(path: str) -> Path
    
    @staticmethod
    def sanitize_filename(filename: str) -> str
```

##### Methods

#### `validate_output_path(path: str) -> Path`

Validate destination path for downloads.

**Parameters:**
- `path` (str): Path to validate

**Returns:**
- `Path`: Validated pathlib.Path object

**Raises:**
- `ValueError`: If path is invalid or not writable

#### `sanitize_filename(filename: str) -> str`

Remove invalid characters from filenames.

**Parameters:**
- `filename` (str): Original filename

**Returns:**
- `str`: Sanitized filename safe for file system

**Example:**

```python
from utils.validators import PathValidator

# Validate path
path = PathValidator.validate_output_path("C:/Downloads")
# Returns: Path object

# Sanitize filename
safe_name = PathValidator.sanitize_filename("Video: Title | 2024")
# Returns: "Video Title 2024"
```

---

### Logger

**Location**: `utils/logger.py`

Centralized logging configuration.

#### Function: `get_logger(name: str) -> logging.Logger`

Get a configured logger instance.

**Parameters:**
- `name` (str): Logger name (typically `__name__`)

**Returns:**
- `logging.Logger`: Configured logger with file and console handlers

**Configuration:**
- **File Logging**: `logs/app_YYYYMMDD_HHMMSS.log` (DEBUG level)
- **Console Logging**: stdout (INFO level)
- **Format**: `[YYYY-MM-DD HH:MM:SS] [LEVEL] [name] message`

**Example:**

```python
from utils.logger import get_logger

logger = get_logger(__name__)

logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")
```

---

### Config

**Location**: `utils/config.py`

Application configuration and design constants.

#### Class: `Config`

```python
class Config:
    WINDOW_WIDTH = 480
    WINDOW_HEIGHT = 600
    WINDOW_TITLE = "Ctrl+S Tube"
    VERSION = "7.0.0"
```

#### Class: `Colors`

```python
class Colors:
    # Background colors
    BACKGROUND = "#0F0F0F"
    BACKGROUND_LIGHTER = "#1A1A1A"
    
    # Text colors
    TEXT = "#FFFFFF"
    TEXT_SECONDARY = "#AAAAAA"
    TEXT_DISABLED = "#666666"
    
    # Accent colors
    ACCENT = "#FF0000"  # YouTube red
    ACCENT_HOVER = "#CC0000"
    
    # Border colors
    BORDER = "#333333"
    BORDER_FOCUS = "#FF0000"
```

#### Class: `Fonts`

```python
class Fonts:
    FAMILY = "Poppins"
    SIZE_SMALL = 12
    SIZE_MEDIUM = 14
    SIZE_LARGE = 24
    WEIGHT_NORMAL = 400
    WEIGHT_SEMIBOLD = 600
    WEIGHT_BOLD = 700
```

#### Class: `Spacing`

```python
class Spacing:
    SMALL = 8
    MEDIUM = 16
    LARGE = 24
    XLARGE = 32
```

**Example:**

```python
from utils.config import Colors, Fonts, Config

# Use in UI
button.setStyleSheet(f"background-color: {Colors.ACCENT};")
label.setFont(QFont(Fonts.FAMILY, Fonts.SIZE_LARGE))
window.resize(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
```

---

### Storage

**Location**: `utils/storage.py`

File system operations with safety checks.

#### Class: `Storage`

```python
class Storage:
    @staticmethod
    def ensure_directory(path: Path) -> None
    
    @staticmethod
    def safe_write(path: Path, content: bytes) -> None
```

---

### ProgressHandler

**Location**: `utils/progress_handler.py`

Progress calculation utilities.

#### Class: `ProgressHandler`

```python
class ProgressHandler:
    @staticmethod
    def normalize_progress(downloaded: int, total: int) -> float
    
    @staticmethod
    def format_bytes(bytes: int) -> str
```

##### Methods

#### `normalize_progress(downloaded: int, total: int) -> float`

Convert bytes to percentage.

**Parameters:**
- `downloaded` (int): Bytes downloaded
- `total` (int): Total bytes

**Returns:**
- `float`: Percentage (0.0 - 100.0)

#### `format_bytes(bytes: int) -> str`

Format bytes as human-readable string.

**Parameters:**
- `bytes` (int): Number of bytes

**Returns:**
- `str`: Formatted string (e.g., "1.5 MB", "3.2 GB")

**Example:**

```python
from utils.progress_handler import ProgressHandler

percent = ProgressHandler.normalize_progress(50000000, 100000000)
# Returns: 50.0

size = ProgressHandler.format_bytes(1536000)
# Returns: "1.5 MB"
```

---

## Type Definitions

**Location**: `core/types.py`

### FormatInfo

```python
class FormatInfo(TypedDict):
    label: str          # "1080p", "720p", etc.
    height: int         # Vertical resolution
    width: int          # Horizontal resolution
    fps: int            # Frames per second
    vcodec: str         # Video codec
    acodec: str         # Audio codec
    ext: str            # File extension
    tbr: float          # Total bitrate
    format_id: str      # yt-dlp format ID
    resolution: str     # "1920x1080"
    quality: str        # "1080p"
```

### VideoMetadata

```python
class VideoMetadata(TypedDict):
    platform: Literal["youtube"]
    type: Literal["video", "playlist"]
    title: str
    duration: Optional[int]      # Seconds, for videos only
    thumbnail: str               # URL
    formats: list[FormatInfo]
    count: Optional[int]         # For playlists
```

### DownloadProgress

```python
class DownloadProgress(TypedDict):
    percent: float                # 0.0 - 100.0
    status: str                   # "downloading", "processing", etc.
    downloaded_bytes: Optional[int]
    total_bytes: Optional[int]
    playlist_index: Optional[int] # Current video in playlist
    n_entries: Optional[int]      # Total videos in playlist
```

### Type Aliases

```python
ProgressCallback = Callable[[float, str], None]
Platform = Literal["youtube"]
DownloadType = Literal["video", "audio"]
```

---

## Exceptions

**Location**: `core/exceptions.py`

### Exception Hierarchy

```
MediaDownloaderException (base)
├── InvalidURLException
├── FetchException
├── DownloadException
├── FFmpegException
└── SpotifyAuthException
```

### MediaDownloaderException

Base exception for all application errors.

```python
class MediaDownloaderException(Exception):
    """Base exception for all Media Downloader errors."""
```

### InvalidURLException

Raised when an invalid URL is provided.

```python
class InvalidURLException(MediaDownloaderException):
    """Raised when an invalid URL is provided."""
```

**When Raised:**
- URL is empty or None
- URL is not a valid YouTube URL
- URL domain is not supported

### FetchException

Raised when fetching metadata fails.

```python
class FetchException(MediaDownloaderException):
    """Raised when fetching metadata fails."""
```

**When Raised:**
- Network error during metadata fetch
- yt-dlp extraction fails
- Video is private or unavailable

### DownloadException

Raised when downloading fails.

```python
class DownloadException(MediaDownloaderException):
    """Raised when downloading fails."""
```

**When Raised:**
- Network error during download
- Insufficient disk space
- Write permission denied
- yt-dlp download fails

### FFmpegException

Raised when FFmpeg operations fail.

```python
class FFmpegException(MediaDownloaderException):
    """Raised when FFmpeg operations fail."""
```

**When Raised:**
- FFmpeg not found in PATH
- Media processing fails
- Encoding errors

### SpotifyAuthException

Raised when Spotify authentication fails (future use).

```python
class SpotifyAuthException(MediaDownloaderException):
    """Raised when Spotify authentication fails."""
```

---

## Usage Examples

### Complete Download Workflow

```python
from core.controller import Controller
from core.exceptions import InvalidURLException, DownloadException

controller = Controller()

# Step 1: Fetch metadata
try:
    metadata = controller.fetch_metadata("https://www.youtube.com/watch?v=...")
    print(f"Title: {metadata['title']}")
    print(f"Available qualities: {[f['quality'] for f in metadata['formats']]}")
except InvalidURLException as e:
    print(f"Invalid URL: {e}")
except FetchException as e:
    print(f"Failed to fetch: {e}")

# Step 2: Download with progress
def progress_callback(percent: float, status: str):
    print(f"\r{percent:.1f}% - {status}", end="", flush=True)

try:
    file_path = controller.download(
        url="https://www.youtube.com/watch?v=...",
        output_path="C:/Downloads",
        quality="1080p",
        progress_callback=progress_callback
    )
    print(f"\nDownloaded: {file_path}")
except DownloadException as e:
    print(f"Download failed: {e}")
```

### Custom Service Integration

```python
from core.controller import Controller
from services.youtube_metadata_service import YouTubeMetadataService

# Custom metadata service with modified behavior
class CustomMetadataService(YouTubeMetadataService):
    def fetch_metadata(self, url: str):
        metadata = super().fetch_metadata(url)
        # Add custom processing
        return metadata

# Inject custom service
controller = Controller(metadata_service=CustomMetadataService())
```

---

**Last Updated**: 2025-11-21  
**Version**: 7.0.0
