# file_mate/converters.py

from PIL import Image
from file_mate.utils import (
    validate_file_exists,
    validate_image_format,
    validate_output_dir,
)
import os
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch


def convert_image(input_file, output_file, target_format=None, quality=100):
    """Converts an image to a specified format.

    Args:
       input_file (str): The path of the input file.
       output_file (str): The path of the output file.
       target_format (str, optional): The target image format. Defaults to None.
       quality (int, optional): The quality of output image (0-100). Defaults to 100.
    """
    validate_file_exists(input_file)
    validate_image_format(input_file)
    validate_output_dir(output_file)

    if not target_format:
        target_format = os.path.splitext(output_file)[1][1:].lower()

    try:
        img = Image.open(input_file)
        img.save(output_file, format=target_format, quality=quality)

    except Exception as e:
        raise RuntimeError(f"Error converting image: {e}")


def convert_image_to_pdf(input_file, output_file):
    """Converts an image to a pdf

    Args:
        input_file (str): The path of the input file.
        output_file (str): The path of the output file.
    """
    validate_file_exists(input_file)
    validate_image_format(input_file)
    validate_output_dir(output_file)

    try:
        img = Image.open(input_file)
        c = canvas.Canvas(output_file, pagesize=letter)
        width, height = letter
        img_width, img_height = img.size

        # Calculate the position and size of the image to fit within the page.
        if (img_width > width or img_height > height):
            # Scale the image to fit within page limits while maintaining aspect ratio
            img_aspect_ratio = img_width / img_height
            page_aspect_ratio = width / height

            if img_aspect_ratio > page_aspect_ratio:
                new_width = width - (2 * 0.5 * inch)  # Subtract 0.5 inch padding from each side
                new_height = new_width / img_aspect_ratio
            else:
                new_height = height - (2 * 0.5 * inch)
                new_width = new_height * img_aspect_ratio

            x = (width - new_width) / 2
            y = (height - new_height) / 2
            c.drawImage(input_file, x, y, width=new_width, height=new_height)
        else:
            x = (width - img_width) / 2
            y = (height - img_height) / 2
            c.drawImage(input_file, x, y, width=img_width, height=img_height)

        c.save()
    except Exception as e:
        raise RuntimeError(f"Error converting image to PDF: {e}")


def convert_pdf_to_images(input_pdf, output_dir, target_format="png"):
    """Converts a PDF to series of images

    Args:
        input_pdf (str): The path of the input PDF file.
        output_dir (str): The output directory path to save the images
        target_format (str, optional): The target image format for the output images. Default is png.
    """
    validate_file_exists(input_pdf)
    from file_mate.utils import validate_pdf_format

    validate_pdf_format(input_pdf)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        images = []
        pdf = PdfReader(input_pdf)
        num_pages = len(pdf.pages)

        for i in range(num_pages):
            page = pdf.pages[i]
            if not page.images:
                continue  # Skip pages without images
            try:
                image = page.images[0]
                img_file = os.path.join(output_dir, f"page_{i+1}.{target_format}")
                with open(img_file, "wb") as f:
                    f.write(image.data)
                images.append(img_file)
            except IndexError:
                continue  # Skip pages without images
        if not images:
            raise RuntimeError("No images found in the PDF.")
    except Exception as e:
        raise RuntimeError(f"Error converting pdf to images: {e}")


def merge_pdf(input_pdfs, output_pdf):
    """Merges the input PDFs to an output PDF

    Args:
        input_pdfs (list): List of paths for the input PDF
        output_pdf (str): Output file path
    """

    for input_pdf in input_pdfs:
        validate_file_exists(input_pdf)
        from file_mate.utils import validate_pdf_format

        validate_pdf_format(input_pdf)

    validate_output_dir(output_pdf)
    merger = PdfWriter()

    try:
        for pdf_file in input_pdfs:
            merger.append(pdf_file)
        merger.write(output_pdf)
        merger.close()
    except Exception as e:
        raise RuntimeError(f"Error merging pdfs: {e}")
