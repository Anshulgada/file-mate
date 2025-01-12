# file_mate/tests/test_info.py

import pytest
import os
from file_mate import info
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Create dummy image file
TEST_IMAGE = "test_image.png"
TEST_PDF = "test.pdf"


@pytest.fixture(scope="module", autouse=True)
def setup_teardown():
    """Set up the tests by creating dummy files"""
    img = Image.new("RGB", (60, 30), color="red")
    img.save(TEST_IMAGE)

    c = canvas.Canvas(TEST_PDF, pagesize=letter)
    width, height = letter
    c.drawString(100, height - 100, "test")
    c.save()

    yield
    os.remove(TEST_IMAGE)
    os.remove(TEST_PDF)


def test_get_file_info_image_success():
    file_info = info.get_file_info(TEST_IMAGE)
    assert "type" in file_info
    assert "size" in file_info
    assert "size_bytes" in file_info
    assert "dimensions" in file_info
    assert file_info["dimensions"] == "60x30"


def test_get_file_info_pdf_success():
    file_info = info.get_file_info(TEST_PDF)
    assert "type" in file_info
    assert "size" in file_info
    assert "size_bytes" in file_info
    assert "page_count" in file_info
    assert file_info["page_count"] == 1


def test_get_file_info_fail_file_not_found():
    with pytest.raises(FileNotFoundError):
        info.get_file_info("non_existent.txt")
