"""Storage manager for download history."""

import json
import os
from typing import List, Dict, Any
from datetime import datetime
from utils.config import Config


class Storage:
    """Manages local storage for download history."""
    
    def __init__(self, history_file: str = None):
        """
        Initialize storage manager.
        
        Args:
            history_file: Path to history JSON file
        """
        self.history_file = history_file or Config.HISTORY_FILE
    
    def save_download(self, download_info: Dict[str, Any]) -> None:
        """
        Save a download to history.
        
        Args:
            download_info: Dictionary with download metadata
                - title: str
                - platform: str
                - quality: str (optional)
                - path: str
                - timestamp: str (optional, will be added if not present)
        """
        # Add timestamp if not present
        if 'timestamp' not in download_info:
            download_info['timestamp'] = datetime.now().isoformat()
        
        # Load existing history
        history = self.load_history()
        
        # Add new download at the beginning
        history.insert(0, download_info)
        
        # Keep only the most recent downloads
        history = history[:Config.MAX_RECENT_DOWNLOADS]
        
        # Save updated history
        self._write_history(history)
    
    def load_history(self) -> List[Dict[str, Any]]:
        """
        Load download history from file.
        
        Returns:
            List of download records, newest first
        """
        if not os.path.exists(self.history_file):
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def clear_history(self) -> None:
        """Clear all download history."""
        self._write_history([])
    
    def _write_history(self, history: List[Dict[str, Any]]) -> None:
        """Write history to file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save history: {e}")
