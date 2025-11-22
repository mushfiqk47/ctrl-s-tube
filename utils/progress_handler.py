"""Progress tracking handler for download operations."""

import threading
from typing import Optional, Callable
from core.types import DownloadProgress


class ProgressHandler:
    """Thread-safe progress tracking for downloads."""
    
    def __init__(self, callback: Optional[Callable[[float, str], None]] = None):
        """
        Initialize progress handler.
        
        Args:
            callback: Optional callback function(percent, status)
        """
        self.callback = callback
        self._lock = threading.Lock()
        self._cancelled = False
        self._current_percent = 0.0
        self._current_status = ""
    
    def update(self, percent: float, status: str):
        """
        Update progress.
        
        Args:
            percent: Progress percentage (0-100)
            status: Status message
        """
        with self._lock:
            if self._cancelled:
                return
            
            self._current_percent = percent
            self._current_status = status
            
            if self.callback:
                try:
                    self.callback(percent, status)
                except Exception as e:
                    # Don't let callback errors stop downloads
                    print(f"Warning: Progress callback error: {e}")
    
    def cancel(self):
        """Cancel the operation."""
        with self._lock:
            self._cancelled = True
    
    def is_cancelled(self) -> bool:
        """Check if operation is cancelled."""
        with self._lock:
            return self._cancelled
    
    def get_progress(self) -> tuple[float, str]:
        """
        Get current progress.
        
        Returns:
            Tuple of (percent, status)
        """
        with self._lock:
            return self._current_percent, self._current_status
    
    def create_yt_dlp_hook(self) -> Callable:
        """
        Create a yt-dlp compatible progress hook.
        
        Returns:
            Progress hook function
        """
        def progress_hook(d: dict):
            """yt-dlp progress hook."""
            if self.is_cancelled():
                raise Exception("Download cancelled by user")
            
            if d['status'] == 'downloading':
                try:
                    downloaded = d.get('downloaded_bytes', 0)
                    total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    speed = d.get('speed', 0)
                    
                    if total > 0:
                        percent = (downloaded / total) * 100
                        
                        # Format speed
                        speed_str = ""
                        if speed:
                            if speed > 1024 * 1024:  # MB/s
                                speed_str = f" ({speed / (1024 * 1024):.1f} MB/s)"
                            elif speed > 1024:  # KB/s
                                speed_str = f" ({speed / 1024:.1f} KB/s)"
                            else:  # B/s
                                speed_str = f" ({speed:.0f} B/s)"
                        
                        # Add playlist info if available
                        info_prefix = ""
                        if 'playlist_index' in d and 'n_entries' in d:
                            info_prefix = f"[{d['playlist_index']}/{d['n_entries']}] "
                        
                        self.update(percent, f"{info_prefix}Downloading...{speed_str}")
                except Exception:
                    # Ignore progress calculation errors
                    pass
            elif d['status'] == 'finished':
                self.update(100, "Processing...")
        
        return progress_hook
