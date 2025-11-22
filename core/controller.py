"""Main controller coordinating between UI and services with dependency injection."""

from typing import Dict, Any, Callable, Optional
from core.router import URLRouter
from core.exceptions import InvalidURLException, FetchException, DownloadException
from core.types import VideoMetadata, ProgressCallback
from services.youtube_metadata_service import YouTubeMetadataService
from services.youtube_download_service import YouTubeDownloadService
from utils.validators import URLValidator, PathValidator
from utils.logger import get_logger

logger = get_logger(__name__)


class Controller:
    """Orchestrates fetch and download operations with dependency injection."""
    
    def __init__(
        self,
        metadata_service: Optional[YouTubeMetadataService] = None,
        download_service: Optional[YouTubeDownloadService] = None
    ):
        """
        Initialize controller with services.
        
        Args:
            metadata_service: Optional YouTubeMetadataService instance (for DI/testing)
            download_service: Optional YouTubeDownloadService instance (for DI/testing)
        """
        self.metadata_service = metadata_service or YouTubeMetadataService()
        self.download_service = download_service or YouTubeDownloadService()
        logger.info("Controller initialized with dependency injection")
    
    def fetch_metadata(self, url: str) -> VideoMetadata:
        """
        Fetch metadata for a given URL with validation.
        
        Args:
            url: YouTube URL
            
        Returns:
            Dictionary containing metadata:
            - platform: "youtube"
            - title: Video title
            - formats: Available quality options
            
        Raises:
            InvalidURLException: If URL is invalid
            FetchException: If fetching fails
        """
        logger.info(f"Controller: Fetching metadata for URL")
        
        try:
            # Validate URL first
            validated_url = URLValidator.validate_youtube_url(url)
            
            # Identify platform (currently only YouTube)
            platform = URLRouter.identify_platform(validated_url)
            
            if platform != "youtube":
                raise InvalidURLException("Only YouTube URLs are supported")
            
            # Fetch metadata using service
            return self.metadata_service.fetch_metadata(validated_url)
                
        except InvalidURLException:
            logger.warning(f"Invalid URL provided: {url}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch metadata: {str(e)}", exc_info=True)
            raise FetchException(f"Failed to fetch metadata: {str(e)}")
    
    def download(
        self,
        url: str,
        output_path: str,
        quality: Optional[str] = None,
        format: str = "mkv",
        progress_callback: Optional[ProgressCallback] = None
    ) -> str:
        """
        Download media from URL with validation.
        
        Args:
            url: YouTube URL
            output_path: Directory to save downloaded files
            quality: Quality selection (e.g., "720p", "Audio Only")
            format: Output format ("mp4" or "mkv")
            progress_callback: Optional callback for progress updates (percent, status)
            
        Returns:
            Path to downloaded file
            
        Raises:
            InvalidURLException: If URL is invalid
            DownloadException: If download fails
        """
        logger.info(f"Controller: Starting download to {output_path}")
        
        try:
            # Validate URL
            validated_url = URLValidator.validate_youtube_url(url)
            
            # Validate and sanitize output path
            validated_path = PathValidator.validate_output_path(output_path)
            
            # Identify platform
            platform = URLRouter.identify_platform(validated_url)
            
            if platform != "youtube":
                raise InvalidURLException("Only YouTube URLs are supported")
            
            # Download using service
            return self.download_service.download(
                validated_url,
                str(validated_path),
                quality,
                format,
                progress_callback
            )
                
        except InvalidURLException:
            logger.warning(f"Invalid URL provided for download: {url}")
            raise
        except ValueError as e:
            # Path validation errors
            logger.error(f"Invalid output path: {str(e)}")
            raise DownloadException(f"Invalid output path: {str(e)}")
        except Exception as e:
            logger.error(f"Download failed: {str(e)}", exc_info=True)
            raise DownloadException(f"Download failed: {str(e)}")
