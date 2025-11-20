"""URL routing to identify platform (YouTube only)."""

from typing import Literal
from core.exceptions import InvalidURLException


Platform = Literal["youtube"]


class URLRouter:
    """Routes URLs to appropriate service based on platform."""
    
    YOUTUBE_DOMAINS = ["youtube.com", "youtu.be", "m.youtube.com"]
    
    @classmethod
    def identify_platform(cls, url: str) -> Platform:
        """
        Identify which platform a URL belongs to.
        
        Args:
            url: The URL to check
            
        Returns:
            Platform name ("youtube")
            
        Raises:
            InvalidURLException: If URL doesn't match YouTube
        """
        url_lower = url.lower()
        
        # Check YouTube
        if any(domain in url_lower for domain in cls.YOUTUBE_DOMAINS):
            return "youtube"
        
        # No match
        raise InvalidURLException(
            f"Invalid URL. Only YouTube URLs are supported."
        )
