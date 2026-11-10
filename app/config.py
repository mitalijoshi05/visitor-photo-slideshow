import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "5"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_FILES_PER_UPLOAD = 5
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_IMAGE_DIMENSION = 1920
