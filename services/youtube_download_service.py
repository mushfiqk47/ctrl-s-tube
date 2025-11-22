"""YouTube download service."""

import yt_dlp
import os
from typing import Optional
from core.types import ProgressCallback
from core.exceptions import DownloadException
from utils.config import Config
from utils.progress_handler import ProgressHandler
from utils.logger import get_logger

logger = get_logger(__name__)


class YouTubeDownloadService:
    """Handles YouTube video downloading operations."""
    
    def __init__(self):
        """Initialize YouTube download service."""
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
        logger.info("YouTubeDownloadService initialized")
    
    def download(
        self,
        url: str,
        output_path: str,
        quality: Optional[str] = None,
        format: str = "mkv",
        progress_callback: Optional[ProgressCallback] = None
    ) -> str:
        """
        Download YouTube video or playlist.
        
        Args:
            url: YouTube URL
            output_path: Directory to save the video
            quality: Quality selection (e.g., "720p", "1080p", "Audio Only")
            format: Output format ("mp4" or "mkv")
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to downloaded file or directory
            
        Raises:
            DownloadException: If download fails
        """
        logger.info(f"Starting download: {url} to {output_path} with quality {quality} and format {format}")
        
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_path, exist_ok=True)

            # Build download options
            ydl_opts = self._build_download_options(url, output_path, quality, format)
            
            # Set up progress tracking
            if progress_callback:
                progress_handler = ProgressHandler(progress_callback)
                ydl_opts['progress_hooks'] = [progress_handler.create_yt_dlp_hook()]

            # Download the video(s)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Return appropriate path
                if 'entries' in info:
                    # Playlist
                    playlist_title = info.get('title', 'Playlist')
                    result_path = os.path.join(output_path, playlist_title)
                    logger.info(f"Playlist download complete: {result_path}")
                    return result_path
                else:
                    # Single video
                    filename = self._get_output_filename(ydl, info, quality, format)
                    logger.info(f"Video download complete: {filename}")
                    return filename

        except Exception as e:
            logger.error(f"YouTube download failed: {str(e)}", exc_info=True)
            raise DownloadException(f"YouTube download failed: {str(e)}")
    
    def _build_download_options(self, url: str, output_path: str, quality: Optional[str], format: str = "mkv") -> dict:
        """
        Build yt-dlp download options.
        
        Args:
            url: YouTube URL
            output_path: Output directory
            quality: Quality selection
            format: Output format ("mp4" or "mkv")
            
        Returns:
            Dictionary of yt-dlp options
        """
        ydl_opts = {
            **self.ydl_opts_base,
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        }

        # Handle playlists
        if 'playlist' in url or 'list=' in url:
            ydl_opts['outtmpl'] = os.path.join(output_path, '%(playlist_title)s', '%(title)s.%(ext)s')
            ydl_opts['yes_playlist'] = True
        else:
            ydl_opts['noplaylist'] = True

        # Configure format based on quality
        if quality == "Audio Only":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': Config.AUDIO_BITRATE,
                }],
            })
            logger.debug("Configured for audio-only download")
        else:
            # Video download
            format_string = self._parse_quality_to_format(quality)
            ydl_opts['format'] = format_string
            ydl_opts['merge_output_format'] = format
            logger.debug(f"Configured for video download: {format_string} in {format}")

        return ydl_opts
    
    def _parse_quality_to_format(self, quality: Optional[str]) -> str:
        """
        Parse quality string to yt-dlp format string.
        
        Args:
            quality: Quality selection string
            
        Returns:
            yt-dlp format string
        """
        if not quality or quality == "Best Available":
            return 'bestvideo+bestaudio/best'
        
        # Remove .mkv extension if present
        quality_clean = quality.replace('.mkv', '')
        
        # Extract resolution height
        import re
        
        # Handle formats like "4K (2160p)", "720p", "1080p60"
        if '(' in quality_clean and 'p)' in quality_clean:
            match = re.search(r'\((\d+p\d*)\)', quality_clean)
            if match:
                resolution = match.group(1)
            else:
                resolution = quality_clean
        else:
            resolution = quality_clean
        
        # Extract numeric height
        if resolution.endswith('p') or 'p' in resolution:
            height = resolution.replace('p', '').split()[0]
            if height.isdigit():
                return f'bestvideo[height<={height}]+bestaudio/best[height<={height}]'
        
        return 'bestvideo+bestaudio/best'
    
    def _get_output_filename(self, ydl: yt_dlp.YoutubeDL, info: dict, quality: Optional[str], format: str = "mkv") -> str:
        """
        Get the output filename for downloaded file.
        
        Args:
            ydl: YoutubeDL instance
            info: Video info dict
            quality: Quality selection
            format: Output format
            
        Returns:
            Full path to output file
        """
        filename = ydl.prepare_filename(info)
        
        # Adjust extension based on download type
        if quality == "Audio Only":
            filename = os.path.splitext(filename)[0] + '.mp3'
        else:
            filename = os.path.splitext(filename)[0] + f'.{format}'
        
        return filename
