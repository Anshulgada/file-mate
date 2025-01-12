# file_mate/tests/test_manipulators.py
import pytest
import os
from file_mate import manipulators
from PIL import Image
from reportlab.pdfgen import canvas  # Add this import
from reportlab.lib.pagesizes import letter

# Create dummy image file
TEST_IMAGE = "test_image.png"
TEST_PDF = "test.pdf"  # New test pdf
TEST_ROTATED_IMAGE = "rotated_image.png"
TEST_RESIZED_IMAGE = "resized_image.png"
TEST_GRAY_IMAGE = "gray_image.png"


@pytest.fixture(scope="module", autouse=True)
def setup_teardown():
    """Set up the tests by creating dummy files"""
    with Image.new("RGB", (60, 30), color="red") as img:
        img.save(TEST_IMAGE)
    # No need for img.close() as the context manager handles it

    c = canvas.Canvas(TEST_PDF, pagesize=letter)  # New pdf object
    c.drawString(100, 100, "Test")  # Dummy text
    c.save()

    yield

    # Ensure files are removed
    for file in [TEST_IMAGE, TEST_PDF, TEST_ROTATED_IMAGE, TEST_RESIZED_IMAGE, TEST_GRAY_IMAGE]:
        if os.path.exists(file):
            os.remove(file)


def test_resize_image_success_with_scale():
    output_file = TEST_RESIZED_IMAGE
    manipulators.resize_image(TEST_IMAGE, output_file, scale=0.5)
    assert os.path.exists(output_file)
    with Image.open(output_file) as img:
       assert img.size == (30, 15)


def test_resize_image_success_with_width_and_height():
    output_file = TEST_RESIZED_IMAGE
    manipulators.resize_image(TEST_IMAGE, output_file, width=100, height=200)
    assert os.path.exists(output_file)
    with Image.open(output_file) as img:
        assert img.size == (100, 200)


def test_resize_image_fail_file_not_found():
    with pytest.raises(FileNotFoundError):
        manipulators.resize_image("not_exists.png", "out.png", width=200, height=100)


def test_resize_image_fail_invalid_image():
    with pytest.raises(ValueError):
        manipulators.resize_image(TEST_PDF, "out.png", width=100, height=200)


def test_resize_image_fail_no_resize_options():
    with pytest.raises(ValueError):  # Changed
        manipulators.resize_image(TEST_IMAGE, "out.png")


def test_rotate_image_success():
    output_file = TEST_ROTATED_IMAGE
    manipulators.rotate_image(TEST_IMAGE, output_file, degrees=90)
    assert os.path.exists(output_file)
    with Image.open(output_file) as img:
        assert img.size == (30, 60)


def test_rotate_image_fail_file_not_found():
    with pytest.raises(FileNotFoundError):
        manipulators.rotate_image("not_exists.png", "out.png", degrees=90)


def test_rotate_image_fail_invalid_image():
    with pytest.raises(ValueError):
        manipulators.rotate_image(TEST_PDF, "out.png", degrees=90)


def test_rotate_image_fail_invalid_degree():
    with pytest.raises(ValueError, match="Error: Rotation must be one of 90, 180 or 270. Got 45"):
        manipulators.rotate_image(TEST_IMAGE, "out.png", degrees=45)


def test_grayscale_image_success():
    output_file = TEST_GRAY_IMAGE
    manipulators.grayscale_image(TEST_IMAGE, output_file)
    assert os.path.exists(output_file)


def test_grayscale_image_fail_file_not_found():
    with pytest.raises(FileNotFoundError):
        manipulators.grayscale_image("not_exists.png", "out.png")


def test_grayscale_image_fail_invalid_image():
    with pytest.raises(ValueError):
        manipulators.grayscale_image(TEST_PDF, "out.png")
