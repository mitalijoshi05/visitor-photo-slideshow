import uuid
from io import BytesIO
from PIL import Image, ImageOps, UnidentifiedImageError

from app.config import (
    ALLOWED_FORMATS,
    MAX_FILE_SIZE_BYTES,
    MAX_IMAGE_DIMENSION,
    UPLOAD_DIR,
)


class ImageError(Exception):
    """Photo me koi problem ho to ye error uthega."""


def validate_and_save(data: bytes) -> str:
    """Photo check karke save karta hai. Naya filename return karta hai."""
    if len(data) == 0:
        raise ImageError("Empty file.")
    if len(data) > MAX_FILE_SIZE_BYTES:
        raise ImageError("File is too large.")

    try:
        img = Image.open(BytesIO(data))
        img.verify()  # file asli image hai ya nahi
        img = Image.open(BytesIO(data))  # verify ke baad dobara kholna padta hai
    except (UnidentifiedImageError, OSError):
        raise ImageError("File is not a valid image.")

    if img.format not in ALLOWED_FORMATS:
        raise ImageError("Only JPG, PNG and WebP images are allowed.")

    # Phone photos ka rotation theek karo, phir resize karo
    img = ImageOps.exif_transpose(img)
    img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION))

    # Naya random naam: user ka diya hua filename kabhi use nahi karte
    filename = uuid.uuid4().hex + ".jpg"
    UPLOAD_DIR.mkdir(exist_ok=True)

    # JPEG me save = EXIF (GPS location waghera) hat jata hai
    img.convert("RGB").save(UPLOAD_DIR / filename, "JPEG", quality=85)
    return filename