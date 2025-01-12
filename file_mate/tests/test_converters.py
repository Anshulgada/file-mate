# file_mate/tests/test_converters.py
import pytest
import os
from file_mate import converters
from PIL import Image
from reportlab.pdfgen import canvas  # Add this line
from reportlab.lib.pagesizes import letter
from pathlib import Path

# Create dummy image files
TEST_IMAGE = "test_image.png"
TEST_PDF = "test.pdf"
TEST_IMG_PDF = "test_img_pdf.pdf"
TEST_MERGED_PDF = "merged.pdf"
TEST_DIR = Path("test_dir")


@pytest.fixture(scope="module", autouse=True)
def setup_teardown():
    """Set up the tests by creating dummy files"""
    img = Image.new('RGB', (60, 30), color='red')
    img.save(TEST_IMAGE)

    # Create PDF with an embedded image
    c = canvas.Canvas(TEST_PDF, pagesize=letter)
    width, height = letter
    c.drawImage(TEST_IMAGE, 0, 0, width=width / 2, height=height / 2)  # Embed the image
    c.save()

    # Create another PDF for merging
    c = canvas.Canvas(TEST_IMG_PDF, pagesize=letter)
    c.drawImage(TEST_IMAGE, 0, 0, width=width, height=height)
    c.save()

    os.makedirs(TEST_DIR, exist_ok=True)

    yield

    os.remove(TEST_IMAGE)
    os.remove(TEST_PDF)
    os.remove(TEST_IMG_PDF)
    os.remove(TEST_MERGED_PDF) if os.path.exists(TEST_MERGED_PDF) else None
    os.rmdir(TEST_DIR)

    #Remove directory with content
    def remove_directory(path):
         for item in os.listdir(path):
             item_path = os.path.join(path,item)
             if os.path.isfile(item_path):
                 os.remove(item_path)
             elif os.path.isdir(item_path):
                   remove_directory(item_path)
         os.rmdir(path)

    remove_directory(TEST_DIR) if os.path.exists(TEST_DIR) else None


def test_convert_image_success():
    output_file = "converted_image.jpg"
    converters.convert_image(
        TEST_IMAGE, output_file, "jpeg"
    )  # changed from jpg to jpeg
    assert os.path.exists(output_file)
    os.remove(output_file)

    target_format = "jpeg"
    if target_format:
        target_format = target_format.lower()  # Add this line


def test_convert_image_fail_file_not_found():
    with pytest.raises(FileNotFoundError):
        converters.convert_image("not_exists.png", "out.png")


def test_convert_image_fail_invalid_image():
    with pytest.raises(ValueError):
        converters.convert_image(TEST_PDF, "out.png")


def test_convert_image_fail_invalid_format():
    with pytest.raises(RuntimeError):
        output_file = "converted_image.invalid"
        converters.convert_image(TEST_IMAGE, output_file)


def test_convert_image_to_pdf_success():
    output_file = "converted_image.pdf"
    converters.convert_image_to_pdf(TEST_IMAGE, output_file)
    assert os.path.exists(output_file)
    os.remove(output_file)


def test_convert_image_to_pdf_fail_file_not_found():
    with pytest.raises(FileNotFoundError):
        converters.convert_image_to_pdf("not_exists.png", "out.pdf")


def test_convert_image_to_pdf_fail_invalid_image():
    with pytest.raises(ValueError):
        converters.convert_image_to_pdf(TEST_PDF, "out.pdf")


def test_convert_pdf_to_images_success():
    output_dir = TEST_DIR / "pdf_to_images"
    converters.convert_pdf_to_images(TEST_PDF, output_dir)
    assert len(os.listdir(output_dir)) > 0  # Ensure at least one image is created
    for file in os.listdir(output_dir):
        os.remove(output_dir / file)
    os.rmdir(output_dir)


def test_convert_pdf_to_images_fail_file_not_found():
    with pytest.raises(FileNotFoundError):
        converters.convert_pdf_to_images("not_exists.pdf", "test_dir")


def test_convert_pdf_to_images_fail_invalid_pdf():
    with pytest.raises(ValueError):
        converters.convert_pdf_to_images(TEST_IMAGE, "test_dir")


def test_merge_pdf_success():
    output_file = TEST_MERGED_PDF
    converters.merge_pdf([TEST_PDF, TEST_IMG_PDF], output_file)
    assert os.path.exists(output_file)


def test_merge_pdf_fail_file_not_found():
    with pytest.raises(FileNotFoundError):
        converters.merge_pdf(["test1.pdf", "test2.pdf"], "merged_out.pdf")


def test_merge_pdf_fail_invalid_pdf():
    with pytest.raises(ValueError):
        converters.merge_pdf([TEST_IMAGE, TEST_PDF], "merged_out.pdf")
