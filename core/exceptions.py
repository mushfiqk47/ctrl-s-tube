"""Custom exceptions for the Media Downloader application."""


class MediaDownloaderException(Exception):
    """Base exception for all Media Downloader errors."""
    pass


class InvalidURLException(MediaDownloaderException):
    """Raised when an invalid URL is provided."""
    pass


class FetchException(MediaDownloaderException):
    """Raised when fetching metadata fails."""
    pass


class DownloadException(MediaDownloaderException):
    """Raised when downloading fails."""
    pass


class FFmpegException(MediaDownloaderException):
    """Raised when FFmpeg operations fail."""
    pass



