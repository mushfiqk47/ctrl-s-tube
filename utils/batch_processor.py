"""Batch processing utilities for multiple video downloads."""

import re
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass, field
from threading import Lock
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class VideoItem:
    """Represents a video in a batch download queue."""
    url: str
    title: str = "Loading..."
    thumbnail: str = ""
    duration: str = ""
    status: str = "pending"  # pending, fetching, ready, downloading, complete, error
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class BatchProgress:
    """Thread-safe progress tracker for batch downloads."""
    
    def __init__(self, total_items: int):
        """
        Initialize batch progress tracker.
        
        Args:
            total_items: Total number of items in the batch
        """
        self.total_items = total_items
        self.completed_items = 0
        self.failed_items = 0
        self.current_progress: Dict[str, float] = {}
        self._lock = Lock()
        logger.info(f"BatchProgress initialized with {total_items} items")
    
    def update_item_progress(self, item_id: str, progress: float) -> None:
        """
        Update progress for a specific item.
        
        Args:
            item_id: Unique identifier for the item
            progress: Progress percentage (0-100)
        """
        with self._lock:
            self.current_progress[item_id] = progress
    
    def mark_completed(self, item_id: str) -> None:
        """
        Mark an item as completed.
        
        Args:
            item_id: Unique identifier for the item
        """
        with self._lock:
            self.completed_items += 1
            self.current_progress[item_id] = 100.0
            logger.debug(f"Item {item_id} marked complete ({self.completed_items}/{self.total_items})")
    
    def mark_failed(self, item_id: str) -> None:
        """
        Mark an item as failed.
        
        Args:
            item_id: Unique identifier for the item
        """
        with self._lock:
            self.failed_items += 1
            self.current_progress[item_id] = 0.0
            logger.warning(f"Item {item_id} marked failed ({self.failed_items} failures)")
    
    def get_overall_progress(self) -> float:
        """
        Calculate overall progress percentage.
        
        Returns:
            Overall progress (0-100)
        """
        with self._lock:
            if self.total_items == 0:
                return 0.0
            
            # Sum all individual progresses
            total_progress = sum(self.current_progress.values())
            # Average across all items
            overall = total_progress / self.total_items
            return min(100.0, overall)
    
    def get_status_summary(self) -> str:
        """
        Get status summary string.
        
        Returns:
            Status string like "3/10 complete, 1 failed"
        """
        with self._lock:
            status = f"{self.completed_items}/{self.total_items} complete"
            if self.failed_items > 0:
                status += f", {self.failed_items} failed"
            return status
    
    def is_complete(self) -> bool:
        """
        Check if all items are processed.
        
        Returns:
            True if all items completed or failed
        """
        with self._lock:
            return (self.completed_items + self.failed_items) >= self.total_items


def extract_urls(text: str) -> List[str]:
    """
    Extract YouTube URLs from text.
    
    Supports formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    
    Args:
        text: Text containing YouTube URLs
        
    Returns:
        List of extracted YouTube URLs
    """
    logger.debug("Extracting URLs from text")
    
    # Comprehensive YouTube URL regex patterns
    patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+(?:&\S*)?',
        r'https?://(?:www\.)?youtube\.com/shorts/[\w-]+',
        r'https?://youtu\.be/[\w-]+(?:\?\S*)?',
        r'https?://m\.youtube\.com/watch\?v=[\w-]+(?:&\S*)?',
        r'https?://(?:www\.)?youtube\.com/embed/[\w-]+',
    ]
    
    urls = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        urls.extend(matches)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in urls:
        # Normalize URL for deduplication
        normalized = url.lower().split('&')[0]  # Remove extra params
        if normalized not in seen:
            seen.add(normalized)
            unique_urls.append(url)
    
    logger.info(f"Extracted {len(unique_urls)} unique YouTube URLs")
    return unique_urls


def validate_url_list(urls: List[str]) -> Tuple[List[str], List[str]]:
    """
    Validate a list of URLs.
    
    Args:
        urls: List of URLs to validate
        
    Returns:
        Tuple of (valid_urls, invalid_urls)
    """
    logger.debug(f"Validating {len(urls)} URLs")
    
    valid_urls = []
    invalid_urls = []
    
    for url in urls:
        url = url.strip()
        if not url:
            continue
            
        # Basic YouTube URL validation
        if any(domain in url.lower() for domain in ['youtube.com', 'youtu.be']):
            # Check if it contains a video ID pattern
            if re.search(r'(?:v=|youtu\.be/|shorts/)[\w-]+', url):
                valid_urls.append(url)
            else:
                invalid_urls.append(url)
        else:
            invalid_urls.append(url)
    
    logger.info(f"Validation complete: {len(valid_urls)} valid, {len(invalid_urls)} invalid")
    return valid_urls, invalid_urls


def deduplicate_urls(urls: List[str]) -> List[str]:
    """
    Remove duplicate URLs from list.
    
    Args:
        urls: List of URLs
        
    Returns:
        List with duplicates removed
    """
    seen = set()
    unique_urls = []
    
    for url in urls:
        # Extract video ID for comparison
        video_id = extract_video_id(url)
        if video_id and video_id not in seen:
            seen.add(video_id)
            unique_urls.append(url)
    
    logger.info(f"Deduplicated {len(urls)} URLs to {len(unique_urls)}")
    return unique_urls


def extract_video_id(url: str) -> str:
    """
    Extract video ID from YouTube URL.
    
    Args:
        url: YouTube URL
        
    Returns:
        Video ID or empty string if not found
    """
    patterns = [
        r'(?:v=|/)([0-9A-Za-z_-]{11}).*',
        r'youtu\.be/([0-9A-Za-z_-]{11})',
        r'shorts/([0-9A-Za-z_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return ""
