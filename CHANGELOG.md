# Changelog

All notable changes to the Ctrl+S Tube project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Spotify integration for music downloads
- Download history and favorites tracking
- Pause/resume functionality
- Download queue management
- Custom output filename templates
- Dark/light theme toggle
- Settings panel for user preferences
- Browser extension integration
- Keyboard shortcuts configuration
- Multiple simultaneous downloads

## [7.0.0] - 2025-11-21

### Added
- **Modern Qt Interface** - Complete UI redesign using PySide6
  - Clean, minimalist dark mode design
  - YouTube-inspired color scheme with red accents
  - Responsive layout optimized for 480x600 window
  - Poppins font family throughout
  
- **Playlist Support** - Download entire YouTube playlists
  - Automatic playlist detection
  - Batch download with progress tracking
  - Individual video quality selection
  
- **Enhanced Quality Selection** - Improved video quality options
  - Support for 4K, 1080p, 720p, 480p resolutions
  - Automatic quality normalization and labeling
  - Duplicate quality removal
  - Intelligent format selection
  
- **Layered Architecture** - Complete codebase refactor
  - Core layer with Controller and Router
  - Service layer with dedicated metadata and download services
  - Utilities layer with validators, logger, config
  - Dependency injection for better testability
  
- **Type Safety** - Comprehensive type definitions
  - TypedDict for data contracts
  - Type hints throughout codebase
  - MyPy configuration for static type checking
  
- **Robust Error Handling** - Custom exception hierarchy
  - `InvalidURLException` for URL validation errors
  - `FetchException` for metadata fetch failures
  - `DownloadException` for download failures
  - User-friendly error messages
  
- **Logging System** - Comprehensive logging framework
  - File logging to `logs/` directory
  - Console logging for development
  - Configurable log levels
  - Timestamped log files
  
- **Input Validation** - Strict validation for all inputs
  - URL validation with YouTube domain checking
  - Path validation for safe file operations
  - Format validation for quality selection
  
- **Progress Tracking** - Real-time download progress
  - Visual progress bar with percentage
  - Status messages (downloading, processing, etc.)
  - Playlist progress with item counts
  
- **Threading Model** - Non-blocking UI operations
  - QThread workers for fetch operations
  - Separate threads for downloads
  - Signal/slot communication for thread safety
  
- **Automated Setup** - Windows batch scripts
  - `setup.bat` for automated installation
  - `run.bat` for easy application launch
  - Virtual environment creation
  - Dependency installation
  - FFmpeg verification

### Changed
- **Video Format** - Changed default video format from MP4 to MKV
  - Better quality preservation
  - Support for multiple audio/subtitle tracks
  
- **Audio Format** - Switched to MP3 320kbps
  - Universal compatibility
  - High quality audio
  
- **UI Layout** - Redesigned from ground up
  - Video/Audio toggle buttons instead of dropdown
  - Larger, more prominent quality selector
  - Improved visual hierarchy
  - Better use of white space
  
- **Code Organization** - Split monolithic services
  - Separated metadata fetching from downloading
  - Dedicated service classes
  - Clear separation of concerns

### Fixed
- Quality options showing duplicates
- Progress bar not updating correctly
- Playlist downloads failing on some URLs
- FFmpeg path detection issues
- UI freezing during long downloads
- Memory leaks in worker threads

### Security
- Path traversal protection in file operations
- Input sanitization for URLs and paths
- Safe filename generation
- Environment variable for sensitive config

### Development
- Pytest configuration and test suite
- Black code formatting (100 char line length)
- Flake8 linting rules
- MyPy type checking configuration
- Comprehensive docstrings
- README and documentation

## [6.0.0] - 2024-XX-XX

### Added
- Initial desktop application with basic Qt interface
- YouTube video downloads
- Audio extraction capability
- Basic progress tracking

### Changed
- Migrated from CLI to GUI application

## [5.0.0] - 2024-XX-XX

### Added
- Command-line interface
- Basic YouTube download support

---

## Version Naming Conventions

- **Major version (X.0.0)** - Breaking changes, major feature additions
- **Minor version (7.X.0)** - New features, backwards compatible
- **Patch version (7.0.X)** - Bug fixes, minor improvements

## Links

- [Repository](https://github.com/username/ctrl-s-tube)
- [Issue Tracker](https://github.com/username/ctrl-s-tube/issues)
- [Releases](https://github.com/username/ctrl-s-tube/releases)

---

**Note**: Dates use YYYY-MM-DD format (ISO 8601)
