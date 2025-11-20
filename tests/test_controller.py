"""Unit tests for Controller with mocking."""

import pytest
from unittest.mock import Mock, MagicMock
from core.controller import Controller
from core.exceptions import InvalidURLException, FetchException, DownloadException
from core.types import VideoMetadata


class TestController:
    """Tests for Controller with dependency injection."""
    
    def test_controller_initialization_default(self):
        """Test controller initializes with default services."""
        controller = Controller()
        assert controller.metadata_service is not None
        assert controller.download_service is not None
    
    def test_controller_initialization_with_di(self):
        """Test controller initializes with injected services."""
        mock_metadata = Mock()
        mock_download = Mock()
        
        controller = Controller(
            metadata_service=mock_metadata,
            download_service=mock_download
        )
        
        assert controller.metadata_service == mock_metadata
        assert controller.download_service == mock_download
    
    def test_fetch_metadata_success(self):
        """Test successful metadata fetch."""
        mock_metadata_service = Mock()
        mock_metadata_service.fetch_metadata.return_value = VideoMetadata(
            platform="youtube",
            type="video",
            title="Test Video",
            duration=120,
            thumbnail="https://example.com/thumb.jpg",
            formats=[],
            count=None
        )
        
        controller = Controller(metadata_service=mock_metadata_service)
        result = controller.fetch_metadata("https://www.youtube.com/watch?v=test123")
        
        assert result['title'] == "Test Video"
        assert result['platform'] == "youtube"
        mock_metadata_service.fetch_metadata.assert_called_once()
    
    def test_fetch_metadata_invalid_url(self):
        """Test metadata fetch with invalid URL."""
        controller = Controller()
        
        with pytest.raises(InvalidURLException):
            controller.fetch_metadata("https://www.google.com")
    
    def test_download_success(self):
        """Test successful download."""
        mock_download_service = Mock()
        mock_download_service.download.return_value = "/path/to/video.mkv"
        
        controller = Controller(download_service=mock_download_service)
        result = controller.download(
            "https://www.youtube.com/watch?v=test123",
            "C:\\Downloads",
            "1080p"
        )
        
        assert result == "/path/to/video.mkv"
        mock_download_service.download.assert_called_once()
    
    def test_download_invalid_url(self):
        """Test download with invalid URL."""
        controller = Controller()
        
        with pytest.raises(InvalidURLException):
            controller.download("invalid_url", "C:\\Downloads")
