# file_mate/cli.py


import click
from file_mate.converters import (
    convert_image,
    convert_image_to_pdf,
    convert_pdf_to_images,
    merge_pdf,
)
from file_mate.info import get_file_info
from file_mate.manipulators import resize_image, rotate_image, grayscale_image


@click.group()
def cli():
    """Filemate is a command-line tool for image, pdf, and other file manipulations."""
    pass


@cli.group()
def convert():
    """Convert files between formats"""
    pass


@convert.command("image")
@click.argument("input_file")
@click.argument("output_file")
@click.option("--format", help="Target image format.")
@click.option("--quality", type=int, default=95, help="Image quality (0-100).")
def convert_image_cli(input_file, output_file, format, quality):
    """Converts an image to another format."""
    try:
        convert_image(input_file, output_file, format, quality)
        click.echo(f"Converted {input_file} to {output_file}")
    except Exception as e:
        click.echo(f"Error: {e}")


@convert.command("image-to-pdf")
@click.argument("input_file")
@click.argument("output_file")
def convert_image_to_pdf_cli(input_file, output_file):
    """Converts an image to a PDF."""
    try:
        convert_image_to_pdf(input_file, output_file)
        click.echo(f"Converted {input_file} to {output_file}")
    except Exception as e:
        click.echo(f"Error: {e}")


@convert.command("pdf-to-images")
@click.argument("input_pdf")
@click.argument("output_dir")
@click.option("--format", default="png", help="Target image format.")
def convert_pdf_to_images_cli(input_pdf, output_dir, format):
    """Converts a PDF to a series of images"""
    try:
        convert_pdf_to_images(input_pdf, output_dir, format)
        click.echo(f"Converted {input_pdf} to images in {output_dir}")
    except Exception as e:
        click.echo(f"Error: {e}")


@convert.command("merge-pdf")
@click.argument("input_pdfs", nargs=-1, type=click.Path(exists=True))
@click.argument("output_pdf")
def merge_pdf_cli(input_pdfs, output_pdf):
    """Merges the given input pdfs into an output pdf"""
    try:
        merge_pdf(input_pdfs, output_pdf)
        click.echo(f"Merged {input_pdfs} into {output_pdf}")
    except Exception as e:
        click.echo(f"Error: {e}")


@cli.group()
def manip():
    """Manipulate files"""
    pass


@manip.command("resize")
@click.argument("input_file")
@click.argument("output_file")
@click.option("--width", type=int, help="Target image width in pixels.")
@click.option("--height", type=int, help="Target image height in pixels.")
@click.option("--scale", type=float, help="Scale the image by this factor (0-1).")
def resize_image_cli(input_file, output_file, width, height, scale):
    """Resize image with scale or height and width"""
    try:
        resize_image(input_file, output_file, width, height, scale)
        click.echo(f"Resized {input_file} to {output_file}")
    except Exception as e:
        click.echo(f"Error: {e}")


@manip.command("rotate")
@click.argument("input_file")
@click.argument("output_file")
@click.option("--degrees", type=int, help="Rotate image by 90, 180 or 270 degrees")
def rotate_image_cli(input_file, output_file, degrees):
    """Rotate image by given degrees (90, 180, 270)"""
    try:
        rotate_image(input_file, output_file, degrees)
        click.echo(f"Rotated {input_file} to {output_file}")
    except Exception as e:
        click.echo(f"Error: {e}")


@manip.command("grayscale")
@click.argument("input_file")
@click.argument("output_file")
def grayscale_image_cli(input_file, output_file):
    """Convert image to grayscale"""
    try:
        grayscale_image(input_file, output_file)
        click.echo(f"Converted {input_file} to grayscale {output_file}")
    except Exception as e:
        click.echo(f"Error: {e}")


@cli.command()
@click.argument("file_path")
def info(file_path):
    """Displays info for a given file."""
    try:
        file_info = get_file_info(file_path)
        click.echo(f"File Info: \n{file_info}")
    except Exception as e:
        click.echo(f"Error: {e}")


if __name__ == "__main__":
    cli()
