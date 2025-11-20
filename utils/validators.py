"""Input validation and sanitization utilities."""

import re
from pathlib import Path
from typing import Optional
from core.exceptions import InvalidURLException


class URLValidator:
    """Validates and sanitizes URLs."""
    
    YOUTUBE_PATTERNS = [
        r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'^https?://(?:www\.)?youtube\.com/playlist\?list=[\w-]+',
        r'^https?://youtu\.be/[\w-]+',
        r'^https?://(?:www\.)?youtube\.com/shorts/[\w-]+',
        r'^https?://m\.youtube\.com/watch\?v=[\w-]+',
    ]
    
    @classmethod
    def validate_youtube_url(cls, url: str) -> str:
        """
        Validate and sanitize a YouTube URL.
        
        Args:
            url: URL to validate
            
        Returns:
            Sanitized URL
            
        Raises:
            InvalidURLException: If URL is invalid
        """
        if not url or not isinstance(url, str):
            raise InvalidURLException("URL must be a non-empty string")
        
        url = url.strip()
        
        # Check against patterns
        for pattern in cls.YOUTUBE_PATTERNS:
            if re.match(pattern, url, re.IGNORECASE):
                return url
        
        raise InvalidURLException(
            "Invalid YouTube URL. Please provide a valid YouTube video or playlist URL."
        )


class PathValidator:
    """Validates and sanitizes file system paths."""
    
    @staticmethod
    def validate_output_path(path: str) -> Path:
        """
        Validate and sanitize an output directory path.
        
        Args:
            path: Directory path to validate
            
        Returns:
            Validated Path object
            
        Raises:
            ValueError: If path is invalid or insecure
        """
        if not path or not isinstance(path, str):
            raise ValueError("Path must be a non-empty string")
        
        # Convert to Path object
        path_obj = Path(path).resolve()
        
        # Security: Check for path traversal attempts
        try:
            # Ensure the resolved path is actually within expected bounds
            path_obj.relative_to(Path.cwd().resolve().anchor)
        except ValueError:
            # Path is outside the file system root
            raise ValueError("Invalid path: Path traversal detected")
        
        # Check if path exists and is a directory
        if path_obj.exists() and not path_obj.is_dir():
            raise ValueError(f"Path exists but is not a directory: {path}")
        
        # Check write permissions (create if doesn't exist)
        try:
            path_obj.mkdir(parents=True, exist_ok=True)
            # Try to create a test file to verify write access
            test_file = path_obj / ".write_test"
            test_file.touch()
            test_file.unlink()
        except PermissionError:
            raise ValueError(f"No write permission for directory: {path}")
        except Exception as e:
            raise ValueError(f"Cannot access directory: {e}")
        
        return path_obj
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename by removing invalid characters.
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Sanitized filename
        """
        # Remove or replace invalid characters for Windows/Unix
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '_', filename)
        
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip('. ')
        
        # Ensure filename is not empty
        if not sanitized:
            sanitized = "download"
        
        # Limit length (Windows has 255 char limit for filenames)
        if len(sanitized) > 200:
            sanitized = sanitized[:200]
        
        return sanitized


class QualityValidator:
    """Validates quality selection strings."""
    
    VALID_QUALITY_PATTERNS = [
        r'^\d+p\d*$',  # e.g., 1080p, 720p60
        r'^[24]K \(\d+p\d*\)$',  # e.g., 4K (2160p), 2K (1440p60)
        r'^Audio Only$',
        r'^MP3 \d+kbps$',
        r'^Best Available$',
        r'^\d+p\d*\.mkv$',  # e.g., 1080p.mkv
    ]
    
    @classmethod
    def validate_quality(cls, quality: str) -> str:
        """
        Validate a quality selection string.
        
        Args:
            quality: Quality string to validate
            
        Returns:
            Validated quality string
            
        Raises:
            ValueError: If quality format is invalid
        """
        if not quality or not isinstance(quality, str):
            raise ValueError("Quality must be a non-empty string")
        
        quality = quality.strip()
        
        # Check against valid patterns
        for pattern in cls.VALID_QUALITY_PATTERNS:
            if re.match(pattern, quality):
                return quality
        
        raise ValueError(f"Invalid quality format: {quality}")
