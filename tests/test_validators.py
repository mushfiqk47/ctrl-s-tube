"""Unit tests for validators."""

import pytest
from pathlib import Path
from utils.validators import URLValidator, PathValidator, QualityValidator
from core.exceptions import InvalidURLException


class TestURLValidator:
    """Tests for URL validation."""
    
    def test_valid_youtube_watch_url(self):
        """Test valid YouTube watch URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = URLValidator.validate_youtube_url(url)
        assert result == url
    
    def test_valid_youtube_short_url(self):
        """Test valid YouTube short URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        result = URLValidator.validate_youtube_url(url)
        assert result == url
    
    def test_valid_youtube_playlist(self):
        """Test valid YouTube playlist URL."""
        url = "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        result = URLValidator.validate_youtube_url(url)
        assert result == url
    
    def test_invalid_url_empty(self):
        """Test empty URL raises exception."""
        with pytest.raises(InvalidURLException):
            URLValidator.validate_youtube_url("")
    
    def test_invalid_url_non_youtube(self):
        """Test non-YouTube URL raises exception."""
        with pytest.raises(InvalidURLException):
            URLValidator.validate_youtube_url("https://www.google.com")
    
    def test_url_with_whitespace(self):
        """Test URL with leading/trailing whitespace."""
        url = "  https://www.youtube.com/watch?v=dQw4w9WgXcQ  "
        result = URLValidator.validate_youtube_url(url)
        assert result == url.strip()


class TestPathValidator:
    """Tests for path validation."""
    
    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization."""
        filename = "My Video File.mp4"
        result = PathValidator.sanitize_filename(filename)
        assert result == "My Video File.mp4"
    
    def test_sanitize_filename_invalid_chars(self):
        """Test filename with invalid characters."""
        filename = "My<Video>File:Name|Test?.mp4"
        result = PathValidator.sanitize_filename(filename)
        assert result == "My_Video_File_Name_Test_.mp4"
    
    def test_sanitize_filename_empty(self):
        """Test empty filename."""
        result = PathValidator.sanitize_filename("")
        assert result == "download"
    
    def test_sanitize_filename_long(self):
        """Test very long filename gets  truncated."""
        filename = "a" * 300 + ".mp4"
        result = PathValidator.sanitize_filename(filename)
        assert len(result) <= 200


class TestQualityValidator:
    """Tests for quality validation."""
    
    def test_valid_quality_standard(self):
        """Test standard quality format."""
        qual = "1080p"
        result = QualityValidator.validate_quality(qual)
        assert result == qual
    
    def test_valid_quality_high_fps(self):
        """Test high FPS quality format."""
        qual = "1080p60"
        result = QualityValidator.validate_quality(qual)
        assert result == qual
    
    def test_valid_quality_4k(self):
        """Test 4K quality format."""
        qual = "4K (2160p)"
        result = QualityValidator.validate_quality(qual)
        assert result == qual
    
    def test_valid_quality_audio(self):
        """Test audio quality format."""
        qual = "Audio Only"
        result = QualityValidator.validate_quality(qual)
        assert result == qual
    
    def test_invalid_quality(self):
        """Test invalid quality format."""
        with pytest.raises(ValueError):
            QualityValidator.validate_quality("invalid_quality")
