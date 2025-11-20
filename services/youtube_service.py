"""YouTube service for downloading videos."""

import yt_dlp
import os
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from core.exceptions import FetchException, DownloadException


class YouTubeService:
    """Handles YouTube video downloading and metadata fetching."""
    
    def __init__(self):
        """Initialize YouTube service."""
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
    
    def fetch_metadata(self, url: str) -> Dict[str, Any]:
        """
        Fetch metadata for a YouTube video.

        Args:
            url: YouTube video URL

        Returns:
            Dictionary with video metadata including available formats

        Raises:
            FetchException: If fetching fails
        """
        try:
            ydl_opts = {
                **self.ydl_opts_base,
                'skip_download': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Single extract_info call with process=True for efficiency
                info = ydl.extract_info(url, download=False)
                
                # Check if it's a playlist based on the extracted info
                if info.get('_type') == 'playlist':
                    #It's a playlist
                    return {
                        'platform': 'youtube',
                        'type': 'playlist',
                        'title': info.get('title', 'Unknown Playlist'),
                        'count': len(list(info.get('entries', []))),
                        'thumbnail': info.get('thumbnail', ''),
                        'formats': []  # No specific formats for playlist, will use generic options
                    }

                # It's a single video - extract available quality options
                # Group formats by height to avoid duplicates
                quality_groups = {}

                # Define standard video heights we want to support
                STANDARD_HEIGHTS = {2160, 1440, 1080, 720, 480, 360, 240, 144}
                
                # Get all available video formats - optimized with list comprehension
                video_formats = [
                    fmt for fmt in info.get('formats', [])
                    if fmt.get('vcodec') and fmt.get('vcodec') != 'none' 
                    and fmt.get('height', 0) in STANDARD_HEIGHTS
                ]
                
                for format_info in video_formats:
                    height = format_info.get('height', 0)
                    width = format_info.get('width', 0)
                    fps = format_info.get('fps', 0)
                    vcodec = format_info.get('vcodec', '')
                    acodec = format_info.get('acodec', '')
                    ext = format_info.get('ext', '')
                    total_bitrate = format_info.get('tbr', 0)  # Total bitrate
                    format_id = format_info.get('format_id', '')

                    # Create a key for grouping (height + fps tier)
                    # Group standard fps (<=30) and high fps (>30) separately
                    fps_key = 'high' if fps and fps > 30 else 'standard'
                    group_key = f"{height}_{fps_key}"

                    # Only keep the best format for each group (highest bitrate)
                    if group_key not in quality_groups or total_bitrate > quality_groups[group_key]['tbr']:
                        # Create quality label
                        quality_label = f"{height}p"
                        if fps and fps > 30:
                            quality_label = f"{height}p{int(fps)}"
                        
                        # Add friendly name for common resolutions
                        if height == 2160:
                            quality_label = "4K (2160p)" if fps_key == 'standard' else f"4K (2160p{int(fps)})"
                        elif height == 1440:
                            quality_label = "2K (1440p)" if fps_key == 'standard' else f"2K (1440p{int(fps)})"

                        quality_groups[group_key] = {
                            'label': quality_label,
                            'height': height,
                            'width': width,
                            'fps': fps,
                            'vcodec': vcodec,
                            'acodec': acodec,
                            'ext': ext,
                            'tbr': total_bitrate,
                            'format_id': format_id,
                            'resolution': f"{width}x{height}",
                            'quality': quality_label
                        }

                # Convert grouped formats to list
                formats = list(quality_groups.values())

                # Sort by height descending, then by FPS
                formats.sort(key=lambda x: (x['height'], x['fps']), reverse=True)

                return {
                    'platform': 'youtube',
                    'type': 'video',
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': formats
                }

        except Exception as e:
            raise FetchException(f"Failed to fetch YouTube metadata: {str(e)}")
    
    def download(
        self,
        url: str,
        output_path: str,
        quality: Optional[str] = None,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> str:
        """
        Download YouTube video.

        Args:
            url: YouTube video URL
            output_path: Directory to save the video
            quality: Quality selection (e.g., "720p", "1080p", "Audio Only")
            progress_callback: Optional callback for progress updates

        Returns:
            Path to downloaded file

        Raises:
            DownloadException: If download fails
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_path, exist_ok=True)

            # Configure download options based on quality
            ydl_opts = {
                **self.ydl_opts_base,
                # Default output template for single video
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            }

            # Check if it's a playlist (by URL or if we had metadata passed, but here we just check URL/behavior)
            # We'll rely on yt-dlp's default behavior for playlists, but we need to adjust output template
            # to put playlist items in a subfolder
            if 'playlist' in url or 'list=' in url:
                ydl_opts['outtmpl'] = os.path.join(output_path, '%(playlist_title)s', '%(title)s.%(ext)s')
                ydl_opts['yes_playlist'] = True
            else:
                ydl_opts['noplaylist'] = True

            if quality == "Audio Only":
                # Audio-only extraction
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',
                    }],
                })
            else:
                # Video download - if we get a specific quality like "720p", we need to find the best matching format
                if quality and quality != "Audio Only":
                    # Extract resolution from quality label like "720p", "1080p", etc.
                    if quality.endswith('p'):
                        height = quality.replace('p', '')
                        if height.isdigit():
                            ydl_opts['format'] = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]'
                        else:
                            ydl_opts['format'] = 'bestvideo+bestaudio/best'
                    else:
                        ydl_opts['format'] = 'bestvideo+bestaudio/best'
                else:
                    # Default to best available
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'

                # Merge to MKV format
                ydl_opts['merge_output_format'] = 'mkv'

            # Add progress hook if callback provided
            if progress_callback:
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        try:
                            downloaded = d.get('downloaded_bytes', 0)
                            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                            if total > 0:
                                percent = (downloaded / total) * 100
                                # Add info about which video is downloading if available
                                info_prefix = ""
                                if 'playlist_index' in d and 'n_entries' in d:
                                    info_prefix = f"[{d['playlist_index']}/{d['n_entries']}] "
                                
                                progress_callback(percent, f"{info_prefix}Downloading...")
                        except Exception:
                            # Silently ignore progress calculation errors to not interrupt download
                            pass
                    elif d['status'] == 'finished':
                        progress_callback(100, "Processing...")

                ydl_opts['progress_hooks'] = [progress_hook]

            # Download the video(s)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Return path - for playlist it's a bit complex, we'll return the directory
                if 'entries' in info:
                    # It was a playlist
                    playlist_title = info.get('title', 'Playlist')
                    return os.path.join(output_path, playlist_title)
                else:
                    # Single video
                    filename = ydl.prepare_filename(info)
                    # Adjust filename extension for audio-only
                    if quality == "Audio Only":
                        filename = os.path.splitext(filename)[0] + '.mp3'
                    else:
                        filename = os.path.splitext(filename)[0] + '.mkv'
                    return filename

        except Exception as e:
            raise DownloadException(f"YouTube download failed: {str(e)}")
