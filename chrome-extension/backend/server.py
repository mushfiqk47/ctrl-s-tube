from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import logging
import os
import uuid
import time
from pathlib import Path
import threading

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Downloads directory
DOWNLOADS_DIR = Path(__file__).parent / 'downloads'
DOWNLOADS_DIR.mkdir(exist_ok=True)

# Store download info and progress
downloads = {}
progress_data = {}

def cleanup_old_files():
    """Clean up files older than 1 hour"""
    try:
        current_time = time.time()
        for file_path in DOWNLOADS_DIR.glob('*'):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > 3600:  # 1 hour
                    file_path.unlink()
                    logger.info(f"Cleaned up old file: {file_path.name}")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

def periodic_cleanup():
    """Run cleanup every 30 minutes"""
    while True:
        time.sleep(1800)  # 30 minutes
        cleanup_old_files()

# Start cleanup thread
cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
cleanup_thread.start()

def progress_hook(file_id):
    """Create a progress hook for yt-dlp"""
    def hook(d):
        status = d.get('status', 'unknown')
        
        if status == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            speed = d.get('speed', 0)
            eta = d.get('eta', 0)
            
            if total > 0:
                percent = (downloaded / total) * 100
            else:
                percent = 0
            
            # Format speed
            speed_str = f"{speed / 1024 / 1024:.2f} MB/s" if speed else "N/A"
            
            # Format downloaded/total
            downloaded_mb = downloaded / 1024 / 1024
            total_mb = total / 1024 / 1024
            
            progress_data[file_id] = {
                'status': 'downloading',
                'percent': round(percent, 1),
                'downloaded': f"{downloaded_mb:.1f} MB",
                'total': f"{total_mb:.1f} MB" if total > 0 else "Unknown",
                'speed': speed_str,
                'eta': f"{eta}s" if eta else "N/A",
                'message': f"Downloading: {percent:.1f}% at {speed_str}"
            }
            
        elif status == 'finished':
            progress_data[file_id] = {
                'status': 'processing',
                'percent': 95,
                'message': 'Download complete, processing video...'
            }
            
        elif status == 'error':
            progress_data[file_id] = {
                'status': 'error',
                'percent': 0,
                'message': 'Download failed'
            }
    
    return hook

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.json
        if not data or 'url' not in data:
            return jsonify({'error': 'Missing URL'}), 400

        video_url = data['url']
        download_type = data.get('type', 'video')
        quality = data.get('quality', 'highest')

        logger.info(f"Received request: URL={video_url}, Type={download_type}, Quality={quality}")

        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Initialize progress
        progress_data[file_id] = {
            'status': 'starting',
            'percent': 0,
            'message': 'Initializing download...'
        }
        
        # Configure yt-dlp options
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'outtmpl': str(DOWNLOADS_DIR / f'{file_id}.%(ext)s'),
            'progress_hooks': [progress_hook(file_id)],
        }

        # Configure format based on type and quality
        if download_type == 'audio':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }]
        else:
            # For video, merge video+audio and output as MKV
            if quality == 'highest':
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
            elif quality in ['2160', '1440', '1080', '720', '480', '360']:
                ydl_opts['format'] = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best'
            else:
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
            
            # Merge into MKV format
            ydl_opts['merge_output_format'] = 'mkv'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mkv',
            }]

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            title = info.get('title', 'video')
            
            # Find the downloaded file
            if download_type == 'audio':
                file_path = DOWNLOADS_DIR / f'{file_id}.m4a'
                if not file_path.exists():
                    # Try other audio formats
                    for ext in ['mp3', 'webm', 'opus']:
                        file_path = DOWNLOADS_DIR / f'{file_id}.{ext}'
                        if file_path.exists():
                            break
                filename = f"{title}.m4a"
            else:
                file_path = DOWNLOADS_DIR / f'{file_id}.mkv'
                if not file_path.exists():
                    # Check if it exists with different extension
                    for ext in ['mp4', 'webm']:
                        file_path = DOWNLOADS_DIR / f'{file_id}.{ext}'
                        if file_path.exists():
                            break
                filename = f"{title}.mkv"
            
            if not file_path.exists():
                logger.error(f"Downloaded file not found: {file_path}")
                logger.error(f"Directory contents: {list(DOWNLOADS_DIR.glob('*'))}")
                progress_data[file_id] = {
                    'status': 'error',
                    'percent': 0,
                    'message': 'Downloaded file not found'
                }
                return jsonify({'error': 'Downloaded file not found'}), 500

            # Store download info
            downloads[file_id] = {
                'path': str(file_path),
                'filename': filename,
                'title': title
            }
            
            # Update progress to complete
            progress_data[file_id] = {
                'status': 'complete',
                'percent': 100,
                'message': 'Download complete!'
            }

            logger.info(f"Download complete: {filename} -> {file_path}")

            return jsonify({
                'success': True,
                'file_id': file_id,
                'filename': filename,
                'title': title
            })

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        if 'file_id' in locals():
            progress_data[file_id] = {
                'status': 'error',
                'percent': 0,
                'message': f'Error: {str(e)}'
            }
        return jsonify({'error': str(e)}), 500

@app.route('/progress/<file_id>', methods=['GET'])
def get_progress(file_id):
    """Get download progress for a specific file"""
    try:
        if file_id in progress_data:
            return jsonify(progress_data[file_id])
        else:
            return jsonify({
                'status': 'unknown',
                'percent': 0,
                'message': 'No progress data available'
            })
    except Exception as e:
        logger.error(f"Error getting progress: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/file/<file_id>', methods=['GET'])
def get_file(file_id):
    try:
        if file_id not in downloads:
            return jsonify({'error': 'File not found'}), 404

        download_info = downloads[file_id]
        file_path = download_info['path']
        filename = download_info['filename']

        if not os.path.exists(file_path):
            return jsonify({'error': 'File does not exist'}), 404

        # Send file and schedule deletion after sending
        response = send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )

        # Clean up download info and progress
        del downloads[file_id]
        if file_id in progress_data:
            del progress_data[file_id]

        return response

    except Exception as e:
        logger.error(f"Error serving file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Ctrl+S Tube Backend is running'})

if __name__ == '__main__':
    import os
    
    # Get port from environment (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    
    # Determine if running in production
    is_production = os.environ.get('RENDER', False)
    
    print("Starting Ctrl+S Tube Backend Server...")
    print(f"Environment: {'Production (Render)' if is_production else 'Development (Local)'}")
    print(f"Listening on port: {port}")
    print(f"Downloads directory: {DOWNLOADS_DIR}")
    
    # In production (Render), bind to 0.0.0.0
    # In development, use localhost for security
    host = '0.0.0.0' if is_production else 'localhost'
    debug = not is_production
    
    app.run(host=host, port=port, debug=debug)
