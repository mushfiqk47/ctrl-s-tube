"""YouTube metadata fetching service."""

import yt_dlp
from typing import Union
from core.types import VideoMetadata, FormatInfo
from core.exceptions import FetchException
from utils.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class YouTubeMetadataService:
    """Handles YouTube metadata fetching operations."""
    
    def __init__(self):
        """Initialize YouTube metadata service."""
        self.ydl_opts_base = {
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }
        logger.info("YouTubeMetadataService initialized")
    
    def fetch_metadata(self, url: str) -> VideoMetadata:
        """
        Fetch metadata for a YouTube video or playlist.
        
        Args:
            url: YouTube video or playlist URL
            
        Returns:
            Video metadata dictionary
            
        Raises:
            FetchException: If fetching fails
        """
        logger.info(f"Fetching metadata for URL: {url}")
        
        try:
            ydl_opts = {
                **self.ydl_opts_base,
                'skip_download': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Single extract_info call for efficiency
                info = ydl.extract_info(url, download=False)
                
                # Check if it's a playlist
                if info.get('_type') == 'playlist':
                    logger.info(f"Detected playlist: {info.get('title')} with {len(list(info.get('entries', [])))} videos")
                    return self._build_playlist_metadata(info)
                
                # Single video
                logger.info(f"Detected single video: {info.get('title')}")
                return self._build_video_metadata(info)

        except Exception as e:
            logger.error(f"Failed to fetch YouTube metadata: {str(e)}", exc_info=True)
            raise FetchException(f"Failed to fetch YouTube metadata: {str(e)}")
    
    def _build_playlist_metadata(self, info: dict) -> VideoMetadata:
        """Build metadata dict for playlist."""
        return VideoMetadata(
            platform="youtube",
            type="playlist",
            title=info.get('title', 'Unknown Playlist'),
            duration=None,
            thumbnail=info.get('thumbnail', ''),
            formats=[],
            count=len(list(info.get('entries', [])))
        )
    
    def _build_video_metadata(self, info: dict) -> VideoMetadata:
        """Build metadata dict for single video."""
        formats = self._extract_formats(info)
        logger.debug(f"Extracted {len(formats)} quality options")
        
        return VideoMetadata(
            platform="youtube",
            type="video",
            title=info.get('title', 'Unknown'),
            duration=info.get('duration', 0),
            thumbnail=info.get('thumbnail', ''),
            formats=formats,
            count=None
        )
    
    def _extract_formats(self, info: dict) -> list[FormatInfo]:
        """
        Extract and filter video formats.
        
        Args:
            info: yt-dlp info dict
            
        Returns:
            List of format information dicts
        """
        quality_groups = {}
        
        # Pre-filter video formats with list comprehension
        video_formats = [
            fmt for fmt in info.get('formats', [])
            if fmt.get('vcodec') and fmt.get('vcodec') != 'none'
            and fmt.get('height', 0) in Config.STANDARD_VIDEO_HEIGHTS
        ]
        
        for format_info in video_formats:
            height = format_info.get('height', 0)
            width = format_info.get('width', 0)
            fps = format_info.get('fps', 0)
            vcodec = format_info.get('vcodec', '')
            acodec = format_info.get('acodec', '')
            ext = format_info.get('ext', '')
            total_bitrate = format_info.get('tbr', 0)
            format_id = format_info.get('format_id', '')

            # Group by height + fps tier
            fps_key = 'high' if fps and fps > 30 else 'standard'
            group_key = f"{height}_{fps_key}"

            # Keep best format for each group (highest bitrate)
            if group_key not in quality_groups or total_bitrate > quality_groups[group_key]['tbr']:
                quality_label = self._format_quality_label(height, fps, fps_key)
                
                quality_groups[group_key] = FormatInfo(
                    label=quality_label,
                    height=height,
                    width=width,
                    fps=fps,
                    vcodec=vcodec,
                    acodec=acodec,
                    ext=ext,
                    tbr=total_bitrate,
                    format_id=format_id,
                    resolution=f"{width}x{height}",
                    quality=quality_label
                )

        # Convert to list and sort
        formats = list(quality_groups.values())
        formats.sort(key=lambda x: (x['height'], x['fps']), reverse=True)
        
        return formats
    
    def _format_quality_label(self, height: int, fps: int, fps_key: str) -> str:
        """
        Format a quality label string.
        
        Args:
            height: Video height in pixels
            fps: Frames per second
            fps_key: FPS tier ('standard' or 'high')
            
        Returns:
            Formatted quality label
        """
        quality_label = f"{height}p"
        
        if fps and fps > 30:
            quality_label = f"{height}p{int(fps)}"
        
        # Add friendly names for common resolutions
        if height == 2160:
            quality_label = "4K (2160p)" if fps_key == 'standard' else f"4K (2160p{int(fps)})"
        elif height == 1440:
            quality_label = "2K (1440p)" if fps_key == 'standard' else f"2K (1440p{int(fps)})"
        
        return quality_label
