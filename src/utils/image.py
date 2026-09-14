"""
EZChart — image validation utilities.
"""

import io

from PIL import Image, UnidentifiedImageError

# Max image size: 5 MB (Telegram limit is 20 MB, but we're stricter)
MAX_IMAGE_SIZE: int = 5 * 1024 * 1024

# Min dimensions — smaller than this = thumbnail, not a chart
MIN_WIDTH: int = 200
MIN_HEIGHT: int = 200


def is_supported_image(image_bytes: bytes) -> bool:
    """
    Check whether the bytes are a valid, readable image
    with sufficient size to be a chart screenshot.
    """
    if not image_bytes:
        return False

    if len(image_bytes) > MAX_IMAGE_SIZE:
        return False

    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()  # verifies integrity without loading pixels
    except (UnidentifiedImageError, OSError, ValueError):
        return False

    # Re-open after verify() (verify closes the file)
    try:
        img = Image.open(io.BytesIO(image_bytes))
        width, height = img.size
    except Exception:
        return False

    if width < MIN_WIDTH or height < MIN_HEIGHT:
        return False

    return True