# file_mate/manipulators.py

from PIL import Image
from file_mate.utils import (
    validate_file_exists,
    validate_image_format,
    validate_output_dir,
)


def resize_image(input_file, output_file, width=None, height=None, scale=None):
    """Resizes an image to a specified width, height or scale

    Args:
         input_file (str): The input image file path
         output_file (str): The output image file path
         width (int, optional): The target image width in pixels. Defaults to None.
         height (int, optional): The target image height in pixels. Defaults to None.
         scale (float, optional): The scale factor to apply on the image (0-1) . Defaults to None.
    """

    validate_file_exists(input_file)
    validate_image_format(input_file)
    validate_output_dir(output_file)

    try:
        img = Image.open(input_file)
    except Exception as e:
        raise ValueError(f"Invalid image file: {e}")

    if scale:
        new_width = int(img.width * scale)
        new_height = int(img.height * scale)
    elif width and height:
        new_width = width
        new_height = height
    else:
        raise ValueError(
            f"Error: Either 'scale' or both 'width' and 'height' must be specified"
        )

    try:
        img = img.resize((new_width, new_height))
        img.save(output_file)
        img.close()  # Ensure the image file is closed
    except Exception as e:
        raise RuntimeError(f"Error resizing image: {e}")


def rotate_image(input_file, output_file, degrees):
    """Rotates an image by 90, 180 or 270 degrees.

    Args:
      input_file (str): The input image file path
      output_file (str): The output image file path
      degrees (int): The rotation amount in degrees. (90, 180, 270)
    """
    validate_file_exists(input_file)
    validate_image_format(input_file)
    validate_output_dir(output_file)

    try:
        img = Image.open(input_file)
        if degrees not in [90, 180, 270]:
            img.close()
            raise ValueError(
                f"Error: Rotation must be one of 90, 180 or 270. Got {degrees}"
            )
        rotated_img = img.rotate(-degrees, expand=True)
        rotated_img.save(output_file)
        img.close()
    except ValueError as e:
        raise e
    except Exception as e:
        raise RuntimeError(f"Error rotating image: {e}")


def grayscale_image(input_file, output_file):
    """Converts image to grayscale

    Args:
        input_file (str): The input image file path
        output_file (str): The output image file path
    """
    validate_file_exists(input_file)
    validate_image_format(input_file)
    validate_output_dir(output_file)

    try:
        img = Image.open(input_file).convert("L")
        img.save(output_file)
        img.close()  # Ensure the image file is closed

    except Exception as e:
        raise RuntimeError(f"Error grayscaling image: {e}")
