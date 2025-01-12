# file_mate/info.py

import os
from file_mate.utils import validate_file_exists, get_file_type
from PIL import Image
from pypdf import PdfReader


def get_file_info(file_path):
    """Extracts basic file info such as type, size etc

    Args:
        file_path (str): The path of the input file.

    Returns:
        dict: File info dictionary.
    """
    validate_file_exists(file_path)
    file_type = get_file_type(file_path)

    file_size = os.path.getsize(file_path)
    info = {
        "type": file_type,
        "size_bytes": file_size,
        "size": format_file_size(file_size),
    }
    if "image" in file_type.lower():
        try:
            img = Image.open(file_path)
            info["dimensions"] = f"{img.width}x{img.height}"
        except Exception as e:
            info["dimensions"] = "N/A"
    elif "pdf" in file_type.lower():
        try:
            pdf = PdfReader(file_path)
            info["page_count"] = len(pdf.pages)
        except Exception as e:
            info["page_count"] = "N/A"

    return info


def format_file_size(size_bytes):
    """Formats bytes to a human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
