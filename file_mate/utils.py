# file_mate/utils.py

import os
import magic

def validate_file_exists(file_path):
    """Checks if a file exists at the specified path."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: File not found: {file_path}")

def get_file_type(file_path):
    """Uses libmagic to get a descriptive file type."""
    try:
        m = magic.Magic()
        return m.from_file(file_path)
    except Exception as e:
        raise RuntimeError(f"Error determining file type: {e}")

def validate_image_format(file_path):
    """Validates if the file is an image."""
    file_type = get_file_type(file_path)
    if "image" not in file_type.lower():
      raise ValueError(f"Error: File {file_path} is not an image")

def validate_pdf_format(file_path):
    """Validates if the file is a PDF"""
    file_type = get_file_type(file_path)
    if "pdf" not in file_type.lower():
      raise ValueError(f"Error: File {file_path} is not a pdf")


def validate_output_dir(output_path):
    """Checks if the output directory exists or create it"""
    directory = os.path.dirname(output_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)