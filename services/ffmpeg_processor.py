"""FFmpeg processor for media operations."""

import subprocess
import os
from pathlib import Path
from core.exceptions import FFmpegException


class FFmpegProcessor:
    """Handles FFmpeg operations for media processing."""
    
    @staticmethod
    def check_ffmpeg_installed() -> bool:
        """
        Check if FFmpeg is installed and available in PATH.
        
        Returns:
            True if FFmpeg is available, False otherwise
        """
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    @staticmethod
    def merge_video_audio(
        video_path: str,
        audio_path: str,
        output_path: str
    ) -> str:
        """
        Merge video and audio files using FFmpeg.
        
        Args:
            video_path: Path to video file
            audio_path: Path to audio file
            output_path: Path for merged output file
            
        Returns:
            Path to merged file
            
        Raises:
            FFmpegException: If merge operation fails
        """
        try:
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-strict", "experimental",
                output_path,
                "-y"  # Overwrite without asking
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise FFmpegException(f"FFmpeg merge failed: {result.stderr}")
            
            # Clean up temporary files
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            return output_path
            
        except Exception as e:
            raise FFmpegException(f"Merge operation failed: {str(e)}")
    
    @staticmethod
    def embed_metadata(
        audio_path: str,
        title: str,
        artist: str,
        album: str = "",
        cover_path: str = None
    ) -> str:
        """
        Embed metadata into audio file using mutagen.
        
        Args:
            audio_path: Path to audio file
            title: Track title
            artist: Artist name
            album: Album name (optional)
            cover_path: Path to cover image (optional)
            
        Returns:
            Path to file with embedded metadata
            
        Raises:
            FFmpegException: If metadata embedding fails
        """
        try:
            from mutagen.mp3 import MP3
            from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC
            
            # Load the file
            audio = MP3(audio_path, ID3=ID3)
            
            # Add ID3 tags if they don't exist
            try:
                audio.add_tags()
            except Exception:
                # Tags already exist, ignore
                pass
            
            # Set metadata
            audio.tags["TIT2"] = TIT2(encoding=3, text=title)
            audio.tags["TPE1"] = TPE1(encoding=3, text=artist)
            
            if album:
                audio.tags["TALB"] = TALB(encoding=3, text=album)
            
            # Add cover art if provided
            if cover_path and os.path.exists(cover_path):
                with open(cover_path, 'rb') as img:
                    audio.tags["APIC"] = APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,
                        desc='Cover',
                        data=img.read()
                    )
            
            audio.save()
            return audio_path
            
        except Exception as e:
            raise FFmpegException(f"Metadata embedding failed: {str(e)}")
