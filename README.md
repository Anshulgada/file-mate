# Filemate: Your Command-Line File Conversion and Manipulation Tool

`Filemate` is a versatile command-line tool designed to streamline your file conversion and manipulation tasks. It currently focuses on image and PDF files, offering efficient ways to convert, manipulate, and extract information from them.

## Features

-   **Image Conversion:** Convert images between various formats like JPEG, PNG, WebP, GIF, and TIFF.
-   **PDF Conversion:** Convert images to PDFs, PDFs to images, and merge multiple PDF files.
-   **Image Manipulation:** Resize, rotate, and grayscale images.
-   **File Information:** Get detailed information about files (type, size, dimensions for images, page count for PDFs).

## Installation

1.  **Install `pipx` (if you don't have it):**

    ```bash
    python -m pip install --user pipx
    python -m pipx ensurepath
    ```

    This ensures that `pipx` is installed globally and its executables are present in your system's PATH. You may need to restart your terminal for these changes to take effect.

2.  **Install `file-mate` using `pipx`:**

    ```bash
    pipx install file-mate
    ```

    This command installs `file-mate` into an isolated environment and makes the `file-mate` command accessible from anywhere.

## Usage

The `file-mate` tool provides the following commands:

1.  **`convert`:** For file format conversion.

    *   **`file-mate convert image <input_file> <output_file> [--format <target_format>] [--quality <0-100>]`**: Converts a single image file.
        *   `input_file`: Path to the input image file.
        *   `output_file`: Path to the output image file.
        *   `--format`: (Optional) Target image format (e.g., `png`, `jpg`, `webp`). If omitted, the extension of the output file will be used.
        *   `--quality`: (Optional) Image quality (0-100) for lossy formats like JPEG and WebP. Default is 100.

        Example:
        ```bash
         file-mate convert image input.png output.jpg --quality 90
        ```
    *   **`file-mate convert image-batch <input_dir> <output_dir> [--format <target_format>] [--quality <0-100>] [--recursive]`**: Converts a batch of images in a directory
        *   `input_dir`: Path to the input directory.
        *   `output_dir`: Path to the output directory.
        *   `--format`: (Optional) Target image format (e.g., `png`, `jpg`, `webp`). If omitted, the extension of the output file will be used.
        *   `--quality`: (Optional) Image quality (0-100) for lossy formats like JPEG and WebP. Default is 100.
        *    `--recursive`: (Optional) Process subdirectories recursively.

         Example:
        ```bash
        file-mate convert image-batch input_dir output_dir --format jpg --recursive
        ```

    *   **`file-mate convert image-to-pdf <input_image> <output_pdf>`**: Converts an image to a PDF file.
        *   `input_image`: Path to the input image file.
        *   `output_pdf`: Path to the output PDF file.
        Example:
        ```bash
        file-mate convert image-to-pdf input.png output.pdf
        ```

    *   **`file-mate convert pdf-to-images <input_pdf> <output_dir> [--format <target_format>]`**: Converts a PDF file to a series of images.
        *   `input_pdf`: Path to the input PDF file.
        *   `output_dir`: Path to the directory where the output images will be saved.
        *   `--format`: (Optional) Target image format for the extracted images (default is `png`).
        Example:
        ```bash
        file-mate convert pdf-to-images input.pdf output_dir --format jpg
        ```
    *   **`file-mate convert merge-pdf <pdf1> <pdf2> ... <output_pdf>`**: Merges multiple PDF files into one.
        *   `pdf1`, `pdf2`, ...: Paths to the input PDF files.
        *   `output_pdf`: Path to the output merged PDF file.
        Example:
        ```bash
        file-mate convert merge-pdf file1.pdf file2.pdf output.pdf
        ```

2.  **`manip`**: For image manipulation.

    *   **`file-mate manip resize <input_image> <output_image> [--width <pixels>] [--height <pixels>] [--scale <0-1>]`**: Resizes an image file.
        *   `input_image`: Path to the input image file.
        *   `output_image`: Path to the output image file.
        *   `--width`: (Optional) Target width in pixels.
        *   `--height`: (Optional) Target height in pixels.
        *   `--scale`: (Optional) Scale factor for resizing (0-1).

        Example:
        ```bash
        file-mate manip resize input.png output.png --width 200 --height 100
        file-mate manip resize input.png output.png --scale 0.5
        ```
    *   **`file-mate manip rotate <input_image> <output_image> [--degrees <90/180/270>]`**: Rotates an image file.
        *   `input_image`: Path to the input image file.
        *   `output_image`: Path to the output image file.
        *   `--degrees`: Rotation degree (90, 180 or 270).
          Example:
        ```bash
        file-mate manip rotate input.png output.png --degrees 90
        ```
    *   **`file-mate manip grayscale <input_image> <output_image>`**: Converts an image to grayscale.
        *   `input_image`: Path to the input image file.
        *   `output_image`: Path to the output image file.
         Example:
        ```bash
        file-mate manip grayscale input.png output.png
        ```

3.  **`info`**: For extracting file information.

    *   **`file-mate info <file_path>`**: Displays information about a file.
        *   `file_path`: Path to the file.
        Example:
        ```bash
         file-mate info input.pdf
         file-mate info input.png
        ```

## Configuration

`file-mate` has no external configuration currently.

## Development and Testing

-   **Editable Install:** To avoid re-installing the package again and again during local development, you should run the tool inside your virtual environment. For this you have to activate your environment and then run `pip install -e .` from the root directory. Now you can use the tool with the activated virtual environment. Whenever you want to update the global version then you have to uninstall the current version using `pipx uninstall file-mate` and install again using `pipx install file-mate`.
-   **Running Tests:**
    *   The tests are located in the `file_mate/tests` directory. You can run the tests using `pytest` from the root of your project i.e. where `setup.py` exists.
        ```bash
        pytest -v -s file_mate/tests
        ```

## Dependencies

-   `Pillow`
-   `pypdf`
-   `python-magic-bin`
-   `click`
-   `reportlab`
-   `setuptools`

## License

This project is licensed under the MIT License.