"""Type definitions for the Ctrl+S Tube application."""

from typing import TypedDict, Optional, Literal, Callable


class FormatInfo(TypedDict):
    """Type definition for video format information."""
    label: str
    height: int
    width: int
    fps: int
    vcodec: str
    acodec: str
    ext: str
    tbr: float
    format_id: str
    resolution: str
    quality: str


class VideoMetadata(TypedDict):
    """Type definition for video metadata."""
    platform: Literal["youtube"]
    type: Literal["video", "playlist"]
    title: str
    duration: Optional[int]
    thumbnail: str
    formats: list[FormatInfo]
    count: Optional[int]  # For playlists


class DownloadProgress(TypedDict):
    """Type definition for download progress information."""
    percent: float
    status: str
    downloaded_bytes: Optional[int]
    total_bytes: Optional[int]
    playlist_index: Optional[int]
    n_entries: Optional[int]


# Type aliases
ProgressCallback = Callable[[float, str], None]
Platform = Literal["youtube"]
DownloadType = Literal["video", "audio"]
