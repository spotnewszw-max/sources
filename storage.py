import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
PROCESSED_DIR = BASE_DIR / "processed"
CACHE_DIR = BASE_DIR / "cache"

# Create directories
for directory in [UPLOAD_DIR, PROCESSED_DIR, CACHE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# File type configurations
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
ALLOWED_AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.ogg'}
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv'}
ALLOWED_DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt'}

MAX_FILE_SIZE_MB = 100  # Maximum file size

def get_upload_path(user_id: int, filename: str) -> Path:
    """Generate upload path for a file"""
    user_dir = UPLOAD_DIR / str(user_id)
    user_dir.mkdir(exist_ok=True)
    return user_dir / filename