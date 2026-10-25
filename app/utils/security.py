"""Security and safe file-handling utilities for Smart Agriculture Agent.

Enforces upload size caps, safe filename generation, directory traversal prevention,
and deep image file content validation using Pillow.
"""

import os
import re
import uuid
from pathlib import Path
from typing import Set, Tuple
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename


def allowed_file(filename: str, allowed_extensions: Set[str]) -> bool:
    """Check if the provided filename has an approved extension.

    Args:
        filename: Uploaded file name.
        allowed_extensions: Set of permitted lowercase extensions (e.g., {'jpg', 'jpeg', 'png'}).

    Returns:
        True if extension is valid, False otherwise.
    """
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in allowed_extensions


def generate_safe_filename(original_filename: str) -> str:
    """Generate a sanitized, unique filename to prevent overwrites and directory traversal.

    Args:
        original_filename: User-supplied filename.

    Returns:
        Sanitized filename with UUID prefix and verified extension.
    """
    clean_name = secure_filename(original_filename)
    # Remove any potential path traversal sequences remaining
    clean_name = re.sub(r"[\\/]", "", clean_name)
    ext = clean_name.rsplit(".", 1)[1].lower() if "." in clean_name else "png"
    unique_prefix = uuid.uuid4().hex[:12]
    return f"leaf_{unique_prefix}.{ext}"


def verify_image_integrity(file_path: Path) -> Tuple[bool, str]:
    """Verify that a saved image file is a non-corrupt, valid visual image.

    Opens the file with Pillow, calls .verify(), checks dimensions, and confirms format.

    Args:
        file_path: Absolute or relative path to the image file.

    Returns:
        Tuple of (is_valid: bool, error_message: str).
    """
    if not file_path.exists():
        return False, "Uploaded image file does not exist on disk."

    if file_path.stat().st_size == 0:
        return False, "Uploaded image is empty (0 bytes)."

    try:
        with Image.open(file_path) as img:
            # Check format
            img_format = (img.format or "").upper()
            if img_format not in {"JPEG", "JPG", "PNG"}:
                return False, f"Unsupported image format: {img_format}. Allowed: JPEG, PNG."

            # Verify image integrity
            img.verify()

        # Re-open to verify raster loading (verify() invalidates file handle)
        with Image.open(file_path) as img:
            img.load()
            width, height = img.size
            if width < 32 or height < 32:
                return False, f"Image dimensions too small ({width}x{height}). Minimum 32x32 required."
            if width > 6000 or height > 6000:
                return False, f"Image dimensions excessively large ({width}x{height}). Maximum 6000x6000."

        return True, ""
    except UnidentifiedImageError:
        return False, "File is not a recognized image or is severely corrupt."
    except Exception as exc:
        return False, f"Image verification failed: {str(exc)}"


def cleanup_temporary_file(file_path: Path) -> None:
    """Safely remove a temporary image file after processing if required."""
    try:
        if file_path.exists():
            os.remove(file_path)
    except Exception:
        pass
