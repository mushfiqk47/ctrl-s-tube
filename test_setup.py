"""Test script to verify all imports and basic functionality."""

import sys

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        # Test core imports
        from core.router import URLRouter
        from core.controller import Controller
        from core.exceptions import MediaDownloaderException
        print("✓ Core modules imported successfully")
        
        # Test services imports
        from services.youtube_service import YouTubeService
        from services.spotify_service import SpotifyService
        from services.ffmpeg_processor import FFmpegProcessor
        print("✓ Services modules imported successfully")
        
        # Test utils imports
        from utils.config import Colors, Fonts, Config
        from utils.storage import Storage
        print("✓ Utils modules imported successfully")
        
        # Test UI imports
        from ui.main_window import MainWindow
        print("✓ UI modules imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_url_routing():
    """Test URL routing functionality."""
    print("\nTesting URL routing...")
    
    try:
        from core.router import URLRouter
        
        # Test YouTube URLs
        yt_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        platform = URLRouter.identify_platform(yt_url)
        assert platform == "youtube", f"Expected 'youtube', got '{platform}'"
        print(f"✓ YouTube URL correctly identified: {yt_url}")
        
        # Test Spotify URLs
        sp_url = "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT"
        platform = URLRouter.identify_platform(sp_url)
        assert platform == "spotify", f"Expected 'spotify', got '{platform}'"
        print(f"✓ Spotify URL correctly identified: {sp_url}")
        
        # Test invalid URL
        try:
            URLRouter.identify_platform("https://example.com")
            print("✗ Invalid URL should have raised exception")
            return False
        except:
            print("✓ Invalid URL correctly rejected")
        
        return True
    except Exception as e:
        print(f"✗ URL routing test failed: {e}")
        return False

def test_storage():
    """Test storage functionality."""
    print("\nTesting storage...")
    
    try:
        from utils.storage import Storage
        import os
        
        # Create test storage
        test_file = "test_history.json"
        storage = Storage(test_file)
        
        # Test saving and loading
        storage.save_download({
            'title': 'Test Video',
            'platform': 'youtube',
            'quality': '720p',
            'path': '/test/path.mkv'
        })
        
        history = storage.load_history()
        assert len(history) > 0, "History should contain at least one item"
        assert history[0]['title'] == 'Test Video'
        print("✓ Storage save/load works correctly")
        
        # Clean up
        storage.clear_history()
        if os.path.exists(test_file):
            os.remove(test_file)
        print("✓ Storage cleanup successful")
        
        return True
    except Exception as e:
        print(f"✗ Storage test failed: {e}")
        return False

def test_ffmpeg():
    """Test FFmpeg availability."""
    print("\nTesting FFmpeg...")
    
    try:
        from services.ffmpeg_processor import FFmpegProcessor
        
        available = FFmpegProcessor.check_ffmpeg_installed()
        if available:
            print("✓ FFmpeg is installed and available")
            return True
        else:
            print("✗ FFmpeg is not available in PATH")
            return False
    except Exception as e:
        print(f"✗ FFmpeg test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Media Downloader - System Verification")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("URL Routing", test_url_routing()))
    results.append(("Storage", test_storage()))
    results.append(("FFmpeg", test_ffmpeg()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("=" * 60)
    if all_passed:
        print("All tests passed! ✓")
        print("\nYou can now run the application with: python main.py")
        return 0
    else:
        print("Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
